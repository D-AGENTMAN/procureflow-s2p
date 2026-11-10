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
