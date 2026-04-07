from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class FixedCharge(Base):
    __tablename__ = "fixed_charges"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False)
    amount       = Column(BigInteger, nullable=False)
    wallet_id    = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    day_of_month = Column(Integer, default=1)   # jour du prélèvement (1-31)
    category     = Column(String, default="charges")
    active       = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    wallet = relationship("Wallet")
