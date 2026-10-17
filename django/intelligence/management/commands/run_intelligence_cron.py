import logging
from dataclasses import asdict
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import FinancialYear
from ledger.backend import getUserGroup
from ledger.models import LedgerData

from intelligence.models import IntelligenceRun
from intelligence.pipeline.dag import MarketIntelligenceDAG
from intelligence.translation import translate_markdown
from intelligence.views import get_monthly_quota_status

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = "Run the 30-day AI Market Intelligence insight refresh cron job for shops"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the cron run without executing the DAG or saving records to database",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force refresh for users even if less than 30 days have elapsed since their last run",
        )
        parser.add_argument(
            "--user",
            type=str,
            help="Limit execution to a single specific username",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Threshold interval in days (default: 30 days)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force = options["force"]
        target_username = options["user"]
        threshold_days = options["days"]

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"==> Starting Market Intelligence 30-Day Cron (dry_run={dry_run}, force={force}, days={threshold_days})"
            )
        )

        users_qs = User.objects.filter(is_active=True)
        if target_username:
            users_qs = users_qs.filter(username=target_username)
            if not users_qs.exists():
                self.stdout.write(self.style.ERROR(f"User '{target_username}' not found or inactive."))
                return

        processed = 0
        executed = 0
        skipped = 0
        errors = 0

        latest_fy = FinancialYear.objects.order_by("-end_date").first()

        for user in users_qs:
            processed += 1
            username = user.username

            # Check monthly quota status
            quota = get_monthly_quota_status(user)
            last_run = quota.get("last_run")

            should_run = False
            reason = ""

            if force:
                should_run = True
                reason = "Forced run (--force requested)"
            elif not last_run:
                should_run = True
                reason = "No prior completed intelligence run found"
            else:
                elapsed = timezone.now() - last_run.created_at
                if elapsed >= timedelta(days=threshold_days):
                    should_run = True
                    reason = f"Last run was {elapsed.days} days ago (>= {threshold_days} days threshold)"
                else:
                    days_left = quota.get("days_remaining", threshold_days - elapsed.days)
                    reason = f"Last run was {elapsed.days} days ago; {days_left} days remaining until next refresh"

            # Check if user has any ledger data to analyze
            user_ledger_count = LedgerData.objects.filter(user=user).count() if not user.is_superuser else LedgerData.objects.count()
            if user_ledger_count == 0 and not user.is_superuser:
                self.stdout.write(
                    self.style.WARNING(f"[-] User '{username}': Skipped (No ledger records present in database).")
                )
                skipped += 1
                continue

            if not should_run:
                self.stdout.write(
                    self.style.NOTICE(f"[-] User '{username}': Skipped ({reason}).")
                )
                skipped += 1
                continue

            self.stdout.write(
                self.style.SUCCESS(f"[+] User '{username}': Eligible for refresh ({reason}). Records: {user_ledger_count}.")
            )

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f"    [DRY RUN] Would execute MarketIntelligenceDAG for user '{username}'.")
                )
                executed += 1
                continue

            # Execute the DAG workflow
            try:
                user_group = getUserGroup(user)
                shop_name = user_group.shop if user_group else "Cash Center"

                seller_ctx = {
                    'shop_name': shop_name,
                    'location': 'Bara Bazar, Darbhanga, Bihar',
                    'turnover': '~₹12 Crore INR / year (~₹1.0 Cr / month)',
                    'problem_statement': (
                        'Scheduled 30-day automated intelligence refresh: Evaluate revenue trends, '
                        'transit delays, and inventory velocity for Mithila wholesale market.'
                    ),
                    'vertical': 'Wholesale & Semi-Wholesale Fabrics & Textiles',
                }

                dag = MarketIntelligenceDAG()
                raw_records = dag.cleaner.ingest_from_db(
                    user=user,
                    financial_year=latest_fy,
                )

                self.stdout.write(f"    Executing DAG pipeline for '{username}' ({len(raw_records)} records)...")
                dag_result = dag.execute(
                    raw_records=raw_records,
                    seller_context=seller_ctx,
                    human_feedback="Automated 30-day periodic scheduled cron refresh",
                )

                # Persist IntelligenceRun
                run_obj = IntelligenceRun.objects.create(
                    user=user,
                    financial_year=latest_fy,
                    status=IntelligenceRun.Status.COMPLETED,
                    seller_name=dag_result.seller_name,
                    total_records=dag_result.total_sales_count,
                    total_revenue=dag_result.total_revenue,
                    total_parcels=dag_result.total_parcels,
                    anomalies_flagged=dag_result.anomalies_flagged,
                    grounding_score=dag_result.grounding_score,
                    hallucination_risk=dag_result.hallucination_risk,
                    execution_time_seconds=dag_result.execution_time_seconds,
                    generated_prompt=dag_result.generated_prompt,
                    initial_insight=dag_result.initial_insight,
                    critique_text=dag_result.critique_text,
                    final_refined_insight=dag_result.final_refined_insight,
                    final_refined_insight_hi=translate_markdown(dag_result.final_refined_insight, "hi"),
                    cleaning_report_json={
                        'canonical_items': dag_result.cleaning_report.canonical_items,
                        'detected_anomalies': dag_result.cleaning_report.detected_anomalies,
                        'buyer_summary': dag_result.cleaning_report.buyer_summary,
                    },
                    market_search_json=[asdict(m) for m in dag_result.market_search_results],
                    dag_nodes_json=[asdict(n) for n in dag_result.node_executions],
                    human_feedback="Automated 30-day periodic scheduled cron refresh",
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"    Successfully generated Run #{run_obj.id} in {dag_result.execution_time_seconds:.1f}s "
                        f"(Score: {dag_result.grounding_score}%, Anomalies: {dag_result.anomalies_flagged})"
                    )
                )
                executed += 1

            except Exception as exc:
                logger.exception("Failed automated intelligence run for user %s", username)
                self.stdout.write(
                    self.style.ERROR(f"    Failed to execute intelligence run for user '{username}': {exc}")
                )
                errors += 1

        self.stdout.write(
            self.style.MIGRATE_LABEL(
                f"\n==> Cron Job Completed. Users processed: {processed}, Executed: {executed}, "
                f"Skipped: {skipped}, Errors: {errors}"
            )
        )
