from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class ProvisionalExpense(Base):
    __tablename__ = "provisional_expenses"

    id          = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount      = Column(BigInteger, nullable=False)
    wallet_id   = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    month       = Column(String, nullable=False)   # format YYYY-MM
    category    = Column(String, default="previsionnel")
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    wallet = relationship("Wallet")
