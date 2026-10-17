"""Business-owner friendly view models for the Market Intelligence dashboard.

Two responsibilities, both side-effect free:

1. ``compute_ledger_stats``  - real numbers computed from the shop's own ledger
   (no placeholders), formatted for quick scanning.
2. ``parse_report``          - splits the AI's markdown report into a headline,
   a 30/60/90-day plan and expandable topic sections.

Everything returned here is plain text / numbers. The templates auto-escape it,
so nothing from the AI or the ledger is ever injected as raw HTML.
"""
from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from typing import Any, Dict, List, Optional

from django.utils import timezone

from ledger.models import LedgerData

# A consignment still on the road after this many days is worth flagging.
TRANSIT_WARN_DAYS = 10
# Freight above this share of goods value is flagged as a cost to watch.
FREIGHT_WARN_PCT = 5.0
# One supplier above this share of spend is a dependency risk.
SUPPLIER_CONCENTRATION_PCT = 35.0


# --------------------------------------------------------------------------- #
# Formatting helpers
# --------------------------------------------------------------------------- #
def format_inr(value: float) -> str:
    """Short Indian-style money: ₹1.62 Cr, ₹16.2 L, ₹54,200."""
    value = float(value or 0)
    sign = "-" if value < 0 else ""
    v = abs(value)
    if v >= 1e7:
        return f"{sign}₹{v / 1e7:.2f} Cr"
    if v >= 1e5:
        return f"{sign}₹{v / 1e5:.1f} L"
    return f"{sign}₹{v:,.0f}"


def _short(text: str, limit: int) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:-– ")
    return cut + "…"


def _pct(part: float, whole: float) -> float:
    return round(part / whole * 100, 1) if whole else 0.0


# --------------------------------------------------------------------------- #
# 1. Ledger statistics
# --------------------------------------------------------------------------- #
def _ledger_queryset(user, financial_year=None):
    """Same scoping rules the AI pipeline uses, so both always see the same data."""
    qs = LedgerData.objects.all()
    if user and not user.is_superuser:
        qs = qs.filter(user=user)
    if financial_year:
        qs = qs.filter(financial_year=financial_year)
    return qs


HINDI_MONTH_ABBR = {
    "Jan": "जनवरी", "Feb": "फ़रवरी", "Mar": "मार्च", "Apr": "अप्रैल",
    "May": "मई", "Jun": "जून", "Jul": "जुलाई", "Aug": "अगस्त",
    "Sep": "सितंबर", "Oct": "अक्टूबर", "Nov": "नवंबर", "Dec": "दिसंबर"
}


def compute_ledger_stats(user, financial_year=None, today: Optional[date] = None, lang: str = "en") -> Dict[str, Any]:
    """Real, display-ready numbers from the ledger in English or Hindi. Safe on an empty ledger."""
    today = today or timezone.localdate()
    rows = list(_ledger_queryset(user, financial_year))

    stats: Dict[str, Any] = {
        "has_data": bool(rows),
        "count": len(rows),
        "kpis": [],
        "flags": [],
        "chart": {"months": [], "month_values": [], "supplier_labels": [], "supplier_values": []},
        "fabrics": [],
    }
    if not rows:
        return stats

    total = sum(r.bill_ammount or 0 for r in rows)
    freight = sum(r.frieght or 0 for r in rows)
    bales = sum(r.no_of_bale or 0 for r in rows)
    metres = sum(r.pcs_mtr or 0 for r in rows)
    freight_pct = _pct(freight, total)

    # ---- monthly purchases: continuous month axis (empty months show as 0) ----
    monthly: Dict[tuple, float] = defaultdict(float)
    for r in rows:
        if r.l_r_date:
            monthly[(r.l_r_date.year, r.l_r_date.month)] += r.bill_ammount or 0
    months: List[tuple] = []
    if monthly:
        y, m = min(monthly)
        last = max(monthly)
        while (y, m) <= last:
            months.append((y, m))
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        months = months[-12:]

    if lang == "hi":
        month_labels = [
            f"{HINDI_MONTH_ABBR.get(date(y, m, 1).strftime('%b'), date(y, m, 1).strftime('%b'))} {date(y, m, 1).strftime('%y')}"
            for y, m in months
        ]
    else:
        month_labels = [date(y, m, 1).strftime("%b %y") for y, m in months]
    month_values = [round(monthly.get(k, 0.0), 2) for k in months]

    # Month-over-month compares the last two *complete, adjacent* months only, so a
    # half-finished current month can never look like a crash.
    mom_text = "मासिक तुलना के लिए पर्याप्त डेटा नहीं है" if lang == "hi" else "Not enough history for a monthly trend"
    mom_trend = "flat"
    complete = [k for k in months if k != (today.year, today.month)]
    if len(complete) >= 2:
        prev_k, last_k = complete[-2], complete[-1]
        adjacent = (last_k[0] * 12 + last_k[1]) - (prev_k[0] * 12 + prev_k[1]) == 1
        prev_v, last_v = monthly.get(prev_k, 0.0), monthly.get(last_k, 0.0)
        if adjacent and prev_v:
            change = (last_v - prev_v) / prev_v * 100
            mom_trend = "up" if change > 1 else "down" if change < -1 else "flat"
            if lang == "hi":
                p_m = HINDI_MONTH_ABBR.get(date(*prev_k, 1).strftime('%b'), date(*prev_k, 1).strftime('%b'))
                l_m = HINDI_MONTH_ABBR.get(date(*last_k, 1).strftime('%b'), date(*last_k, 1).strftime('%b'))
                mom_text = f"{p_m} की तुलना में {l_m} में {change:+.0f}%"
            else:
                mom_text = (
                    f"{change:+.0f}% in {date(*last_k, 1).strftime('%b')} "
                    f"vs {date(*prev_k, 1).strftime('%b')}"
                )

    # ---- transit & delivery speed ----
    in_transit = [r for r in rows if (not r.status) or not r.delivery]
    transit_value = sum(r.bill_ammount or 0 for r in in_transit)
    durations = [
        (r.delivery - r.l_r_date).days
        for r in rows
        if r.delivery and r.l_r_date and r.delivery >= r.l_r_date
    ]
    avg_days = round(sum(durations) / len(durations), 1) if durations else None

    # ---- suppliers ----
    by_supplier: Dict[str, Dict[str, float]] = defaultdict(lambda: {"bill": 0.0, "freight": 0.0})
    for r in rows:
        name = (r.supplier or "Unnamed supplier").strip()
        by_supplier[name]["bill"] += r.bill_ammount or 0
        by_supplier[name]["freight"] += r.frieght or 0
    ranked = sorted(by_supplier.items(), key=lambda kv: kv[1]["bill"], reverse=True)
    top_name, top_vals = ranked[0]
    top_share = _pct(top_vals["bill"], total)

    top5 = ranked[:5]
    labels = [_short(n, 26) for n, _ in top5]
    values = [round(v["bill"], 2) for _, v in top5]
    other = sum(v["bill"] for _, v in ranked[5:])
    if other > 0:
        labels.append("अन्य सभी" if lang == "hi" else "All others")
        values.append(round(other, 2))

    # ---- top fabrics by spend ----
    by_item: Dict[str, float] = defaultdict(float)
    for r in rows:
        by_item[_short((r.item or "Unlabelled fabric"), 46)] += r.bill_ammount or 0
    item_ranked = sorted(by_item.items(), key=lambda kv: kv[1], reverse=True)
    top_item_val = item_ranked[0][1] or 1
    fabrics = [
        {
            "name": n,
            "value": format_inr(v),
            "share": _pct(v, total),
            "bar": max(round(v / top_item_val * 100), 3),
        }
        for n, v in item_ranked
    ]

    # ---- KPI cards ----
    if lang == "hi":
        stats["kpis"] = [
            {
                "key": "bought",
                "icon": "fa-bag-shopping",
                "label": "खरीदा गया माल",
                "value": format_inr(total),
                "sub": mom_text,
                "trend": mom_trend,
                "tone": "neutral",
                "hint": "इस वर्ष आपके बहीखाते में दर्ज सप्लायर बिलों का कुल मूल्य।",
                "spark": month_values,
            },
            {
                "key": "freight",
                "icon": "fa-truck-fast",
                "label": "चुकाया गया भाड़ा",
                "value": format_inr(freight),
                "sub": f"माल मूल्य का {freight_pct}%",
                "trend": "flat",
                "tone": "warn" if freight_pct > FREIGHT_WARN_PCT else "good",
                "hint": "माल की लागत पर लगा भाड़ा। थोक वस्त्र व्यापार में 5% से कम भाड़ा स्वस्थ माना जाता है।",
                "spark": [],
            },
            {
                "key": "transit",
                "icon": "fa-road",
                "label": "रास्ते में (ट्रांजिट)",
                "value": str(len(in_transit)),
                "sub": f"{format_inr(transit_value)} मूल्य का" if in_transit else "सभी माल दुकान पर पहुंच चुका है",
                "trend": "flat",
                "tone": "warn" if any(
                    r.l_r_date and (today - r.l_r_date).days > TRANSIT_WARN_DAYS for r in in_transit
                ) else "neutral",
                "hint": "वे चालान जिनका बिल बन चुका है पर डिलीवरी अभी नहीं हुई। माल आने तक पूंजी फंसी रहती है।",
                "spark": [],
            },
            {
                "key": "delivery",
                "icon": "fa-clock",
                "label": "औसत डिलीवरी समय",
                "value": f"{avg_days:g} दिन" if avg_days is not None else "—",
                "sub": f"न्यूनतम {min(durations)} दिन · अधिकतम {max(durations)} दिन" if durations else "अभी कोई डिलीवर खेप नहीं है",
                "trend": "flat",
                "tone": "neutral",
                "hint": "ट्रांसपोर्ट बिल्टी (L/R) तारीख से माल दुकान पर पहुंचने में लगा औसत समय।",
                "spark": [],
            },
            {
                "key": "suppliers",
                "icon": "fa-handshake",
                "label": "सप्लायर्स (आपूर्तिकर्ता)",
                "value": str(len(by_supplier)),
                "sub": f"{_short(top_name, 24)} = खर्च का {top_share:g}%",
                "trend": "flat",
                "tone": "warn" if top_share > SUPPLIER_CONCENTRATION_PCT else "neutral",
                "hint": "आपने कितने सप्लायरों से माल खरीदा, और शीर्ष सप्लायर की आपके कुल खर्च में कितनी हिस्सेदारी है।",
                "spark": [],
            },
            {
                "key": "volume",
                "icon": "fa-boxes-stacked",
                "label": "प्राप्त गांठें (बेल्स)",
                "value": f"{bales:,}",
                "sub": f"{metres:,.0f} मीटर कपड़ा" if metres else "मीटर दर्ज नहीं हैं",
                "trend": "flat",
                "tone": "neutral",
                "hint": "दुकान में आया कुल भौतिक माल (गांठें एवं मीटर)।",
                "spark": [],
            },
        ]
    else:
        stats["kpis"] = [
            {
                "key": "bought",
                "icon": "fa-bag-shopping",
                "label": "Goods bought",
                "value": format_inr(total),
                "sub": mom_text,
                "trend": mom_trend,
                "tone": "neutral",
                "hint": "Total value of supplier bills recorded in your ledger this year.",
                "spark": month_values,
            },
            {
                "key": "freight",
                "icon": "fa-truck-fast",
                "label": "Freight paid",
                "value": format_inr(freight),
                "sub": f"{freight_pct}% of goods value",
                "trend": "flat",
                "tone": "warn" if freight_pct > FREIGHT_WARN_PCT else "good",
                "hint": "Transport cost added on top of goods. Under ~5% is healthy for this trade.",
                "spark": [],
            },
            {
                "key": "transit",
                "icon": "fa-road",
                "label": "Still on the road",
                "value": str(len(in_transit)),
                "sub": f"worth {format_inr(transit_value)}" if in_transit else "Everything has arrived",
                "trend": "flat",
                "tone": "warn" if any(
                    r.l_r_date and (today - r.l_r_date).days > TRANSIT_WARN_DAYS for r in in_transit
                ) else "neutral",
                "hint": "Consignments with a bill but no delivery date yet. Your money is tied up until they arrive.",
                "spark": [],
            },
            {
                "key": "delivery",
                "icon": "fa-clock",
                "label": "Average delivery time",
                "value": f"{avg_days:g} days" if avg_days is not None else "—",
                "sub": f"fastest {min(durations)}d · slowest {max(durations)}d" if durations else "No delivered consignments yet",
                "trend": "flat",
                "tone": "neutral",
                "hint": "Days from the transport bill (L/R) date to the day goods reached you.",
                "spark": [],
            },
            {
                "key": "suppliers",
                "icon": "fa-handshake",
                "label": "Suppliers",
                "value": str(len(by_supplier)),
                "sub": f"{_short(top_name, 24)} = {top_share:g}% of spend",
                "trend": "flat",
                "tone": "warn" if top_share > SUPPLIER_CONCENTRATION_PCT else "neutral",
                "hint": "How many suppliers you bought from, and how much of your spend the biggest one holds.",
                "spark": [],
            },
            {
                "key": "volume",
                "icon": "fa-boxes-stacked",
                "label": "Bales received",
                "value": f"{bales:,}",
                "sub": f"{metres:,.0f} metres of fabric" if metres else "Metres not recorded",
                "trend": "flat",
                "tone": "neutral",
                "hint": "Physical volume that came in, regardless of price.",
                "spark": [],
            },
        ]

    # ---- "Things to watch" ----
    flags: List[Dict[str, str]] = []
    stuck = sorted(
        (r for r in in_transit if r.l_r_date and (today - r.l_r_date).days > TRANSIT_WARN_DAYS),
        key=lambda r: r.l_r_date,
    )
    if stuck:
        oldest = stuck[0]
        days_stuck = (today - oldest.l_r_date).days
        stuck_val = format_inr(sum(r.bill_ammount or 0 for r in stuck))
        if lang == "hi":
            flags.append({
                "level": "warn",
                "icon": "fa-triangle-exclamation",
                "title": f"{TRANSIT_WARN_DAYS} दिनों से अधिक समय से रास्ते में {len(stuck)} खेप",
                "detail": (
                    f"सबसे पुराना L/R {oldest.l_r_no} ({oldest.supplier or 'सप्लायर'}, {days_stuck} दिन) से है। "
                    f"{stuck_val} का माल अभी तक दुकान नहीं पहुंचा है।"
                ),
            })
        else:
            flags.append({
                "level": "warn",
                "icon": "fa-triangle-exclamation",
                "title": f"{len(stuck)} consignment{'s' if len(stuck) > 1 else ''} on the road for over {TRANSIT_WARN_DAYS} days",
                "detail": (
                    f"Oldest is L/R {oldest.l_r_no} from {oldest.supplier or 'a supplier'} "
                    f"({days_stuck} days). "
                    f"{stuck_val} of stock is not yet in your shop."
                ),
            })

    if top_share > SUPPLIER_CONCENTRATION_PCT and len(by_supplier) > 1:
        if lang == "hi":
            flags.append({
                "level": "warn",
                "icon": "fa-link",
                "title": f"खर्च का {top_share:g}% एक ही सप्लायर ({_short(top_name, 30)}) के पास",
                "detail": "यदि यह सप्लायर भाव बढ़ाता है या माल में देरी करता है, तो आपका बड़ा हिस्सा प्रभावित होगा।",
            })
        else:
            flags.append({
                "level": "warn",
                "icon": "fa-link",
                "title": f"{_short(top_name, 30)} supplies {top_share:g}% of what you buy",
                "detail": "If this supplier raises prices or delays a shipment, a big part of your stock is affected.",
            })

    worst = max(
        ((n, _pct(v["freight"], v["bill"])) for n, v in by_supplier.items() if v["bill"]),
        key=lambda kv: kv[1],
        default=None,
    )
    if worst and worst[1] > FREIGHT_WARN_PCT:
        if lang == "hi":
            flags.append({
                "level": "warn" if freight_pct > FREIGHT_WARN_PCT else "info",
                "icon": "fa-money-bill-transfer",
                "title": f"{_short(worst[0], 30)} पर भाड़ा सर्वाधिक है (बिल का {worst[1]:g}%)",
                "detail": f"सभी सप्लायरों में औसत भाड़ा {freight_pct}% है। जांचें कि क्या बड़े व कम अंतराल के ऑर्डर से यह कम हो सकता है।",
            })
        else:
            flags.append({
                "level": "warn" if freight_pct > FREIGHT_WARN_PCT else "info",
                "icon": "fa-money-bill-transfer",
                "title": f"Freight is highest on {_short(worst[0], 30)} ({worst[1]:g}% of bill value)",
                "detail": f"Across all suppliers freight averages {freight_pct}%. Ask whether bigger, less frequent loads would cut this.",
            })
    stats["flags"] = flags[:3]

    stats["chart"] = {
        "months": month_labels,
        "month_values": month_values,
        "supplier_labels": labels,
        "supplier_values": values,
    }
    stats["fabrics"] = fabrics
    return stats


# --------------------------------------------------------------------------- #
# 2. AI report -> digestible structure
# --------------------------------------------------------------------------- #
_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_EMPHASIS = re.compile(r"(\*\*|__|\*|`)")
_BULLET = re.compile(r"^\s*(?:[*\-•]|\d+[.)])\s+(.*)$")


def _plain(text: str) -> str:
    text = _LINK.sub(r"\1", text)
    text = _EMPHASIS.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def _first_sentence(text: str, limit: int = 230) -> str:
    text = _plain(text)
    first = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9₹\"“(])", text, maxsplit=1)[0]
    return _short(first, limit)


def _split_emoji(heading: str) -> tuple:
    """'1. 🎯 Executive ...' -> ('1', '🎯', 'Executive ...')."""
    m = re.match(r"^(?:(\d+)[.)]\s*)?(.*)$", heading.strip())
    num, rest = (m.group(1) or ""), m.group(2).strip()
    emoji = ""
    parts = rest.split(None, 1)
    if parts and not re.search(r"\w", parts[0]):
        emoji, rest = parts[0], (parts[1] if len(parts) > 1 else "")
    return num, emoji, rest.strip()


def _headline(body: str, limit: int = 170) -> str:
    """One-line gist: prose -> first bullet -> a leading note -> first sub-heading."""
    first_bullet = note = ""
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para or para.startswith(("#", "|", ">", "---")):
            continue
        bullet = _BULLET.match(para.splitlines()[0])
        if bullet:
            first_bullet = first_bullet or bullet.group(1)
            continue
        if _plain(para).lower().startswith("note"):
            note = note or para
            continue
        return _first_sentence(para, limit)
    if first_bullet:
        return _first_sentence(first_bullet, limit)
    if note:
        return _first_sentence(re.sub(r"(?i)^\W*note[^:]*:\s*", "", note), limit)
    sub = re.search(r"(?m)^###\s+(.*)$", body)
    return _short(_split_emoji(sub.group(1))[2], limit) if sub else ""


def _bullets(block: str, limit: int = 3) -> List[Dict[str, str]]:
    """Top bullets as {lead, detail}; '**Lead:** rest' becomes lead + detail."""
    out: List[Dict[str, str]] = []
    for line in block.splitlines():
        m = _BULLET.match(line)
        if not m:
            continue
        raw = m.group(1).strip()
        lead_m = re.match(r"^\*\*(.+?)\*\*[:\s–-]*(.*)$", raw)
        if lead_m:
            lead = _plain(lead_m.group(1)).rstrip(":")
            detail = _first_sentence(lead_m.group(2), 170) if lead_m.group(2) else ""
        else:
            lead, detail = _first_sentence(raw, 90), ""
        if lead:
            out.append({"lead": _short(lead, 90), "detail": detail})
        if len(out) >= limit:
            break
    return out


def _extract_plan(body: str) -> List[Dict[str, Any]]:
    """Find '### 📅 DAYS 1–30: Title' blocks and keep their top actions."""
    plan: List[Dict[str, Any]] = []
    chunks = re.split(r"(?m)^###\s+", body)[1:]
    for chunk in chunks:
        head, _, rest = chunk.partition("\n")
        _, _, head_clean = _split_emoji(head)
        # Only real phase headings such as "DAYS 1–30: ..." or "दिन 1–30: ...".
        if not re.match(r"(?i)^(?:days?|दिन)\s*\d", head_clean):
            continue
        label, _, title = head_clean.partition(":")
        plan.append({
            "label": _plain(label) or "Next steps",
            "title": _short(_plain(title), 80),
            "actions": _bullets(rest, limit=3),
        })
    return plan


def parse_report(markdown_text: str) -> Dict[str, Any]:
    """Break the AI report into headline, 30/60/90 plan and topic sections."""
    empty = {
        "ok": False, "title": "", "headline": "", "summary": "",
        "sections": [], "plan": [], "first_actions": [],
    }
    if not (markdown_text or "").strip():
        return empty

    title = ""
    sections: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None
    for line in markdown_text.splitlines():
        if re.match(r"^##\s+", line):
            num, emoji, name = _split_emoji(re.sub(r"^##\s+", "", line))
            current = {"num": num, "emoji": emoji, "title": name, "lines": []}
            sections.append(current)
        elif re.match(r"^#\s+", line) and not title:
            title = _split_emoji(re.sub(r"^#\s+", "", line))[2]
        elif current is not None:
            current["lines"].append(line)

    plan: List[Dict[str, Any]] = []
    out_sections: List[Dict[str, Any]] = []
    for idx, sec in enumerate(sections, start=1):
        body = "\n".join(sec["lines"]).strip()
        sec_plan = _extract_plan(body)
        if sec_plan and not plan:
            plan = sec_plan
        out_sections.append({
            "key": f"sec-{idx}",
            "num": sec["num"] or str(idx),
            "emoji": sec["emoji"] or "📄",
            "title": sec["title"],
            "headline": _headline(body),
            "body": body,
            "is_plan": bool(sec_plan),
        })

    first_actions = plan[0]["actions"] if plan else []
    return {
        "ok": bool(out_sections),
        "title": title,
        "headline": out_sections[0]["headline"] if out_sections else "",
        # Longer gist for the hero card (the first section's opening sentence).
        "summary": _headline(out_sections[0]["body"], 340) if out_sections else "",
        "sections": out_sections,
        "plan": plan,
        "first_actions": first_actions,
    }
