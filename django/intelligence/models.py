from django.db import models
from django.contrib.auth.models import User


class IntelligenceRun(models.Model):
    """Stores full telemetry and outputs of an AI Market Intelligence DAG execution."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='intelligence_runs')
    financial_year = models.ForeignKey(
        'core.FinancialYear',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)
    seller_name = models.CharField(max_length=255, default='CashCenter Wholesale Merchant')
    total_records = models.IntegerField(default=0)
    total_revenue = models.FloatField(default=0.0)
    total_parcels = models.FloatField(default=0.0)
    anomalies_flagged = models.IntegerField(default=0)
    grounding_score = models.FloatField(default=90.0)
    hallucination_risk = models.CharField(max_length=30, default='LOW')
    execution_time_seconds = models.FloatField(default=0.0)

    # Core prompt & reasoning deliverables
    generated_prompt = models.TextField(blank=True, default='')
    initial_insight = models.TextField(blank=True, default='')
    critique_text = models.TextField(blank=True, default='')
    final_refined_insight = models.TextField(blank=True, default='')
    final_refined_insight_hi = models.TextField(blank=True, default='')

    # Full structured data payloads
    cleaning_report_json = models.JSONField(default=dict, blank=True)
    market_search_json = models.JSONField(default=list, blank=True)
    dag_nodes_json = models.JSONField(default=list, blank=True)
    human_feedback = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Run #{self.id} - {self.seller_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class IntelligenceFeedback(models.Model):
    """Stores iterative human & AI feedback loops on a run."""

    run = models.ForeignKey(IntelligenceRun, on_delete=models.CASCADE, related_name='feedback_iterations')
    iteration = models.IntegerField(default=1)
    human_instruction = models.TextField()
    critique = models.TextField(blank=True, default='')
    refined_output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['iteration']

    def __str__(self):
        return f"Feedback #{self.id} for Run #{self.run_id} (Iteration {self.iteration})"
