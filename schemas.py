"""
Database Schemas for 3ersi.ai (AI Wedding Planner)

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercase of the class name (e.g., Vendor -> "vendor").
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, EmailStr

Region = Literal["lebanon", "gcc", "egypt"]
Currency = Literal["USD", "LBP", "AED", "SAR", "EGP"]

class User(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: Optional[str] = None  # write-only on input

class UserPublic(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserPreference(BaseModel):
    full_name: str = Field(..., description="Couple or user's full name")
    email: str = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone (optional)")
    region: Region = Field(..., description="Primary market/region")
    city: Optional[str] = Field(None, description="Preferred city")
    wedding_date: Optional[str] = Field(None, description="Target date (ISO or text)")
    guest_count: int = Field(..., ge=1, le=2000)
    style: Optional[str] = Field(None, description="Wedding style e.g. classic, boho, luxury")
    budget: float = Field(..., ge=0)
    currency: Currency = Field("USD")

class Vendor(BaseModel):
    name: str
    category: Literal[
        "venue", "planner", "photography", "videography", "catering",
        "music", "zaffe", "makeup", "hair", "florals", "decor",
        "lighting", "dj", "band", "cake", "stationery", "transport"
    ]
    region: Region
    city: Optional[str] = None
    description: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    price_tier: Literal["$, $$, $$$, $$$$"] = "$$"
    average_price_usd: Optional[float] = Field(None, ge=0)
    capacity: Optional[int] = Field(None, ge=1)
    images: List[str] = Field(default_factory=list)
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    instagram: Optional[str] = None
    featured: bool = False

class Venue(BaseModel):
    name: str
    region: Region
    city: Optional[str] = None
    capacity: int = Field(..., ge=10)
    indoor: bool = True
    outdoor: bool = False
    sea_view: bool = False
    luxury_level: Literal["boutique", "premium", "ultra"] = "premium"
    average_price_usd: Optional[float] = Field(None, ge=0)
    images: List[str] = Field(default_factory=list)

class Package(BaseModel):
    vendor_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    items: List[str] = Field(default_factory=list)
    price_usd: float = Field(..., ge=0)

class Inquiry(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    vendor_id: Optional[str] = None
    message: str
    region: Optional[Region] = None

class ChecklistItem(BaseModel):
    label: str
    category: Literal[
        "planning", "venue", "attire", "beauty", "decor", "florals", "media",
        "entertainment", "food", "logistics", "paperwork", "traditions"
    ]
    due_months_before: int = Field(..., ge=0, le=24)
    optional: bool = False

class WeddingPlan(BaseModel):
    preference_id: Optional[str] = None
    region: Region
    currency: Currency
    guest_count: int
    total_budget: float
    timeline: List[dict] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)

class BudgetItem(BaseModel):
    category: str
    allocation_percent: float
    amount: float
    notes: Optional[str] = None

class PlanCreate(BaseModel):
    title: Optional[str] = None
    data: dict

class PlanPublic(BaseModel):
    id: str
    title: Optional[str] = None
    data: dict
