from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple
from django.db.models import QuerySet
from ledger.models import LedgerData
from ledger_base.models import LedgerDataBase
from orderlist.models import Order
from ratelist.models import RatelistDataHelper


# Known textile domain acronyms and normalizations
TEXTILE_SYNONYMS = {
    r"\bctn\b": "Cotton",
    r"\bcott\b": "Cotton",
    r"\bryn\b": "Rayon",
    r"\bryon\b": "Rayon",
    r"\bprnt\b": "Print",
    r"\bprtd\b": "Printed",
    r"\bslb\b": "Slub",
    r"\bcambrc\b": "Cambric",
    r"\bcmbrc\b": "Cambric",
    r"\bchiff\b": "Chiffon",
    r"\bchifn\b": "Chiffon",
    r"\bgeorg\b": "Georgette",
    r"\bgorgett\b": "Georgette",
    r"\bwh\b": "White",
    r"\bblk\b": "Black",
    r"\bmtr\b": "Meters",
    r"\bmtrs\b": "Meters",
    r"\bpcs\b": "Pieces",
    r"\bpc\b": "Pieces",
    r"\bprcl\b": "Parcels",
    r"\bprcls\b": "Parcels",
    r"\bd\.?no\b": "Design No.",
    r"\bdes\b": "Design",
    r"\blyc\b": "Lycra",
    r"\bjqd\b": "Jacquard",
    r"\borg\b": "Organza",
    r"\bmusl\b": "Muslin",
}


@dataclass
class NormalizedSaleRecord:
    raw_id: str
    raw_item: str
    clean_item: str
    category: str
    buyer: str
    quantity: float
    unit: str
    price: float
    total_amount: float
    sale_date: str
    order_mode: str
    anomalies: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class CleaningReport:
    total_records: int
    cleaned_records: int
    anomalous_records: int
    detected_anomalies: List[Dict[str, Any]]
    canonical_items: Dict[str, Dict[str, Any]]
    total_revenue: float
    total_quantity: float
    buyer_summary: Dict[str, Dict[str, Any]]
    sanitized_dataset: List[NormalizedSaleRecord]


def clean_item_name(raw: str) -> Tuple[str, str]:
    """Clean raw item text, standardize textile terms, and infer category."""
    if not raw:
        return ("Unspecified Item", "General")

    cleaned = raw.strip()
    # Normalize multiple whitespace
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Standardize known contractions
    for pattern, replacement in TEXTILE_SYNONYMS.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    # Clean title case
    cleaned = " ".join([word.capitalize() if not word.isupper() else word for word in cleaned.split()])

    # Infer primary textile category
    cat = "Fabrics"
    c_lower = cleaned.lower()
    if any(k in c_lower for k in ["cotton", "cambric", "poplin", "mulmul"]):
        cat = "Cotton & Natural Blends"
    elif any(k in c_lower for k in ["rayon", "viscose", "modal"]):
        cat = "Rayon & Viscose"
    elif any(k in c_lower for k in ["georgette", "chiffon", "crepe"]):
        cat = "Georgette & Chiffon"
    elif any(k in c_lower for k in ["silk", "jacquard", "brocade", "chanderi", "organza"]):
        cat = "Silks & Festive Jacquards"
    elif any(k in c_lower for k in ["denim", "lycra", "twill"]):
        cat = "Denim & Bottomwear"
    elif any(k in c_lower for k in ["saree", "dupatta", "kurti", "suit"]):
        cat = "Finished Garments & Ethnic Wear"

    return (cleaned, cat)


class SoldDataCleaner:
    """Ingests raw sold data from DB or external uploads, sanitizing anomalies."""

    def ingest_from_db(self, user=None, financial_year=None) -> List[Dict[str, Any]]:
        records = []

        # 1. Primary Source: Ingest from LedgerData (Transport bills, L/R numbers, incoming consignments)
        ledger_qs = LedgerData.objects.all()
        if user and not user.is_superuser:
            ledger_qs = ledger_qs.filter(user=user)
        if financial_year:
            ledger_qs = ledger_qs.filter(financial_year=financial_year)

        for l in ledger_qs:
            qty = float(l.pcs_mtr or (l.no_of_bale * 100) or 1)
            price = float(l.price or 0)
            if not price and l.bill_ammount and qty > 0:
                freight_val = float(l.frieght or 0)
                price = round((float(l.bill_ammount) + freight_val) / qty, 2)

            records.append({
                "id": f"LR-{l.l_r_no or l.id}",
                "item": l.item or "Wholesale Fabric",
                "buyer": l.supplier or "Wholesale Mill Supplier",
                "supplier": l.supplier or "Wholesale Mill Supplier",
                "location": l.location or "Surat / Gujarat Hub",
                "quantity": qty,
                "unit": "meters" if l.pcs_mtr else "bales",
                "price": price,
                "bill_ammount": float(l.bill_ammount or 0),
                "frieght": float(l.frieght or 0),
                "transport": l.transport or "",
                "l_r_no": l.l_r_no or "",
                "bale_no": l.bale_no or "",
                "no_of_bale": l.no_of_bale or 1,
                "date": str(l.l_r_date or date.today()),
                "l_r_date": str(l.l_r_date) if l.l_r_date else "",
                "delivery": str(l.delivery) if l.delivery else "",
                "status": bool(l.status),
                "hsn_code": l.hsn_code or "",
                "remark": l.remark or "",
                "mode": "ledger_transport",
            })

        # 2. Ingest unapproved base ledger entries if any
        base_qs = LedgerDataBase.objects.all()
        if user and not user.is_superuser:
            base_qs = base_qs.filter(user=user)
        for b in base_qs:
            qty = float(b.pcs_mtr or (b.no_of_bale * 100) or 1)
            price = float(b.price or 0)
            if not price and b.bill_ammount and qty > 0:
                freight_val = float(b.frieght or 0)
                price = round((float(b.bill_ammount) + freight_val) / qty, 2)
            records.append({
                "id": f"BASE-LR-{b.l_r_no or b.id}",
                "item": b.item or "Unapproved Fabric Entry",
                "buyer": b.supplier or "Wholesale Supplier",
                "supplier": b.supplier or "Wholesale Supplier",
                "location": b.location or "Surat Hub",
                "quantity": qty,
                "unit": "meters" if b.pcs_mtr else "bales",
                "price": price,
                "bill_ammount": float(b.bill_ammount or 0),
                "frieght": float(b.frieght or 0),
                "transport": b.transport or "",
                "l_r_no": b.l_r_no or "",
                "bale_no": b.bale_no or "",
                "no_of_bale": b.no_of_bale or 1,
                "date": str(b.l_r_date or date.today()),
                "l_r_date": str(b.l_r_date) if b.l_r_date else "",
                "delivery": str(b.delivery) if b.delivery else "",
                "status": bool(b.status),
                "hsn_code": b.hsn_code or "",
                "remark": b.remark or "",
                "mode": "ledger_base",
            })

        # 3. If ledger has very few rows (e.g. fresh/test database), supplement with Order records
        if len(records) < 5:
            order_qs = Order.objects.all()
            if user and not user.is_superuser:
                order_qs = order_qs.filter(user=user)
            if financial_year:
                order_qs = order_qs.filter(financial_year=financial_year)
            for o in order_qs:
                records.append({
                    "id": f"ORD-{o.id}",
                    "item": o.item,
                    "buyer": o.company_name or "Unknown Buyer",
                    "quantity": float(o.num_parcels or 0),
                    "unit": "parcels",
                    "price": float(o.order_price or 0),
                    "date": str(o.order_date or date.today()),
                    "mode": o.mode or "phone",
                    "transport": o.transport or "",
                    "remark": o.remark or "",
                })

        return records

    def ingest_from_raw_text(self, text: str) -> List[Dict[str, Any]]:
        """Parses CSV, JSON, or line-delimited sold records."""
        text = text.strip()
        if not text:
            return []

        # Try JSON
        if text.startswith("[") or text.startswith("{"):
            try:
                data = json.loads(text)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
            except Exception:
                pass

        # Try CSV / TSV
        records = []
        try:
            reader = csv.DictReader(io.StringIO(text))
            for i, row in enumerate(reader):
                item = row.get("item") or row.get("Item") or row.get("product") or row.get("Product") or ""
                buyer = row.get("buyer") or row.get("company") or row.get("Customer") or "Customer"
                qty = float(row.get("quantity") or row.get("qty") or row.get("parcels") or 1)
                price = float(row.get("price") or row.get("rate") or 0)
                d = row.get("date") or str(date.today())
                records.append({
                    "id": f"UPLOAD-{i+1}",
                    "item": item,
                    "buyer": buyer,
                    "quantity": qty,
                    "unit": row.get("unit", "parcels"),
                    "price": price,
                    "date": d,
                    "mode": row.get("mode", "uploaded"),
                })
            if records:
                return records
        except Exception:
            pass

        # Fallback: line-by-line loose format (e.g., "Cotton 60s - 10 parcels - Rs 45000 - ABC Co")
        for i, line in enumerate(text.splitlines()):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in re.split(r"[-;,|]", line)]
            item = parts[0] if len(parts) > 0 else "Unknown"
            qty = 1.0
            price = 0.0
            buyer = "Direct Buyer"
            for p in parts[1:]:
                # Extract number for qty
                m_qty = re.search(r"(\d+(?:\.\d+)?)\s*(?:parcels?|pcs?|mtrs?|bale)?", p, re.IGNORECASE)
                if m_qty and qty == 1.0:
                    try:
                        qty = float(m_qty.group(1))
                    except ValueError:
                        pass
                m_price = re.search(r"(?:rs|₹|@)?\s*(\d+(?:\.\d+)?)", p, re.IGNORECASE)
                if m_price and price == 0.0:
                    try:
                        price = float(m_price.group(1))
                    except ValueError:
                        pass
                if not re.search(r"\d", p) and len(p) > 2:
                    buyer = p

            records.append({
                "id": f"LINE-{i+1}",
                "item": item,
                "buyer": buyer,
                "quantity": qty,
                "unit": "units",
                "price": price,
                "date": str(date.today()),
                "mode": "manual_entry",
            })

        return records

    def process(self, raw_records: List[Dict[str, Any]]) -> CleaningReport:
        sanitized: List[NormalizedSaleRecord] = []
        anomalies_detected: List[Dict[str, Any]] = []
        canonical_items: Dict[str, Dict[str, Any]] = {}
        buyer_summary: Dict[str, Dict[str, Any]] = {}
        total_rev = 0.0
        total_qty = 0.0

        for r in raw_records:
            rid = str(r.get("id", ""))
            raw_item = str(r.get("item", "")).strip()
            clean_item, category = clean_item_name(raw_item)
            buyer = str(r.get("buyer", "Unknown Buyer")).strip()
            qty = float(r.get("quantity") or 0)
            unit = str(r.get("unit", "units"))
            price = float(r.get("price") or 0)
            s_date = str(r.get("date", date.today()))
            mode = str(r.get("mode", "phone"))

            item_anomalies = []
            confidence = 1.0

            # 1. Zero or negative quantity check
            if qty <= 0:
                item_anomalies.append("Zero or missing quantity/parcels.")
                qty = 1.0
                confidence *= 0.7

            # 2. Zero or outlier price check
            if price <= 0:
                item_anomalies.append("Zero or missing price. Likely sample/credit return.")
                confidence *= 0.6

            # 3. Noisy or vague item description
            if len(clean_item) < 3 or clean_item.lower() in ["item", "test", "demo", "sample", "xx"]:
                item_anomalies.append("Ambiguous or corrupted item description.")
                confidence *= 0.5

            # 4. Total amount calculation
            total_amt = round(qty * price, 2)
            total_rev += total_amt
            total_qty += qty

            record = NormalizedSaleRecord(
                raw_id=rid,
                raw_item=raw_item,
                clean_item=clean_item,
                category=category,
                buyer=buyer,
                quantity=qty,
                unit=unit,
                price=price,
                total_amount=total_amt,
                sale_date=s_date,
                order_mode=mode,
                anomalies=item_anomalies,
                confidence=round(confidence, 2),
            )
            sanitized.append(record)

            if item_anomalies:
                anomalies_detected.append({
                    "id": rid,
                    "raw_item": raw_item,
                    "cleaned": clean_item,
                    "issues": item_anomalies,
                    "confidence": record.confidence,
                })

            # Aggregations for canonical item
            if clean_item not in canonical_items:
                canonical_items[clean_item] = {
                    "item_name": clean_item,
                    "category": category,
                    "total_quantity": 0.0,
                    "total_revenue": 0.0,
                    "transaction_count": 0,
                    "prices": [],
                    "buyers": set(),
                }
            canonical_items[clean_item]["total_quantity"] += qty
            canonical_items[clean_item]["total_revenue"] += total_amt
            canonical_items[clean_item]["transaction_count"] += 1
            canonical_items[clean_item]["prices"].append(price)
            canonical_items[clean_item]["buyers"].add(buyer)

            # Buyer summary aggregation
            if buyer not in buyer_summary:
                buyer_summary[buyer] = {
                    "buyer_name": buyer,
                    "total_spend": 0.0,
                    "total_orders": 0,
                    "items_bought": set(),
                }
            buyer_summary[buyer]["total_spend"] += total_amt
            buyer_summary[buyer]["total_orders"] += 1
            buyer_summary[buyer]["items_bought"].add(clean_item)

        # Finalize aggregations (convert sets to counts/lists)
        for k, v in canonical_items.items():
            prices = v["prices"]
            v["avg_price"] = round(sum(prices) / len(prices), 2) if prices else 0.0
            v["min_price"] = min(prices) if prices else 0.0
            v["max_price"] = max(prices) if prices else 0.0
            v["buyers_count"] = len(v["buyers"])
            v["buyers"] = list(v["buyers"])[:5]

        for k, v in buyer_summary.items():
            v["items_count"] = len(v["items_bought"])
            v["items_bought"] = list(v["items_bought"])[:5]

        return CleaningReport(
            total_records=len(raw_records),
            cleaned_records=len(sanitized),
            anomalous_records=len(anomalies_detected),
            detected_anomalies=anomalies_detected,
            canonical_items=canonical_items,
            total_revenue=round(total_rev, 2),
            total_quantity=round(total_qty, 2),
            buyer_summary=buyer_summary,
            sanitized_dataset=sanitized,
        )
