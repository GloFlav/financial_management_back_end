from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone
from app.database import Base


class ActionLog(Base):
    __tablename__ = "action_logs"

    id          = Column(Integer, primary_key=True, index=True)
    timestamp   = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    prompt      = Column(Text,     nullable=True)
    ai_response = Column(Text,     nullable=True)
    action_type = Column(String(64), nullable=True)
    action_data = Column(Text,     nullable=True)   # JSON string
    result      = Column(String(32), nullable=True) # auto / pending_confirm / error
