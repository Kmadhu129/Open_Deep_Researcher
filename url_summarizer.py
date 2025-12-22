import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
import os

llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"))

def run_url_summary(url, length):
    html = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    text = " ".join(p.get_text() for p in soup.find_all("p"))

    return llm.invoke(
        f"Give a {length.lower()} summary:\n{text}"
    ).content
