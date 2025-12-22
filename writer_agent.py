from langchain_groq import ChatGroq
import os

class WriterAgent:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant"
        )

    def generate(self, messages):
        return self.llm.invoke(messages).content
