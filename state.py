from pydantic import BaseModel
from typing import List, Dict, Any

class ResearchState(BaseModel):
    question: str
    sub_questions: List[str] = []
    search_results: Dict[str, Any] = {}
    final_answer: str = ""
