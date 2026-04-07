from pydantic import BaseModel
from datetime import datetime

class WalletBase(BaseModel):
    name: str
    type: str
    balance: int
    currency: str = "MGA"

class WalletCreate(WalletBase):
    pass

class WalletOut(WalletBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
