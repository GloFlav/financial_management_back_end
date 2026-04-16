from pydantic import BaseModel
from typing import List, Optional


class AgendaEventCreate(BaseModel):
    date: str                       # YYYY-MM-DD
    hour: float                     # ex: 9.5 = 9h30
    duration: float = 1
    title: str
    color: str = "#60a5fa"
    occupation_id: Optional[int] = None
    location: Optional[str] = None
    participants: List[str] = []
    notes: Optional[str] = None


class AgendaEventPatch(BaseModel):
    date: Optional[str] = None
    hour: Optional[float] = None
    duration: Optional[float] = None
    title: Optional[str] = None
    color: Optional[str] = None
    occupation_id: Optional[int] = None
    location: Optional[str] = None
    participants: Optional[List[str]] = None
    notes: Optional[str] = None


class AgendaEventOut(BaseModel):
    id: int
    date: str
    hour: float
    duration: float
    title: str
    color: str
    occupation_id: Optional[int]
    location: Optional[str]
    participants: List[str]
    notes: Optional[str]

    class Config:
        from_attributes = True
