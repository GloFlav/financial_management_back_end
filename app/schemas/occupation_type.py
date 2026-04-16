from pydantic import BaseModel
from typing import List, Optional


class OccupationTypeCreate(BaseModel):
    name: str
    color: str = "#60a5fa"
    collaborators: List[str] = []


class OccupationTypePatch(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    collaborators: Optional[List[str]] = None


class OccupationTypeOut(BaseModel):
    id: int
    name: str
    color: str
    collaborators: List[str]

    class Config:
        from_attributes = True
