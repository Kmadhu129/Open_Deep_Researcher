from pydantic import BaseModel
from typing import List

class ResearchState(BaseModel):
    query: str
    context: str
    mode: str
    references: List[str] = []
