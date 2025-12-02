from langchain_openai import ChatOpenAI
import ast

class PlannerAgent:
    def __init__(self, openai_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)

    def run(self, state):
        question = state.question

        prompt = f"""
Break the following research question into 3–5 sub-questions.
Return ONLY a Python list. No markdown, no quotes.

Question: "{question}"
"""

        response = self.llm.invoke(prompt).content

        sub_questions = ast.literal_eval(response)

        return {"sub_questions": sub_questions}
