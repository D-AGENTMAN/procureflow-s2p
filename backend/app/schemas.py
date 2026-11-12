from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SourcingProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=160)
    category: str = Field(min_length=2, max_length=100)
    owner: str = Field(min_length=2, max_length=120)
    estimated_budget: float = Field(ge=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    description: str = Field(default="", max_length=2000)


class SourcingProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_code: str
    name: str
    category: str
    owner: str
    estimated_budget: float
    currency: str
    status: str
    description: str
    created_at: datetime


class SourcingProjectUpdate(SourcingProjectCreate):
    status: str = Field(min_length=2, max_length=30)


class SupplierCreate(BaseModel):
    supplier_code: str = Field(min_length=3, max_length=30)
    name: str = Field(min_length=2, max_length=160)
    category: str = Field(min_length=2, max_length=100)
    city: str = Field(default="", max_length=100)
    country: str = Field(default="India", max_length=100)
    contact_person: str = Field(default="", max_length=120)
    email: str = Field(default="", max_length=160)
    status: str = Field(default="Active", max_length=30)


class SupplierRead(SupplierCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_demo: bool
    created_at: datetime


class QuotationCreate(BaseModel):
    project_id: int = Field(gt=0)
    supplier_id: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    moq: int = Field(ge=1)
    lead_time_days: int = Field(ge=0)
    payment_terms: str = Field(default="", max_length=100)
    validity_days: int = Field(default=30, ge=1)
    remarks: str = Field(default="", max_length=2000)


class QuotationRead(QuotationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_demo: bool
    created_at: datetime


class AwardCreate(BaseModel):
    project_id: int = Field(gt=0)
    quotation_id: int = Field(gt=0)
    awarded_price: float = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    justification: str = Field(min_length=10, max_length=2000)


class AwardRead(AwardCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_demo: bool
    awarded_at: datetime


class BidComparisonRead(BaseModel):
    quotation_id: int
    supplier_id: int
    supplier_name: str
    unit_price: float
    currency: str
    moq: int
    lead_time_days: int
    payment_terms: str
    validity_days: int
    price_rank: int
    moq_rank: int
    lead_time_rank: int
    overall_rank: int
