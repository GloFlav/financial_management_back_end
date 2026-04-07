from sqlalchemy import Column, Integer, String, BigInteger
from app.database import Base


class UserSetting(Base):
    __tablename__ = "user_settings"

    id    = Column(Integer, primary_key=True)
    key   = Column(String, unique=True, nullable=False)
    value = Column(BigInteger, nullable=False)
