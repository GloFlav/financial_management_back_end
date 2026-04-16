from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class OccupationType(Base):
    __tablename__ = "occupation_types"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    color         = Column(String, nullable=False, default="#60a5fa")
    collaborators = Column(Text, nullable=False, default="[]")  # JSON array of names
