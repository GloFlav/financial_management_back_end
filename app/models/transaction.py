from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id          = Column(Integer, primary_key=True, index=True)
    type        = Column(String, nullable=False)      # income | expense
    amount      = Column(BigInteger, nullable=False)  # en Ariary
    category    = Column(String, nullable=False)      # alimentation | transport | salaire | ...
    description = Column(Text, nullable=True)
    wallet_id   = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    date        = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    attachment  = Column(Text, nullable=True)         # base64 PDF/image ou null

    wallet = relationship("Wallet", back_populates="transactions")
