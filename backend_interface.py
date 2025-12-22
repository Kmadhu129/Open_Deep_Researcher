from research_engine import (
    general_web_answer,
    academic_research_answer
)

def run_research(query, chat, mode):
    if mode == "General Web":
        return general_web_answer(query), []

    if mode == "Academic Papers":
        return academic_research_answer(query, chat)

    return "Invalid mode selected.", []
