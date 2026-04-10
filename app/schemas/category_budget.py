from pydantic import BaseModel
from typing import Optional


class CategoryBudgetCreate(BaseModel):
    category:       str
    default_amount: int


class CategoryBudgetPatch(BaseModel):
    default_amount:  Optional[int] = None
    override_amount: Optional[int] = None   # 0 = désactiver l'override
    override_month:  Optional[int] = None   # YYYYMM


class CategoryBudgetOut(BaseModel):
    category:        str
    default_amount:  int
    override_amount: Optional[int] = None
    override_month:  Optional[int] = None
    effective_limit: int
    spent:           int
    ratio:           float

    model_config = {"from_attributes": True}
