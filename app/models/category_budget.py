from sqlalchemy import Column, Integer, String, BigInteger
from app.database import Base


class CategoryBudget(Base):
    __tablename__ = "category_budgets"

    id              = Column(Integer, primary_key=True, index=True)
    category        = Column(String, unique=True, nullable=False)
    default_amount  = Column(BigInteger, nullable=False)   # plafond mensuel normal
    override_amount = Column(BigInteger, nullable=True)    # override ponctuel (NULL = inactif)
    override_month  = Column(Integer, nullable=True)       # YYYYMM du mois concerné
