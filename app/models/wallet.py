from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)           # ex: "Compte bancaire"
    type       = Column(String, nullable=False)           # bank | mobile_money | cash
    balance    = Column(BigInteger, default=0, nullable=False)  # en Ariary (pas de décimales)
    currency   = Column(String, default="MGA")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    transactions = relationship("Transaction", back_populates="wallet")
