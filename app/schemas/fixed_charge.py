from pydantic import BaseModel
from datetime import datetime


class FixedChargeCreate(BaseModel):
    name: str
    amount: int
    wallet_id: int
    day_of_month: int = 1
    category: str = "charges"


class FixedChargeOut(FixedChargeCreate):
    id: int
    active: bool
    created_at: datetime
    wallet_name: str = ""

    model_config = {"from_attributes": True}
