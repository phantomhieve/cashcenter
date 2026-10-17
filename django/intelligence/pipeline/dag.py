from __future__ import annotations

import concurrent.futures
import datetime
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
from intelligence.ai_gateway import AIGateway, TaskType, gateway
from intelligence.pipeline.cleaner import CleaningReport, SoldDataCleaner
from intelligence.pipeline.feedback import FeedbackLoopResult, ReflectiveFeedbackLoop
from intelligence.pipeline.prompt_gen import ArgonPromptSynthesizer
from intelligence.pipeline.search import MarketSearchEngine, MarketSearchResult

logger = logging.getLogger(__name__)


@dataclass
class DAGNodeExecution:
    node_id: str
    name: str
    stage: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    output_summary: str = ""
    error: Optional[str] = None


@dataclass
class DAGRunResult:
    run_id: str
    seller_name: str
    total_sales_count: int
    total_revenue: float
    total_parcels: float
    anomalies_flagged: int
    cleaning_report: CleaningReport
    market_search_results: List[MarketSearchResult]
    generated_prompt: str
    initial_insight: str
    critique_text: str
    grounding_score: float
    hallucination_risk: str
    final_refined_insight: str
    node_executions: List[DAGNodeExecution]
    execution_time_seconds: float
    timestamp: str


class MarketIntelligenceDAG:
    """Multi-stage Directed Acyclic Graph (DAG) for Wholesale Market Intelligence."""

    def __init__(self, ai_gateway: Optional[AIGateway] = None):
        self.gateway = ai_gateway or gateway
        self.cleaner = SoldDataCleaner()
        self.search_engine = MarketSearchEngine()
        self.prompt_synthesizer = ArgonPromptSynthesizer(self.gateway)
        self.feedback_loop = ReflectiveFeedbackLoop(self.gateway)

    def execute(
        self,
        raw_records: Optional[List[Dict[str, Any]]] = None,
        seller_context: Optional[Dict[str, Any]] = None,
        human_feedback: Optional[str] = None,
    ) -> DAGRunResult:
        start_time = time.time()
        run_id = f"dag-{int(start_time)}"
        seller_ctx = seller_context or {"shop_name": "CashCenter Wholesale Merchant", "vertical": "Textiles & Fabrics"}
        node_logs: List[DAGNodeExecution] = []

        def log_node(node_id: str, name: str, stage: str):
            node = DAGNodeExecution(
                node_id=node_id,
                name=name,
                stage=stage,
                status="RUNNING",
                started_at=datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3],
            )
            node_logs.append(node)
            return node

        def finish_node(node: DAGNodeExecution, summary: str, is_error: bool = False):
            node.status = "FAILED" if is_error else "COMPLETED"
            node.completed_at = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            node.output_summary = summary

        # -------------------------------------------------------------
        # STAGE 1: Parallel Diagnostic Lenses (Fan-Out)
        # -------------------------------------------------------------
        node_1a = log_node("1A", "Data Hygiene & Normalization", "Stage 1: Fan-out")
        node_1b = log_node("1B", "Seller Identity & Web Market Discovery", "Stage 1: Fan-out")
        node_1c = log_node("1C", "Demand Velocity & Pareto Concentration", "Stage 1: Fan-out")

        cleaning_report: CleaningReport
        market_results: List[MarketSearchResult] = []
        velocity_metrics: Dict[str, Any] = {}

        # 1A. Clean Data
        t0 = time.time()
        try:
            records = raw_records if raw_records is not None else self.cleaner.ingest_from_db()
            cleaning_report = self.cleaner.process(records)
            node_1a.duration_ms = round((time.time() - t0) * 1000, 2)
            finish_node(
                node_1a,
                f"Processed {cleaning_report.total_records} records. Corrected {cleaning_report.anomalous_records} anomalous/noisy entries.",
            )
        except Exception as e:
            node_1a.duration_ms = round((time.time() - t0) * 1000, 2)
            finish_node(node_1a, f"Cleaning failed: {e}", is_error=True)
            raise e

        # 1B & 1C. Web Market Search & Velocity in parallel
        top_item_names = list(cleaning_report.canonical_items.keys())[:3]
        if not top_item_names:
            top_item_names = ["Cotton 60s Cambric", "Rayon 14kg Print"]

        def run_web_search():
            t = time.time()
            all_res = []
            for item in top_item_names:
                res = self.search_engine.search_product(item)
                all_res.extend(res)
            return all_res, round((time.time() - t) * 1000, 2)

        def run_velocity_analysis():
            t = time.time()
            # Calculate concentration & average ticket
            tot_rev = cleaning_report.total_revenue
            top_rev = sum(it["total_revenue"] for it in list(cleaning_report.canonical_items.values())[:3])
            concentration = round((top_rev / tot_rev * 100), 1) if tot_rev > 0 else 0.0
            avg_ticket = round(tot_rev / max(cleaning_report.total_records, 1), 2)
            return {
                "top_3_concentration_pct": concentration,
                "average_ticket_inr": avg_ticket,
                "total_buyers": len(cleaning_report.buyer_summary),
            }, round((time.time() - t) * 1000, 2)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            fut_search = executor.submit(run_web_search)
            fut_velocity = executor.submit(run_velocity_analysis)

            market_results, dur_search = fut_search.result()
            velocity_metrics, dur_vel = fut_velocity.result()

        node_1b.duration_ms = dur_search
        finish_node(
            node_1b,
            f"Retrieved {len(market_results)} live wholesale web listings & benchmarks across Surat/India hubs.",
        )

        node_1c.duration_ms = dur_vel
        finish_node(
            node_1c,
            f"Top 3 items drive {velocity_metrics['top_3_concentration_pct']}% of revenue. Avg order: ₹{velocity_metrics['average_ticket_inr']:,.2f}.",
        )

        # -------------------------------------------------------------
        # STAGE 2: Tactical Prompt Synthesis (Fan-In via Argon)
        # -------------------------------------------------------------
        node_2 = log_node("2", "Argon Master Prompt Synthesis", "Stage 2: Fan-in")
        t2 = time.time()
        try:
            master_prompt = self.prompt_synthesizer.generate_master_prompt(
                seller_context=seller_ctx,
                cleaning_report=cleaning_report,
                market_search_results=market_results,
            )
            node_2.duration_ms = round((time.time() - t2) * 1000, 2)
            finish_node(node_2, f"Argon generated comprehensive {len(master_prompt)} char multi-angle diagnostic prompt.")
        except Exception as e:
            node_2.duration_ms = round((time.time() - t2) * 1000, 2)
            finish_node(node_2, f"Prompt synthesis failed: {e}", is_error=True)
            raise e

        # -------------------------------------------------------------
        # STAGE 3: Deep Reasoning & Reflective Feedback Loop
        # -------------------------------------------------------------
        node_3a = log_node("3A", "Initial Argon Deep Reasoning", "Stage 3: Deep Reasoning")
        t3a = time.time()
        initial_insight_res = self.gateway.generate_text(
            prompt=master_prompt,
            system_instruction="You are Argon, an elite wholesale commercial diagnostic engine.",
            task_type=TaskType.REASONING,
            model="gemini-4-argon",
            temperature=0.25,
        )
        initial_insight = initial_insight_res.text.strip()
        node_3a.duration_ms = round((time.time() - t3a) * 1000, 2)
        finish_node(node_3a, f"Produced initial strategic diagnostic ({len(initial_insight)} chars).")

        node_3b = log_node("3B", "Reflective Audit & Critique Loop", "Stage 3: Feedback Loop")
        t3b = time.time()
        feedback_res = self.feedback_loop.run_feedback_cycle(
            comprehensive_prompt=master_prompt,
            initial_insight=initial_insight,
            cleaning_report_summary={
                "total_records": cleaning_report.total_records,
                "total_revenue": cleaning_report.total_revenue,
                "anomalous_records": cleaning_report.anomalous_records,
            },
            market_search_summary=[asdict(m) for m in market_results[:4]],
            human_instruction=human_feedback,
        )
        node_3b.duration_ms = round((time.time() - t3b) * 1000, 2)
        finish_node(
            node_3b,
            f"Critique audit completed (Grounding: {feedback_res.grounding_score}/100, Risk: {feedback_res.hallucination_risk}). Final report refined.",
        )

        # -------------------------------------------------------------
        # STAGE 4: Terminal Grounding & Delivery
        # -------------------------------------------------------------
        node_4 = log_node("4", "Terminal Structured Delivery", "Stage 4: Grounding")
        t4 = time.time()
        finish_node(node_4, "Assembled executive dashboard KPIs, star items, and action roadmap.")
        node_4.duration_ms = round((time.time() - t4) * 1000, 2)

        total_duration = round(time.time() - start_time, 2)

        return DAGRunResult(
            run_id=run_id,
            seller_name=seller_ctx.get("shop_name", "CashCenter Wholesale Merchant"),
            total_sales_count=cleaning_report.total_records,
            total_revenue=cleaning_report.total_revenue,
            total_parcels=cleaning_report.total_quantity,
            anomalies_flagged=cleaning_report.anomalous_records,
            cleaning_report=cleaning_report,
            market_search_results=market_results,
            generated_prompt=master_prompt,
            initial_insight=initial_insight,
            critique_text=feedback_res.critique_text,
            grounding_score=feedback_res.grounding_score,
            hallucination_risk=feedback_res.hallucination_risk,
            final_refined_insight=feedback_res.refined_insight_raw,
            node_executions=node_logs,
            execution_time_seconds=total_duration,
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
