from django.contrib import admin
from .models import IntelligenceRun, IntelligenceFeedback


class IntelligenceFeedbackInline(admin.TabularInline):
    model = IntelligenceFeedback
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('iteration', 'human_instruction', 'critique', 'refined_output', 'created_at')


@admin.register(IntelligenceRun)
class IntelligenceRunAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'seller_name',
        'financial_year',
        'status',
        'total_records',
        'total_revenue',
        'grounding_score',
        'hallucination_risk',
        'execution_time_seconds',
        'created_at',
    )
    list_filter = (
        'status',
        'hallucination_risk',
        'created_at',
        'financial_year',
    )
    search_fields = (
        'seller_name',
        'user__username',
        'final_refined_insight',
        'final_refined_insight_hi',
    )
    readonly_fields = (
        'created_at',
        'total_records',
        'total_revenue',
        'total_parcels',
        'anomalies_flagged',
        'grounding_score',
        'hallucination_risk',
        'execution_time_seconds',
        'cleaning_report_json',
        'market_search_json',
        'dag_nodes_json',
    )
    fieldsets = (
        (
            'Run Overview',
            {
                'fields': (
                    'user',
                    'seller_name',
                    'financial_year',
                    'status',
                    'created_at',
                    'execution_time_seconds',
                )
            },
        ),
        (
            'Telemetry & Risk Verification',
            {
                'fields': (
                    'total_records',
                    'total_revenue',
                    'total_parcels',
                    'anomalies_flagged',
                    'grounding_score',
                    'hallucination_risk',
                )
            },
        ),
        (
            'Deliverables (Dual-Data English & Hindi)',
            {
                'fields': (
                    'final_refined_insight',
                    'final_refined_insight_hi',
                    'human_feedback',
                )
            },
        ),
        (
            'DAG Pipeline Deliberation (Internal)',
            {
                'classes': ('collapse',),
                'fields': (
                    'generated_prompt',
                    'initial_insight',
                    'critique_text',
                ),
            },
        ),
        (
            'Raw Structured JSON Artifacts',
            {
                'classes': ('collapse',),
                'fields': (
                    'cleaning_report_json',
                    'market_search_json',
                    'dag_nodes_json',
                ),
            },
        ),
    )
    inlines = [IntelligenceFeedbackInline]


@admin.register(IntelligenceFeedback)
class IntelligenceFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'iteration', 'created_at')
    list_filter = ('created_at', 'iteration')
    search_fields = (
        'human_instruction',
        'critique',
        'refined_output',
        'run__seller_name',
    )
    readonly_fields = ('created_at',)
