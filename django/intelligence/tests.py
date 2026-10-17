import json
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from core.models import FinancialYear, UserProfile
from ledger.models import LedgerData
from orderlist.models import Order
from .ai_gateway import TaskType, gateway
from .ai_gateway.client import normalize_model_name
from .insights import compute_ledger_stats, parse_report
from .models import IntelligenceFeedback, IntelligenceRun
from .pipeline.cleaner import SoldDataCleaner, clean_item_name
from .pipeline.dag import MarketIntelligenceDAG
from .pipeline.feedback import ReflectiveFeedbackLoop
from .pipeline.prompt_gen import ArgonPromptSynthesizer
from .pipeline.search import MarketSearchEngine


class DataCleanerTests(TestCase):
    def test_clean_item_name_abbreviations(self):
        cleaned, cat = clean_item_name("ctn cambrc 60s prnt")
        self.assertIn("Cotton", cleaned)
        self.assertIn("Cambric", cleaned)
        self.assertIn("Print", cleaned)
        self.assertEqual(cat, "Cotton & Natural Blends")

        cleaned_ryn, cat_ryn = clean_item_name("ryn slb 14kg")
        self.assertIn("Rayon", cleaned_ryn)
        self.assertIn("Slub", cleaned_ryn)
        self.assertEqual(cat_ryn, "Rayon & Viscose")

    def test_cleaner_anomalies_detection(self):
        cleaner = SoldDataCleaner()
        raw = [
            {"id": "1", "item": "ctn 60s", "buyer": "Client A", "quantity": 10, "price": 4500},
            {"id": "2", "item": "xx", "buyer": "Client B", "quantity": 0, "price": -50}, # Anomalous
        ]
        report = cleaner.process(raw)
        self.assertEqual(report.total_records, 2)
        self.assertEqual(report.anomalous_records, 1)
        self.assertGreater(report.total_revenue, 0)
        self.assertIn("Cotton 60s", report.canonical_items)


class ModelAliasNormalizationTests(TestCase):
    def test_argon_normalization(self):
        self.assertEqual(normalize_model_name("argon"), "gemini-4-argon")
        self.assertEqual(normalize_model_name("gemini-argon"), "gemini-4-argon")
        self.assertEqual(normalize_model_name("ARGON"), "gemini-4-argon")
        self.assertEqual(normalize_model_name("flash"), "gemini-3.8-flash")
        self.assertEqual(normalize_model_name("gemini-3.8-flash"), "gemini-3.8-flash")


class MarketSearchEngineTests(TestCase):
    def test_curated_benchmark_fallback(self):
        engine = MarketSearchEngine()
        results = engine.search_product("Rayon 14kg Print")
        self.assertGreaterEqual(len(results), 1)
        first = results[0]
        self.assertTrue(len(first.snippet) > 0)
        self.assertIsNotNone(first.market_location)


class DAGWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testadmin", password="password123")
        if hasattr(self.user, 'profile'):
            self.user.profile.financial_year_password = "test_admin_pwd"
            self.user.profile.save()
        else:
            UserProfile.objects.create(user=self.user, financial_year_password="test_admin_pwd")

    def test_dag_execution(self):
        dag = MarketIntelligenceDAG()
        sample_sales = [
            {"id": "S1", "item": "Cotton 60s Cambric", "buyer": "Surat Mills", "quantity": 20, "price": 5000},
            {"id": "S2", "item": "Rayon 14kg Printed", "buyer": "Ahmedabad Traders", "quantity": 15, "price": 3200},
            {"id": "S3", "item": "Georgette 60g Foil", "buyer": "Delhi Retail", "quantity": 5, "price": 4100},
        ]
        result = dag.execute(raw_records=sample_sales, seller_context={"shop_name": "Test Fabrics"})

        self.assertEqual(result.total_sales_count, 3)
        self.assertGreater(result.total_revenue, 0)
        self.assertGreater(len(result.node_executions), 3)
        self.assertTrue(len(result.generated_prompt) > 0)
        self.assertTrue(len(result.final_refined_insight) > 0)
        self.assertGreaterEqual(result.grounding_score, 50.0)


class IntelligenceViewsSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="shopowner", password="password123", is_staff=True)
        # Profile created by signal or manually
        if not hasattr(self.user, 'profile'):
            UserProfile.objects.create(user=self.user, financial_year_password="admin_secret_pass")
        else:
            self.user.profile.financial_year_password = "admin_secret_pass"
            self.user.profile.save()

    def test_dashboard_redirects_unauthenticated(self):
        resp = self.client.get(reverse('intelligence:dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/user/login/', resp.url)

    def test_dashboard_requires_admin_password(self):
        self.client.login(username="shopowner", password="password123")
        resp = self.client.get(reverse('intelligence:dashboard'))
        # Should redirect to auth gate
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('intelligence:auth_gate'), resp.url)

    def test_auth_gate_wrong_password(self):
        self.client.login(username="shopowner", password="password123")
        resp = self.client.post(reverse('intelligence:auth_gate'), {'password': 'wrong_password'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Incorrect Admin Password")

    def test_auth_gate_success_and_unlock(self):
        self.client.login(username="shopowner", password="password123")
        resp = self.client.post(reverse('intelligence:auth_gate'), {'password': 'admin_secret_pass'})
        # Should redirect to dashboard on successful password check
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('intelligence:dashboard'), resp.url)

        # Subsequent GET to dashboard should succeed directly
        dash_resp = self.client.get(reverse('intelligence:dashboard'))
        self.assertEqual(dash_resp.status_code, 200)
        self.assertContains(dash_resp, "Turnaround Intelligence")

    def test_lock_clears_session(self):
        self.client.login(username="shopowner", password="password123")
        self.client.post(reverse('intelligence:auth_gate'), {'password': 'admin_secret_pass'})
        # Now lock
        lock_resp = self.client.get(reverse('intelligence:lock_dashboard'))
        self.assertEqual(lock_resp.status_code, 302)

        # Accessing dashboard should require password again
        dash_resp = self.client.get(reverse('intelligence:dashboard'))
        self.assertEqual(dash_resp.status_code, 302)
        self.assertIn(reverse('intelligence:auth_gate'), dash_resp.url)

    def test_monthly_quota_guardrail(self):
        self.client.login(username="shopowner", password="password123")
        self.client.post(reverse('intelligence:auth_gate'), {'password': 'admin_secret_pass'})

        # First run succeeds
        post_resp1 = self.client.post(reverse('intelligence:run_analysis'), {
            'source_type': 'raw',
            'raw_payload': 'Cotton 60s Cambric - 10 parcels - Rs 45000 - Radha Krishna Textiles',
        })
        self.assertEqual(post_resp1.status_code, 302)
        self.assertEqual(IntelligenceRun.objects.filter(user=self.user).count(), 1)

        # Second run without force_override is blocked by monthly quota
        post_resp2 = self.client.post(reverse('intelligence:run_analysis'), {
            'source_type': 'raw',
            'raw_payload': 'Cotton 60s Cambric - 10 parcels - Rs 45000 - Radha Krishna Textiles',
        }, follow=True)
        self.assertEqual(post_resp2.status_code, 200)
        self.assertContains(post_resp2, "once every 30 days")
        self.assertEqual(IntelligenceRun.objects.filter(user=self.user).count(), 1)

        # Third run WITH force_override succeeds
        post_resp3 = self.client.post(reverse('intelligence:run_analysis'), {
            'source_type': 'raw',
            'raw_payload': 'Cotton 60s Cambric - 10 parcels - Rs 45000 - Radha Krishna Textiles',
            'force_override': 'true',
        })
        self.assertEqual(post_resp3.status_code, 302)
        self.assertEqual(IntelligenceRun.objects.filter(user=self.user).count(), 2)


class LedgerStatsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="pw")
        self.fy = FinancialYear.objects.create(start_date=date(2026, 4, 1), end_date=date(2027, 3, 31))

    def _row(self, lr, supplier, bill, freight, lr_date, delivery=None, status=True, item="Cambric"):
        return LedgerData.objects.create(
            user=self.user, financial_year=self.fy, l_r_no=lr, supplier=supplier, item=item,
            bill_ammount=bill, frieght=freight, l_r_date=lr_date, delivery=delivery,
            status=status, no_of_bale=2, pcs_mtr=100,
        )

    def test_empty_ledger_is_safe(self):
        stats = compute_ledger_stats(self.user, self.fy, today=date(2026, 10, 17))
        self.assertFalse(stats["has_data"])
        self.assertEqual(stats["kpis"], [])
        self.assertEqual(stats["flags"], [])

    def test_totals_freight_and_transit_are_real(self):
        self._row("A1", "Mill One", 100000, 4000, date(2026, 8, 1), date(2026, 8, 15))
        self._row("A2", "Mill One", 100000, 6000, date(2026, 9, 1), date(2026, 9, 20))
        self._row("A3", "Mill Two", 50000, 1000, date(2026, 9, 5), None, status=False)
        stats = compute_ledger_stats(self.user, self.fy, today=date(2026, 10, 17))
        kpis = {k["key"]: k for k in stats["kpis"]}

        self.assertEqual(kpis["bought"]["value"], "₹2.5 L")
        self.assertEqual(kpis["freight"]["value"], "₹11,000")
        self.assertIn("4.4%", kpis["freight"]["sub"])
        self.assertEqual(kpis["transit"]["value"], "1")
        self.assertEqual(kpis["suppliers"]["value"], "2")
        # Average of 14 and 19 days.
        self.assertEqual(kpis["delivery"]["value"], "16.5 days")
        # Mill One holds 80% of spend and A3 has been on the road 42 days.
        titles = " ".join(f["title"] for f in stats["flags"])
        self.assertIn("on the road", titles)
        self.assertIn("80%", titles)

    def test_partial_current_month_never_drives_the_trend(self):
        self._row("B1", "Mill One", 100000, 0, date(2026, 8, 10), date(2026, 8, 20))
        self._row("B2", "Mill One", 120000, 0, date(2026, 9, 10), date(2026, 9, 20))
        self._row("B3", "Mill One", 1000, 0, date(2026, 10, 2), date(2026, 10, 9))  # tiny, month in progress
        stats = compute_ledger_stats(self.user, self.fy, today=date(2026, 10, 17))
        bought = stats["kpis"][0]
        self.assertEqual(bought["trend"], "up")
        self.assertIn("+20% in Sep vs Aug", bought["sub"])

    def test_month_axis_is_continuous(self):
        self._row("C1", "Mill One", 1000, 0, date(2026, 5, 10), date(2026, 5, 20))
        self._row("C2", "Mill One", 1000, 0, date(2026, 8, 10), date(2026, 8, 20))
        stats = compute_ledger_stats(self.user, self.fy, today=date(2026, 10, 17))
        self.assertEqual(stats["chart"]["months"], ["May 26", "Jun 26", "Jul 26", "Aug 26"])
        self.assertEqual(stats["chart"]["month_values"], [1000.0, 0.0, 0.0, 1000.0])


SAMPLE_REPORT = """# 🏛️ TEST REPORT
**Client:** Shop

## 1. 🎯 Diagnosis

Sales are slipping because cash is stuck in slow stock. More detail follows here.

### The "60-Day Cash Cycle" myth
* **Not a plan phase:** this must not become a plan column.

## 2. 💎 Fabrics

| A | B |
|---|---|
| 1 | 2 |

### Quadrant matrix

## 3. 📦 Action Plan

### 📅 DAYS 1–30: Clear old stock
* **Liquidate poly shirting:** Offer a cash discount this week. Second sentence.
* Freeze new orders for slow lines

### 📅 DAYS 31–60: Rebalance
* **Shift budget:** Move money to fast fabrics.
"""


class ReportParsingTests(TestCase):
    def test_empty_report(self):
        parsed = parse_report("")
        self.assertFalse(parsed["ok"])
        self.assertEqual(parsed["sections"], [])

    def test_sections_headlines_and_emoji(self):
        parsed = parse_report(SAMPLE_REPORT)
        self.assertTrue(parsed["ok"])
        self.assertEqual([s["title"] for s in parsed["sections"]], ["Diagnosis", "Fabrics", "Action Plan"])
        self.assertEqual(parsed["sections"][0]["emoji"], "🎯")
        self.assertEqual(parsed["sections"][0]["headline"], "Sales are slipping because cash is stuck in slow stock.")
        # A table-only section still gets a readable gist (falls back to its sub-heading).
        self.assertEqual(parsed["sections"][1]["headline"], "Quadrant matrix")

    def test_plan_only_uses_real_day_phases(self):
        parsed = parse_report(SAMPLE_REPORT)
        self.assertEqual([p["label"] for p in parsed["plan"]], ["DAYS 1–30", "DAYS 31–60"])
        first = parsed["first_actions"]
        self.assertEqual(first[0]["lead"], "Liquidate poly shirting")
        self.assertEqual(first[0]["detail"], "Offer a cash discount this week.")
        self.assertEqual(first[1]["lead"], "Freeze new orders for slow lines")


class DashboardUxTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="shopowner", password="password123", is_staff=True)
        if not hasattr(self.user, "profile"):
            UserProfile.objects.create(user=self.user, financial_year_password="pw_admin")
        else:
            self.user.profile.financial_year_password = "pw_admin"
            self.user.profile.save()
        today = timezone.localdate()
        self.fy = FinancialYear.objects.create(
            start_date=today - timedelta(days=100), end_date=today + timedelta(days=200)
        )
        LedgerData.objects.create(
            user=self.user, financial_year=self.fy, l_r_no="LR1", supplier="Mill One", item="Cambric",
            bill_ammount=100000, frieght=3000, l_r_date=today - timedelta(days=20),
            delivery=today - timedelta(days=5), status=True, no_of_bale=2, pcs_mtr=500,
        )
        self.client.login(username="shopowner", password="password123")
        self.client.post(reverse("intelligence:auth_gate"), {"password": "pw_admin"})

    def _make_run(self, days_old):
        run = IntelligenceRun.objects.create(
            user=self.user, financial_year=self.fy, seller_name="Cash Center", total_records=1,
            final_refined_insight=SAMPLE_REPORT, generated_prompt="internal prompt", grounding_score=85,
        )
        IntelligenceRun.objects.filter(pk=run.pk).update(created_at=timezone.now() - timedelta(days=days_old))
        return run

    def test_first_visit_offers_generate_not_pipeline_controls(self):
        resp = self.client.get(reverse("intelligence:dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Generate my insights")
        self.assertContains(resp, "Goods bought")  # real ledger KPI shows even before the first AI run
        self.assertNotContains(resp, 'class="ix-btn ix-btn-muted"')

    def test_recent_run_mutes_refresh_and_shows_days_left(self):
        self._make_run(days_old=5)
        resp = self.client.get(reverse("intelligence:dashboard"))
        self.assertContains(resp, 'class="ix-btn ix-btn-muted"')
        self.assertContains(resp, "Available in 25 days")
        self.assertNotContains(resp, 'id="refreshForm"')  # no way to submit while muted in the UI
        self.assertContains(resp, "Your 90-day plan")
        self.assertContains(resp, "Liquidate poly shirting")

    def test_old_run_enables_refresh(self):
        self._make_run(days_old=31)
        resp = self.client.get(reverse("intelligence:dashboard"))
        self.assertNotContains(resp, 'class="ix-btn ix-btn-muted"')
        self.assertContains(resp, "Refresh insights")
        self.assertContains(resp, 'id="refreshForm"')

    def test_no_technical_jargon_on_dashboard(self):
        self._make_run(days_old=5)
        html = self.client.get(reverse("intelligence:dashboard")).content.decode()
        for banned in ("DAG", "Argon", "gemini-", "Directed Acyclic", "internal prompt"):
            self.assertNotIn(banned, html)

    def test_server_still_blocks_refresh_inside_30_days(self):
        self._make_run(days_old=5)
        resp = self.client.post(reverse("intelligence:run_analysis"), {"source_type": "db"}, follow=True)
        self.assertContains(resp, "once every 30 days")
        self.assertEqual(IntelligenceRun.objects.filter(user=self.user).count(), 1)


class CronCommandTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cronuser", password="password123")
        self.user.profile.financial_year_password = "admin"
        self.user.profile.save()
        self.fy = FinancialYear.objects.create(start_date="2025-04-01", end_date="2026-03-31")
        LedgerData.objects.create(
            user=self.user, l_r_no="CRON-01", financial_year=self.fy,
            bill_ammount=50000, frieght=1200, supplier="Surat Textiles",
        )

    def test_cron_dry_run_eligible_when_no_prior_runs(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        call_command("run_intelligence_cron", "--dry-run", "--user", "cronuser", stdout=out)
        output = out.getvalue()
        self.assertIn("Eligible for refresh", output)
        self.assertIn("Executed: 1", output)

    def test_cron_skips_when_run_is_recent(self):
        from io import StringIO
        from django.core.management import call_command
        run = IntelligenceRun.objects.create(
            user=self.user, financial_year=self.fy, seller_name="Cash Center", total_records=1,
            final_refined_insight="test", generated_prompt="test", grounding_score=80,
        )
        IntelligenceRun.objects.filter(pk=run.pk).update(created_at=timezone.now() - timedelta(days=5))

        out = StringIO()
        call_command("run_intelligence_cron", "--dry-run", "--user", "cronuser", stdout=out)
        output = out.getvalue()
        self.assertIn("Skipped", output)
        self.assertIn("remaining until next refresh", output)
        self.assertIn("Executed: 0", output)

    def test_cron_force_flag_bypasses_30_day_window(self):
        from io import StringIO
        from django.core.management import call_command
        run = IntelligenceRun.objects.create(
            user=self.user, financial_year=self.fy, seller_name="Cash Center", total_records=1,
            final_refined_insight="test", generated_prompt="test", grounding_score=80,
        )
        IntelligenceRun.objects.filter(pk=run.pk).update(created_at=timezone.now() - timedelta(days=5))

        out = StringIO()
        call_command("run_intelligence_cron", "--dry-run", "--force", "--user", "cronuser", stdout=out)
        output = out.getvalue()
        self.assertIn("Eligible for refresh (Forced run", output)
        self.assertIn("Executed: 1", output)


class BilingualTranslationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bilingual_user", password="password123")
        self.user.profile.financial_year_password = "admin"
        self.user.profile.save()
        self.fy = FinancialYear.objects.create(start_date="2025-04-01", end_date="2026-03-31")
        LedgerData.objects.create(
            user=self.user,
            l_r_no="TEST-01",
            financial_year=self.fy,
            bill_ammount=50000,
            frieght=1200,
            supplier="Surat Textiles",
        )
        self.run = IntelligenceRun.objects.create(
            user=self.user,
            financial_year=self.fy,
            seller_name="Cash Center",
            total_records=5,
            final_refined_insight=(
                "## 1. Executive Summary\nCash Center sales must be improved.\n\n"
                "### 📅 DAYS 1–30: Liquidate Dead Capital\n- Freeze fresh orders.\n"
            ),
            final_refined_insight_hi=(
                "## 1. कार्यकारी सारांश\nकैश सेंटर की बिक्री में सुधार होना चाहिए।\n\n"
                "### 📅 दिन 1-30: निष्क्रिय पूंजी का परिसमापन\n- नए ऑर्डर फ्रीज करें।\n"
            ),
            generated_prompt="prompt",
            grounding_score=90,
        )

    def test_dashboard_embeds_dual_data_json_scripts(self):
        client = Client()
        client.login(username="bilingual_user", password="password123")
        session = client.session
        session['intelligence_admin_unlocked'] = True
        session.save()

        response = client.get(reverse('intelligence:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="stats-en-data"')
        self.assertContains(response, 'id="stats-hi-data"')
        self.assertContains(response, 'id="report-en-data"')
        self.assertContains(response, 'id="report-hi-data"')
        self.assertContains(response, 'id="chart-data"')
        self.assertContains(response, 'id="chart-data-hi"')
        # Verify Hindi parsed data in context
        self.assertIn("report_hi", response.context)
        self.assertTrue(response.context["report_hi"]["ok"])
        self.assertIn("stats_hi", response.context)
        self.assertEqual(response.context["stats_hi"]["kpis"][0]["label"], "खरीदा गया माल")

    def test_api_translate_endpoint(self):
        client = Client()
        client.login(username="bilingual_user", password="password123")
        resp = client.get(reverse('intelligence:api_translate') + '?q=Hello&to=hi')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertIn("translated", data)



