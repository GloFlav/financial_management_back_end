from pydantic import BaseModel
from datetime import datetime


class ProvisionalExpenseCreate(BaseModel):
    description: str
    amount: int
    wallet_id: int
    month: str          # format YYYY-MM
    category: str = "previsionnel"


class ProvisionalExpenseOut(ProvisionalExpenseCreate):
    id: int
    created_at: datetime
    wallet_name: str = ""

    model_config = {"from_attributes": True}
