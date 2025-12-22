import os
import re
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from tavily import TavilyClient

# ------------------ SETUP ------------------ #

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant"
)

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ------------------ GENERAL WEB ------------------ #

def general_web_answer(query: str) -> str:
    return llm.invoke(
        f"Answer clearly and simply without academic references:\n{query}"
    ).content

# ------------------ ACADEMIC MODE ------------------ #

def academic_research_answer(query: str, chat: dict):
    chat.setdefault("papers", [])

    # detect url & paper refs
    url = extract_url(query)
    refs = extract_refs(query)

    # ---------- USER PROVIDED URL ----------
    if url:
        content = fetch_url_content(url)

        if not content:
            return "Unable to read content from the provided link.", []

        paper = {
            "id": len(chat["papers"]) + 1,
            "title": "User Provided Link",
            "url": url,
            "summary": content[:1500],
            "content": content
        }

        chat["papers"].append(paper)

        return llm.invoke(f"""
Summarize the following content clearly.

Content:
{content}
""").content, [url]

    # ---------- FOLLOW-UP ----------
    if refs and chat["papers"]:
        return handle_followup(query, chat, refs), []

    # ---------- NEW SEARCH ----------
    papers = search_papers(query)
    chat["papers"] = papers

    context = ""
    links = []

    for p in papers:
        context += f"""
Paper {p['id']}
Title: {p['title']}
Abstract:
{p['summary']}
"""
        links.append(p["url"])

    prompt = f"""
Answer ONLY using the research papers below.

Question:
{query}

Papers:
{context}

Rules:
- Cite paper numbers (Paper 1, Paper 2, etc.)
- Do NOT hallucinate
- Be concise
"""

    answer = llm.invoke(prompt).content
    return answer, links

# ------------------ PAPER SEARCH ------------------ #

def search_papers(query):
    res = tavily.search(
        query=f"{query} research paper",
        max_results=3,
        search_depth="advanced"
    )

    papers = []

    for i, r in enumerate(res["results"]):
        title = r.get("title", "").strip()
        content = r.get("content", "").strip()

        summary = (
            content[:2000]
            if content
            else "Abstract not available from source."
        )

        papers.append({
            "id": i + 1,
            "title": title if title else "Title not available",
            "url": r.get("url"),
            "summary": summary,
            "content": content
        })

    return papers

# ------------------ FOLLOW-UP HANDLER ------------------ #

def handle_followup(query, chat, refs):
    papers = chat.get("papers", [])
    paper = next((p for p in papers if p["id"] in refs), None)

    if not paper:
        return "Referenced paper not found."

    q = query.lower()

    if "title" in q:
        return f"**Title:** {paper['title']}"

    if "summary" in q or "summarize" in q or "abstract" in q:
        return f"**Summary:**\n{paper['summary']}"

    if "method" in q:
        return llm.invoke(f"""
Extract ONLY the methodology from the following paper.

Paper Content:
{paper['content']}
""").content

    if "limitation" in q:
        return llm.invoke(f"""
Extract ONLY the limitations from the following paper.

Paper Content:
{paper['content']}
""").content

    if "advantage" in q or "application" in q:
        return llm.invoke(f"""
Extract ONLY applications or advantages from the following paper.

Paper Content:
{paper['content']}
""").content

    return llm.invoke(f"""
Answer ONLY using this paper.

Paper Content:
{paper['content']}

Question:
{query}
""").content

# ------------------ URL HELPERS ------------------ #

def extract_url(query):
    match = re.search(r"https?://\S+", query)
    return match.group(0) if match else None


def fetch_url_content(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        text = " ".join(p.get_text() for p in soup.find_all("p"))
        return text[:5000]
    except Exception:
        return ""

# ------------------ REFERENCE PARSER ------------------ #

def extract_refs(query):
    q = query.lower()

    if "first" in q or "1st" in q:
        return [1]
    if "second" in q or "2nd" in q:
        return [2]
    if "third" in q or "3rd" in q:
        return [3]

    return list(map(int, re.findall(r"(?:paper|reference)\s*(\d+)", q)))
