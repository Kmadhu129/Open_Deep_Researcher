from langchain_openai import ChatOpenAI

class WriterAgent:
    def __init__(self, openai_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)

    def run(self, state):
        prompt = f"""
Write a clean, structured research summary.

Main Question:
{state.question}

Sub Questions:
{state.sub_questions}

Search Results:
{state.search_results}

Write a final consolidated answer.
"""

        answer = self.llm.invoke(prompt).content
        return {"final_answer": answer}
