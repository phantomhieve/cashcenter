import json
import logging
import math
from dataclasses import asdict
from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from core.views import _verify_fy_password
from ledger.backend import getUserGroup
from datetime import timedelta
from django.utils import timezone
from .insights import compute_ledger_stats, parse_report
from .models import IntelligenceFeedback, IntelligenceRun
from .pipeline.dag import MarketIntelligenceDAG
from .translation import translate_text, translate_markdown

logger = logging.getLogger(__name__)


SESSION_UNLOCKED_KEY = 'intelligence_admin_unlocked'


def get_monthly_quota_status(user) -> dict:
    """Calculate whether user has utilized their once-per-month intelligence run."""
    last_run = IntelligenceRun.objects.filter(
        user=user,
        status=IntelligenceRun.Status.COMPLETED
    ).order_by('-created_at').first()

    if not last_run:
        return {
            'is_limited': False,
            'last_run': None,
            'days_remaining': 0,
            'next_available_date': None,
        }

    now = timezone.now()
    cutoff = last_run.created_at + timedelta(days=30)
    if now < cutoff:
        days_rem = max(math.ceil((cutoff - now).total_seconds() / 86400), 1)
        return {
            'is_limited': True,
            'last_run': last_run,
            'days_remaining': days_rem,
            'next_available_date': cutoff,
        }
    return {
        'is_limited': False,
        'last_run': last_run,
        'days_remaining': 0,
        'next_available_date': None,
    }


def intelligence_admin_required(view_func):
    """Decorator ensuring user is logged in AND has unlocked using their admin password."""
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('user_login')

        if not request.session.get(SESSION_UNLOCKED_KEY, False):
            # Save target url in session to redirect back after unlocking
            request.session['intelligence_next_url'] = request.get_full_path()
            return redirect('intelligence:auth_gate')

        return view_func(request, *args, **kwargs)
    return _wrapped


def auth_gate(request: HttpRequest) -> HttpResponse:
    """Security Gate requiring the user's admin password before accessing intelligence."""
    if not request.user.is_authenticated:
        return redirect('user_login')

    if request.session.get(SESSION_UNLOCKED_KEY, False):
        next_url = request.session.pop('intelligence_next_url', None) or 'intelligence:dashboard'
        return redirect(next_url)

    error_msg = None
    if request.method == 'POST':
        password = request.POST.get('password', '')
        if _verify_fy_password(request.user, password):
            request.session[SESSION_UNLOCKED_KEY] = True
            messages.success(request, "Admin access verified. Welcome to Market Intelligence.")
            next_url = request.session.pop('intelligence_next_url', None) or 'intelligence:dashboard'
            return redirect(next_url)
        else:
            error_msg = "Incorrect Admin Password. Please try again."

    return render(request, 'intelligence/auth_gate.html', {
        'error_msg': error_msg,
        'user': request.user,
    })


@require_http_methods(["POST"])
def api_verify_password(request: HttpRequest) -> JsonResponse:
    """AJAX endpoint for validating admin password."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
    try:
        data = json.loads(request.body)
        password = data.get('password', '')
        if _verify_fy_password(request.user, password):
            request.session[SESSION_UNLOCKED_KEY] = True
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'message': 'Incorrect Admin Password'})
    except Exception as e:
        logger.warning("Error verifying admin password: %s", e)
        return JsonResponse({'success': False, 'message': 'Invalid request data'}, status=400)


@login_required
def lock_dashboard(request: HttpRequest) -> HttpResponse:
    """Explicitly lock the intelligence module."""
    request.session[SESSION_UNLOCKED_KEY] = False
    messages.info(request, "Market Intelligence dashboard locked.")
    return redirect('intelligence:auth_gate')


def _confidence(run) -> dict:
    """Translate the technical grounding score into plain words for the owner."""
    score = float(run.grounding_score or 0)
    if score >= 80:
        label, tone = "High", "good"
    elif score >= 60:
        label, tone = "Moderate", "warn"
    else:
        label, tone = "Low", "bad"
    return {"label": label, "tone": tone, "score": round(score)}


@intelligence_admin_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Business-owner overview: real ledger numbers + the AI's plain-English advice."""
    runs = IntelligenceRun.objects.filter(user=request.user)
    latest_run = runs.first()

    # Determine shop / seller context
    user_group = getUserGroup(request.user)
    shop_name = user_group.shop if user_group else "Cash Center"

    quota = get_monthly_quota_status(request.user)
    current_fy = getattr(request, 'financial_year', None)

    stats_en = compute_ledger_stats(request.user, current_fy, lang="en")
    stats_hi = compute_ledger_stats(request.user, current_fy, lang="hi")

    if latest_run and not latest_run.final_refined_insight_hi and latest_run.final_refined_insight:
        latest_run.final_refined_insight_hi = translate_markdown(latest_run.final_refined_insight, "hi")
        latest_run.save(update_fields=["final_refined_insight_hi"])

    report = parse_report(latest_run.final_refined_insight) if latest_run else parse_report('')
    report_hi = parse_report(latest_run.final_refined_insight_hi) if (latest_run and latest_run.final_refined_insight_hi) else None

    return render(request, 'intelligence/dashboard.html', {
        'runs': runs[:10],
        'latest_run': latest_run,
        'shop_name': shop_name,
        'location': 'Bara Bazar, Darbhanga, Bihar',
        'quota': quota,
        'can_refresh': not quota['is_limited'],
        'current_fy': current_fy,
        'stats': stats_en,
        'stats_hi': stats_hi,
        'chart_data': stats_en['chart'],
        'chart_data_hi': stats_hi['chart'],
        'report': report,
        'report_hi': report_hi,
        'confidence': _confidence(latest_run) if latest_run else None,
        'market_searches': latest_run.market_search_json if latest_run else [],
    })


@intelligence_admin_required
@require_http_methods(["POST"])
def run_analysis(request: HttpRequest) -> HttpResponse:
    """Trigger the multi-stage DAG workflow engine with monthly quota guardrails."""
    source_type = request.POST.get('source_type', 'db')  # 'db' or 'raw'
    raw_payload = request.POST.get('raw_payload', '').strip()
    human_notes = request.POST.get('human_notes', '').strip()
    force_override = request.POST.get('force_override', 'false').lower() in ('1', 'true', 'yes', 'on')

    # Guardrail: Limit to once a month for AI insights
    quota = get_monthly_quota_status(request.user)
    if quota['is_limited'] and not force_override:
        last_date_str = quota['last_run'].created_at.strftime('%b %d, %Y')
        next_date_str = quota['next_available_date'].strftime('%b %d, %Y')
        messages.warning(
            request,
            f"Insights were last refreshed on {last_date_str}. "
            f"To keep the advice meaningful, they can be refreshed once every 30 days "
            f"- next refresh opens on {next_date_str} ({quota['days_remaining']} days to go)."
        )
        return redirect('intelligence:dashboard')

    user_group = getUserGroup(request.user)
    shop_name = user_group.shop if user_group else "Cash Center"
    seller_ctx = {
        'shop_name': shop_name,
        'location': 'Bara Bazar, Darbhanga, Bihar',
        'turnover': '~₹12 Crore INR / year (~₹1.0 Cr / month)',
        'problem_statement': (
            'Average yearly turnover over last 2-3 years is ~₹12 CR, but sales have started declining. '
            'We urgently need strategic insights on how to improve sales, protect margins against Surat mill-direct bypass, '
            'and shift inventory towards high-velocity running fabrics for North Bihar & Mithila retail.'
        ),
        'vertical': 'Wholesale & Semi-Wholesale Fabrics & Textiles',
    }

    dag = MarketIntelligenceDAG()
    raw_records = None
    if source_type == 'raw' and raw_payload:
        raw_records = dag.cleaner.ingest_from_raw_text(raw_payload)
    else:
        raw_records = dag.cleaner.ingest_from_db(
            user=request.user,
            financial_year=getattr(request, 'financial_year', None),
        )

    try:
        dag_result = dag.execute(
            raw_records=raw_records,
            seller_context=seller_ctx,
            human_feedback=human_notes if human_notes else None,
        )

        # Persist to database
        run_obj = IntelligenceRun.objects.create(
            user=request.user,
            financial_year=getattr(request, 'financial_year', None),
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
            human_feedback=human_notes,
        )

        messages.success(request, "Your insights are up to date.")
        return redirect('intelligence:dashboard')

    except Exception:
        logger.exception("Market intelligence refresh failed for user %s", request.user.pk)
        messages.error(
            request,
            "We couldn't refresh your insights just now. Your previous insights are unchanged - "
            "please try again in a few minutes."
        )
        return redirect('intelligence:dashboard')


@intelligence_admin_required
def run_detail(request: HttpRequest, run_id: int) -> HttpResponse:
    """Detailed view for a specific run with interactive feedback studio."""
    if request.user.is_superuser:
        run = get_object_or_404(IntelligenceRun, id=run_id)
    else:
        run = get_object_or_404(IntelligenceRun, id=run_id, user=request.user)

    if run and not run.final_refined_insight_hi and run.final_refined_insight:
        run.final_refined_insight_hi = translate_markdown(run.final_refined_insight, "hi")
        run.save(update_fields=["final_refined_insight_hi"])

    feedback_items = run.feedback_iterations.all()

    return render(request, 'intelligence/run_detail.html', {
        'run': run,
        'feedback_items': feedback_items,
        'canonical_items': run.cleaning_report_json.get('canonical_items', {}),
        'anomalies': run.cleaning_report_json.get('detected_anomalies', []),
        'buyers': run.cleaning_report_json.get('buyer_summary', {}),
        'market_searches': run.market_search_json,
        'dag_nodes': run.dag_nodes_json,
        'stats': compute_ledger_stats(request.user, run.financial_year),
    })


@intelligence_admin_required
@require_http_methods(["POST"])
def submit_feedback(request: HttpRequest, run_id: int) -> HttpResponse:
    """Human-in-the-loop feedback to trigger an extra critique and refinement loop."""
    if request.user.is_superuser:
        run = get_object_or_404(IntelligenceRun, id=run_id)
    else:
        run = get_object_or_404(IntelligenceRun, id=run_id, user=request.user)
    human_instruction = request.POST.get('human_instruction', '').strip()

    if not human_instruction:
        messages.warning(request, "Please enter guidance for the feedback loop.")
        return redirect('intelligence:run_detail', run_id=run.id)

    dag = MarketIntelligenceDAG()
    loop_result = dag.feedback_loop.run_feedback_cycle(
        comprehensive_prompt=run.generated_prompt,
        initial_insight=run.final_refined_insight,
        cleaning_report_summary={
            'total_records': run.total_records,
            'total_revenue': run.total_revenue,
            'anomalous_records': run.anomalies_flagged,
        },
        market_search_summary=run.market_search_json[:4],
        human_instruction=human_instruction,
    )

    iteration_num = run.feedback_iterations.count() + 1
    IntelligenceFeedback.objects.create(
        run=run,
        iteration=iteration_num,
        human_instruction=human_instruction,
        critique=loop_result.critique_text,
        refined_output=loop_result.refined_insight_raw,
    )

    # Update run's final insight and grounding
    run.final_refined_insight = loop_result.refined_insight_raw
    run.final_refined_insight_hi = translate_markdown(loop_result.refined_insight_raw, "hi")
    run.grounding_score = loop_result.grounding_score
    run.hallucination_risk = loop_result.hallucination_risk
    run.save()

    messages.success(request, f"Feedback Loop #{iteration_num} executed. Report refined with Argon.")
    return redirect('intelligence:run_detail', run_id=run.id)


@login_required
@require_http_methods(["GET", "POST"])
def api_translate(request: HttpRequest) -> JsonResponse:
    """AJAX translation proxy for dynamic text elements on the Market Intelligence dashboard."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("text", "")
            target_lang = data.get("target_lang", "hi")
        except Exception:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)
    else:
        text = request.GET.get("q", "")
        target_lang = request.GET.get("to", "hi")

    translated = translate_text(text, target_lang=target_lang)
    return JsonResponse({"success": True, "original": text, "translated": translated})

