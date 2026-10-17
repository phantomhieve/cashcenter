from __future__ import annotations

import json
from typing import Any, Dict, List
from intelligence.ai_gateway import AIGateway, TaskType
from intelligence.pipeline.cleaner import CleaningReport
from intelligence.pipeline.search import MarketSearchResult


class ArgonPromptSynthesizer:
    """Uses Argon (gemini-4-argon) to engineer a comprehensive, tailored diagnostic prompt."""

    def __init__(self, ai_gateway: AIGateway):
        self.gateway = ai_gateway

    def generate_master_prompt(
        self,
        seller_context: Dict[str, Any],
        cleaning_report: CleaningReport,
        market_search_results: List[MarketSearchResult],
    ) -> str:
        """Assembles rich context and tasks Argon with authoring the comprehensive analysis prompt."""

        # Summarize top products
        top_items = sorted(
            cleaning_report.canonical_items.values(),
            key=lambda x: x["total_revenue"],
            reverse=True,
        )[:8]

        # Summarize market findings
        market_snippets = [
            f"- Query: '{s.query}' | Match: '{s.title}' | Rate: {s.estimated_price or 'N/A'} | Market: {s.market_location} | Excerpt: {s.snippet[:140]}..."
            for s in market_search_results[:6]
        ]

        # Extract rich context with Darbhanga Bara Bazar defaults
        shop_name = seller_context.get("shop_name") or "Cash Center"
        location = seller_context.get("location") or "Bara Bazar, Darbhanga, Bihar"
        turnover = seller_context.get("turnover") or "~₹12 Crore INR / year (approx ₹1.0 Cr / month historical baseline)"
        problem_statement = seller_context.get("problem_statement") or (
            "Annual sales have been declining over the last 2-3 years from ~₹12 CR. "
            "We urgently need actionable intelligence extracted from our shop's ledger to identify root causes "
            "(Surat mill-direct WhatsApp bypass, freight drag, transit delays, margin compression) "
            "and execute a concrete sales recovery plan for North Bihar & Mithila retail."
        )

        meta_prompt = (
            f"You are Argon (gemini-4-argon), the elite wholesale textile strategist and enterprise AI prompt architect.\n"
            f"Your objective: Author an EXHAUSTIVE, DEEPLY RIGOROUS master diagnostic and extraction prompt.\n"
            f"This prompt will be executed downstream by commercial AI models to parse the shop's operational LEDGER data, "
            f"extract hidden commercial metrics, diagnose the sales decline from ~₹12 CR, and deliver a turnaround strategy.\n\n"
            f"=== ENTERPRISE SELLER & REPOSITORY PROFILE ===\n"
            f"Shop Name: {shop_name}\n"
            f"Location: {location} (Primary wholesale textile hub serving Darbhanga, Madhubani, Samastipur, Sitamarhi & Nepal border)\n"
            f"Core Business: Wholesale and semi-wholesale cloth & fabric distribution.\n"
            f"Historical Scale: {turnover}\n"
            f"Current Strategic Challenge: {problem_statement}\n"
            f"Primary Data System: Wholesale Ledger (`LedgerData`) tracking transport bilty/L/R consignments from Surat, Ahmedabad, etc.\n"
            f"Total Ledger Records Ingested: {cleaning_report.total_records} consignments | Volume: ₹{cleaning_report.total_revenue:,.2f} | {cleaning_report.total_quantity} meters/bales\n"
            f"Data Cleanliness: {cleaning_report.anomalous_records} anomalous/noisy records cleaned (textile acronyms resolved, zero-value prices flagged)\n"
            f"Top Canonical Fabrics in Ledger:\n"
            f"{json.dumps(top_items, indent=2)}\n\n"
            f"=== LIVE INTERNET MARKET RESEARCH GROUNDING (Surat to Bihar Parity) ===\n"
            f"{chr(10).join(market_snippets)}\n\n"
            f"=== MANDATORY STRUCTURE OF THE MASTER EXTRACTION PROMPT YOU MUST AUTHOR ===\n"
            f"Compose an exhaustive, master prompt directing the diagnostic engine to analyze the ledger data across 7 comprehensive modules:\n\n"
            f"1. 📋 Ledger Data Ingestion & Normalization Specification:\n"
            f"   - Detail exact rules to parse transport bilty fields: L/R No, L/R Date, Bale No, Mill/Supplier, Origin City (Surat, Ahmedabad, Bhiwandi), Fabric Variety (standardizing shorthand like 'ctn 60s', 'ryn 14kg prnt', 'cambrc'), Meters/Pieces, Invoice Bill Amount, Freight Charges, and Landed Unit Cost `(bill_amount + freight) / meters`.\n\n"
            f"2. 🎯 Root-Cause Turnaround Diagnosis (~₹12 CR Turnover Erosion):\n"
            f"   - Direct the AI to systematically diagnose why sales have declined: Is it Surat mill traveling agents bypassing Bara Bazar wholesalers? Credit extension trap (60-90 days unpaid from mofussil retailers)? Outdated fabric assortment? Or landed cost disadvantage against direct mill shipments?\n\n"
            f"3. 🚚 Logistics, Freight Drag & Transit Delay Impact:\n"
            f"   - Direct the AI to calculate Freight Drag % `(freight / bill_amount)` per supplier and transport carrier.\n"
            f"   - Analyze transit duration `(delivery_date - l_r_date)` and cross-reference with the Mithila Festive Calendar (Lagan wedding season, Durga Puja, Chhath Puja, Eid). Identify orders that arrived late and missed peak retail selling windows.\n\n"
            f"4. 💎 Fabric Catalog Rationalization (Fast-Turnover vs Dead Capital):\n"
            f"   - Classify fabric purchases into 4 quadrants: Running Stars (Cotton 60s Cambric, Rayon 14kg Lurex), Steady Volume Cash Cows, High-Risk Bets, and Dead Capital (slow-moving polyester/shirting locking working capital).\n\n"
            f"5. 🌐 Mill Gate Parity & Arbitrage vs Live Internet Benchmarks:\n"
            f"   - Benchmark shop's landed prices against live Surat mill rates. Identify fabrics where Cash Center is purchasing at inflated rates or where freight is eating entire wholesale margins.\n\n"
            f"6. 👥 Supplier Dependency & Counterparty Risk Matrix:\n"
            f"   - Analyze supplier concentration: Are 2-3 mills dominating procurement? Are those mills reliable on delivery timelines, or are they selling identical designs to competing shops in Bara Bazar?\n\n"
            f"7. 📦 30-60-90 Day Sales Recovery Action Plan & B2B Distribution Directives:\n"
            f"   - Formulate concrete, non-generic operational directives for the shopkeeper: Open-to-buy allocation for next month, dead stock liquidation discount rules, 2% cash discount on 7-day payment to recover cash, and proactive WhatsApp B2B catalog broadcast playbook for 200+ North Bihar retailers.\n\n"
            f"Write the master prompt in high-precision Markdown, addressing the downstream diagnostic engine with commercial authority, wholesale domain mastery, and acute regional understanding."
        )

        response = self.gateway.generate_text(
            prompt=meta_prompt,
            system_instruction="You are an expert prompt architect and wholesale textile strategist specializing in Indian B2B commerce.",
            task_type=TaskType.REASONING,
            model="gemini-4-argon",
            temperature=0.3,
        )

        return response.text.strip()
