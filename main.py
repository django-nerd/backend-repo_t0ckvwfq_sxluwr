import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import (
    UserPreference, Vendor, Venue, Package, Inquiry, ChecklistItem, WeddingPlan, BudgetItem
)

app = FastAPI(title="3ersi.ai API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "3ersi.ai backend running", "version": "1.0.0"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from 3ersi.ai backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ---------- Utility: Schema Introspection ----------
class SchemaInfo(BaseModel):
    name: str
    fields: Dict[str, Any]


@app.get("/schema", response_model=List[SchemaInfo])
def get_schema():
    """Expose simplified schema info for collections."""
    def model_fields(model: Any) -> Dict[str, Any]:
        return {k: str(v.annotation) for k, v in model.model_fields.items()}

    return [
        SchemaInfo(name="userpreference", fields=model_fields(UserPreference)),
        SchemaInfo(name="vendor", fields=model_fields(Vendor)),
        SchemaInfo(name="venue", fields=model_fields(Venue)),
        SchemaInfo(name="package", fields=model_fields(Package)),
        SchemaInfo(name="inquiry", fields=model_fields(Inquiry)),
        SchemaInfo(name="checklistitem", fields=model_fields(ChecklistItem)),
        SchemaInfo(name="weddingplan", fields=model_fields(WeddingPlan)),
        SchemaInfo(name="budgetitem", fields=model_fields(BudgetItem)),
    ]


# ---------- Seed Sample Vendors (idempotent) ----------
@app.post("/api/seed/vendors")
def seed_vendors():
    samples = [
        {
            "name": "Phoenicia Beirut",
            "category": "venue",
            "region": "lebanon",
            "city": "Beirut",
            "description": "Iconic luxury hotel venue with sea views",
            "languages": ["Arabic", "English", "French"],
            "price_tier": "$$$$",
            "average_price_usd": 50000,
            "capacity": 600,
            "images": ["https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?q=80&w=1200"],
            "instagram": "@phoeniciabeirut",
            "featured": True
        },
        {
            "name": "Byblos Sur Mer",
            "category": "venue",
            "region": "lebanon",
            "city": "Byblos",
            "description": "Historic seaside venue in Jbeil",
            "languages": ["Arabic", "English", "French"],
            "price_tier": "$$$",
            "average_price_usd": 25000,
            "capacity": 300,
            "images": ["https://images.unsplash.com/photo-1496412705862-e0088f16f791?q=80&w=1200"],
            "featured": True
        },
        {
            "name": "Burj Al Arab Events",
            "category": "venue",
            "region": "gcc",
            "city": "Dubai",
            "description": "Ultra-luxury Dubai wedding experiences",
            "languages": ["Arabic", "English"],
            "price_tier": "$$$$",
            "average_price_usd": 150000,
            "capacity": 300,
            "images": ["https://images.unsplash.com/photo-1528909514045-2fa4ac7a08ba?q=80&w=1200"],
            "featured": True
        },
        {
            "name": "Four Seasons Cairo",
            "category": "venue",
            "region": "egypt",
            "city": "Cairo",
            "description": "Luxury Nile-side celebrations",
            "languages": ["Arabic", "English"],
            "price_tier": "$$$",
            "average_price_usd": 40000,
            "capacity": 500,
            "images": ["https://images.unsplash.com/photo-1528715471579-d1bcf0ba5e83?q=80&w=1200"],
            "featured": True
        },
        {
            "name": "Maison de Fleurs",
            "category": "florals",
            "region": "lebanon",
            "city": "Beirut",
            "description": "Lavish floral design studio",
            "languages": ["Arabic", "English", "French"],
            "price_tier": "$$$",
            "average_price_usd": 8000,
            "images": ["https://images.unsplash.com/photo-1464965911861-746a04b4bca6?q=80&w=1200"],
            "featured": True
        },
        {
            "name": "Zaffe Arabia",
            "category": "zaffe",
            "region": "gcc",
            "city": "Riyadh",
            "description": "Traditional zaffe troupes across GCC",
            "languages": ["Arabic"],
            "price_tier": "$$",
            "average_price_usd": 3000,
            "images": ["https://images.unsplash.com/photo-1558981403-c5f9899a28bc?q=80&w=1200"],
            "featured": True
        },
        {
            "name": "Nile Moments Photography",
            "category": "photography",
            "region": "egypt",
            "city": "Cairo",
            "description": "Artful wedding photography in Egypt",
            "languages": ["Arabic", "English"],
            "price_tier": "$$",
            "average_price_usd": 3500,
            "images": ["https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=1200"],
            "featured": True
        },
    ]

    created = 0
    for s in samples:
        existing = db["vendor"].find_one({"name": s["name"], "region": s["region"]})
        if not existing:
            db["vendor"].insert_one({**s})
            created += 1

    return {"seeded": created, "total_vendors": db["vendor"].count_documents({})}


# ---------- Vendor Endpoints ----------
@app.get("/api/vendors")
def list_vendors(
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    featured: Optional[bool] = Query(None),
    limit: int = 50,
):
    filter_q: Dict[str, Any] = {}
    if region:
        filter_q["region"] = region
    if category:
        filter_q["category"] = category
    if featured is not None:
        filter_q["featured"] = featured

    vendors = get_documents("vendor", filter_q, limit)
    for v in vendors:
        v["_id"] = str(v.get("_id"))
    return {"items": vendors}


class PreferenceCreate(UserPreference):
    pass


@app.post("/api/preferences")
def create_preferences(pref: PreferenceCreate):
    pref_id = create_document("userpreference", pref)
    return {"id": pref_id}


# ---------- AI-like Plan Generation (rule-based) ----------
class PlanRequest(UserPreference):
    pass


def arabic_checklist(guest_count: int) -> List[Dict[str, Any]]:
    base: List[ChecklistItem] = [
        ChecklistItem(label="حددوا الميزانية الكاملة", category="planning", due_months_before=12),
        ChecklistItem(label="اختيار القاعة أو المكان", category="venue", due_months_before=11),
        ChecklistItem(label="حجز الفرقة أو الدي جي", category="entertainment", due_months_before=9),
        ChecklistItem(label="تصميم الزينة والورود", category="florals", due_months_before=6),
        ChecklistItem(label="حجز الزفة", category="entertainment", due_months_before=5, optional=True),
        ChecklistItem(label="التصوير والفيديو", category="media", due_months_before=7),
        ChecklistItem(label="الدعوات والبطاقات", category="paperwork", due_months_before=3),
        ChecklistItem(label="بروفة نهائية وجدول اليوم الكبير", category="logistics", due_months_before=1),
    ]
    # Adjust based on size
    if guest_count > 300:
        base.append(ChecklistItem(label="تأكيد ترتيبات خدمة صف السيارات", category="logistics", due_months_before=2))
    return [item.model_dump() for item in base]


def regional_allocations(region: str) -> Dict[str, float]:
    # Percent allocation by category (should sum roughly to 100)
    if region == "gcc":
        return {
            "venue": 30, "catering": 20, "decor": 12, "florals": 8, "media": 8,
            "entertainment": 10, "beauty": 4, "attire": 4, "stationery": 2, "misc": 2
        }
    if region == "egypt":
        return {
            "venue": 22, "catering": 25, "decor": 10, "florals": 6, "media": 8,
            "entertainment": 8, "beauty": 5, "attire": 5, "stationery": 3, "misc": 3
        }
    # lebanon default
    return {
        "venue": 28, "catering": 22, "decor": 12, "florals": 8, "media": 8,
        "entertainment": 8, "beauty": 5, "attire": 5, "stationery": 2, "misc": 2
    }


def build_budget(total: float, region: str) -> List[BudgetItem]:
    alloc = regional_allocations(region)
    items: List[BudgetItem] = []
    for cat, pct in alloc.items():
        amount = round(total * (pct / 100.0), 2)
        items.append(BudgetItem(category=cat, allocation_percent=pct, amount=amount))
    return items


def recommend_vendors(region: str, categories: List[str], limit_per_cat: int = 3) -> Dict[str, List[Dict[str, Any]]]:
    recs: Dict[str, List[Dict[str, Any]]] = {}
    for cat in categories:
        docs = list(db["vendor"].find({"region": region, "category": cat}).limit(limit_per_cat)) if db else []
        # Fallback to any region if none found
        if not docs:
            docs = list(db["vendor"].find({"category": cat}).limit(limit_per_cat)) if db else []
        for d in docs:
            d["_id"] = str(d.get("_id"))
        recs[cat] = docs
    return recs


@app.post("/api/plan")
def generate_plan(req: PlanRequest):
    # Persist preferences first
    pref_id = create_document("userpreference", req)

    # Timeline heuristic
    checklist = arabic_checklist(req.guest_count)

    # Budget breakdown
    budget_items = [bi.model_dump() for bi in build_budget(req.budget, req.region)]

    # Vendor recommendations by key categories
    key_cats = ["venue", "photography", "florals", "zaffe", "dj"]
    vendor_recs = recommend_vendors(req.region, key_cats)

    plan: Dict[str, Any] = {
        "preference_id": pref_id,
        "region": req.region,
        "currency": req.currency,
        "guest_count": req.guest_count,
        "total_budget": req.budget,
        "timeline": checklist,
        "categories": key_cats,
    }

    return {
        "plan": plan,
        "budget": budget_items,
        "vendors": vendor_recs,
        "message": "Plan generated using regional best-practice heuristics"
    }


# ---------- Inquiries ----------
@app.post("/api/inquiries")
def create_inquiry(inq: Inquiry):
    inq_id = create_document("inquiry", inq)
    return {"id": inq_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
