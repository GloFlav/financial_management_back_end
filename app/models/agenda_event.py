from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class AgendaEvent(Base):
    __tablename__ = "agenda_events"

    id            = Column(Integer, primary_key=True, index=True)
    date          = Column(String, nullable=False)          # YYYY-MM-DD
    hour          = Column(Float, nullable=False)           # ex: 9.5 = 9h30
    duration      = Column(Float, nullable=False, default=1)
    title         = Column(String, nullable=False)
    color         = Column(String, nullable=False, default="#60a5fa")
    occupation_id = Column(Integer, ForeignKey("occupation_types.id"), nullable=True)
    location      = Column(String, nullable=True)
    participants  = Column(Text, nullable=False, default="[]")  # JSON array
    notes         = Column(Text, nullable=True)

    occupation = relationship("OccupationType")
