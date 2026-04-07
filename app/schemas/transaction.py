from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TransactionCreate(BaseModel):
    type: str          # income | expense
    amount: int        # en Ariary
    category: str
    description: Optional[str] = None
    wallet_id: int
    date: Optional[datetime] = None
    attachment: Optional[str] = None   # base64 facultatif

class TransactionOut(BaseModel):
    id: int
    type: str
    amount: int
    category: str
    description: Optional[str]
    wallet_id: int
    date: datetime
    wallet_name: str = ""
    attachment: Optional[str] = None

    model_config = {"from_attributes": True}
