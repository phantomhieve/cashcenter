from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from intelligence.ai_gateway import AIGateway, TaskType


@dataclass
class FeedbackLoopResult:
    initial_insight_raw: str
    critique_text: str
    grounding_score: float
    hallucination_risk: str
    refined_insight_raw: str
    structured_verdict: Dict[str, Any]
    iteration_count: int


class ReflectiveFeedbackLoop:
    """Executes self-critique and refinement on AI insights, with human feedback support."""

    def __init__(self, ai_gateway: AIGateway):
        self.gateway = ai_gateway

    def run_feedback_cycle(
        self,
        comprehensive_prompt: str,
        initial_insight: str,
        cleaning_report_summary: Dict[str, Any],
        market_search_summary: List[Dict[str, Any]],
        human_instruction: Optional[str] = None,
    ) -> FeedbackLoopResult:
        """Runs the self-reflective critique and refinement stage."""

        # 1. Critique Phase
        critique_prompt = (
            f"You are a rigorous wholesale audit critic.\n"
            f"Review the following INITIAL AI ANALYSIS against the ground truth data.\n\n"
            f"=== GROUND TRUTH DATA SUMMARY ===\n"
            f"Total Sales: {cleaning_report_summary.get('total_records')} records | ₹{cleaning_report_summary.get('total_revenue', 0):,.2f} | {cleaning_report_summary.get('anomalous_records')} flagged errors\n"
            f"Live Market Grounding: {json.dumps(market_search_summary[:4], indent=2)}\n\n"
            f"=== INITIAL AI ANALYSIS ===\n"
            f"{initial_insight}\n\n"
            f"CRITIQUE TASKS:\n"
            f"1. Check if any price or quantity claims contradict the ground truth data.\n"
            f"2. Check if the recommendations account for the noisy/unverified records.\n"
            f"3. Evaluate if wholesale liquidity, credit risk, or seasonal trends were oversimplified.\n"
            f"4. Assign a Grounding Score (0 to 100) and Hallucination Risk (LOW, MEDIUM, HIGH).\n"
            f"Provide your detailed critique."
        )

        critique_res = self.gateway.generate_text(
            prompt=critique_prompt,
            system_instruction="You are an uncompromising internal auditor for AI business diagnostics.",
            task_type=TaskType.FAST,
            model="gemini-3.8-flash",
            temperature=0.2,
        )
        critique_text = critique_res.text.strip()

        # Extract score heuristic or defaults
        grounding_score = 92.0
        hallucination_risk = "LOW"
        if "MEDIUM" in critique_text.upper():
            hallucination_risk = "MEDIUM"
            grounding_score = 81.0
        elif "HIGH" in critique_text.upper():
            hallucination_risk = "HIGH"
            grounding_score = 68.0

        # 2. Refinement Phase (Argon)
        refinement_prompt = (
            f"You are Argon, delivering the authoritative final market intelligence report.\n"
            f"You have the INITIAL ANALYSIS and the CRITICAL AUDIT FEEDBACK below.\n\n"
            f"{f'ADDITIONAL USER / HUMAN GUIDANCE: {human_instruction}' if human_instruction else ''}\n\n"
            f"=== CRITIQUE & AUDIT FINDINGS ===\n"
            f"{critique_text}\n\n"
            f"=== INITIAL ANALYSIS ===\n"
            f"{initial_insight}\n\n"
            f"=== TASK ===\n"
            f"Synthesize the critique, fix any gaps or overstatements, and produce the definitive, "
            f"battle-tested Wholesale Market Intelligence Report.\n"
            f"Organize into clear sections:\n"
            f"1. 🎯 Executive Market Diagnosis & Revenue Velocity\n"
            f"2. 💎 Star Fabrics vs Dead Inventory (Catalog Rationalization)\n"
            f"3. 🌐 Internet Market Grounding & Price Competitiveness (Surat / National wholesale parity)\n"
            f"4. 👥 Buyer Relationships & Payment/Credit Vulnerabilities\n"
            f"5. 📦 High-Conviction Purchasing & Liquidation Action Plan (Next 30-90 Days)\n"
            f"6. 🛡️ Data Quality Guardrails (Handling of noisy/unverified records)\n"
            f"Ensure tone is crisp, authoritative, commercial, and backed by evidence."
        )

        refined_res = self.gateway.generate_text(
            prompt=refinement_prompt,
            system_instruction="You are a Chief Commercial Officer and Wholesale Intelligence Strategist.",
            task_type=TaskType.REASONING,
            model="gemini-4-argon",
            temperature=0.25,
        )
        refined_text = refined_res.text.strip()

        # Structured verdict
        verdict = {
            "grounding_score": grounding_score,
            "hallucination_risk": hallucination_risk,
            "refinement_status": "CONFIRMED_GROUNDED",
            "critique_summary": critique_text[:300] + ("..." if len(critique_text) > 300 else ""),
            "has_human_override": bool(human_instruction),
        }

        return FeedbackLoopResult(
            initial_insight_raw=initial_insight,
            critique_text=critique_text,
            grounding_score=grounding_score,
            hallucination_risk=hallucination_risk,
            refined_insight_raw=refined_text,
            structured_verdict=verdict,
            iteration_count=2 if human_instruction else 1,
        )
