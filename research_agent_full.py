import os
import json
import time
import requests
from openai import OpenAI
from tavily import TavilyClient
import PyPDF2
import tempfile

# =========================================================
# Setup
# =========================================================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
MODEL = "gpt-4o-mini"

HISTORY_FILE = "history.json"


# =========================================================
# History Management
# =========================================================
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def display_history(history):
    if not history:
        print("No previous topics found.\n")
        return

    print("\n=== Previously Asked Research Topics ===")
    for i, entry in enumerate(history, 1):
        print(f"{i}. {entry['topic']}")
    print("0. None (enter a new topic)\n")


# =========================================================
# LLM Helper (WITH RATE-LIMIT DELAY)
# =========================================================
def ask_llm(system, user, tokens=350):
    # Prevent rate limit for FREE tier users
    time.sleep(20)

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=tokens,
    )
    return resp.choices[0].message.content.strip()


# =========================================================
# Convert Deep Question → Short Tavily Query
# =========================================================
def make_tavily_query(question):
    sys = (
        "Convert this complex question into a VERY short search query "
        "with only key concepts. Max 15 words. No punctuation."
    )
    return ask_llm(sys, question, tokens=25).strip()


# =========================================================
# Generate EXACTLY 3 Intellectual Sub-Questions
# =========================================================
def generate_subquestions(topic):
    system_prompt = (
        "Generate EXACTLY 3 highly intellectual, theoretical sub-questions.\n"
        "Rules:\n"
        "- Exactly 3 questions\n"
        "- Each on its own line\n"
        "- MUST NOT start with: why, what, how, when, where, do, is, can\n"
        "- Use phrasing like: To what extent…, Under what conditions…, Assuming…\n"
        "- One sentence each\n"
        "- No numbering or bullets\n"
        "- Output ONLY 3 lines"
    )

    response = ask_llm(system_prompt, f"Topic: {topic}", tokens=200)
    lines = [x.strip() for x in response.split("\n") if x.strip()]

    if len(lines) != 3:
        response = ask_llm(system_prompt, f"Regenerate. Topic: {topic}")
        lines = [x.strip() for x in response.split("\n") if x.strip()]

    return lines[:3]


# =========================================================
# Tavily Answering
# =========================================================
def answer_with_tavily(question):
    short_query = make_tavily_query(question)

    # Try QnA search
    try:
        qna = tavily.qna_search(short_query)
        if "answer" in qna:
            return qna["answer"], qna.get("sources", [])
    except:
        pass

    # Fallback search
    results = tavily.search(query=short_query, max_results=3)
    snippets, sources = [], []

    for r in results["results"]:
        snippets.append(r.get("snippet", ""))
        sources.append(r.get("url", ""))

    evidence = "\n".join(snippets)
    system_prompt = "Give a short factual answer using ONLY the evidence."
    user_prompt = f"Q: {question}\nEvidence:\n{evidence}"

    answer = ask_llm(system_prompt, user_prompt)
    return answer, sources


# =========================================================
# Safe PDF Downloader
# =========================================================
def try_download_pdf(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except:
        return None

    if resp.status_code != 200:
        return None

    # Save PDF to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(resp.content)
        path = tmp.name

    # Try reading PDF
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            if not reader.pages:
                return None

            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""

        return text

    except:
        return None


# =========================================================
# Try multiple PDFs from Tavily
# =========================================================
def find_valid_pdf(topic):
    print("\n[Searching for PDFs...]")
    results = tavily.search(query=f"{topic} pdf", max_results=10)

    for r in results["results"]:
        url = r.get("url", "")
        if ".pdf" in url.lower():
            print(f"Trying PDF: {url}")
            text = try_download_pdf(url)
            if text:
                print("✔ Valid PDF found.")
                return text

    return None


# =========================================================
# ArXiv Fallback (guaranteed open-access PDFs)
# =========================================================
def find_arxiv_pdf(topic):
    print("\n[Fallback → Searching arXiv PDFs...]")

    results = tavily.search(
        query=f"{topic} site:arxiv.org/pdf",
        max_results=5
    )

    for r in results["results"]:
        url = r.get("url", "")
        if url.endswith(".pdf"):
            print(f"Trying arXiv PDF: {url}")
            text = try_download_pdf(url)
            if text:
                print("✔ arXiv PDF found.")
                return text

    return None


# =========================================================
# Chunk-Based PDF Summary (TPM-safe)
# =========================================================
def summarize_paper(text):
    # Break PDF text into chunks (3000 characters per chunk)
    chunks = []
    chunk_size = 3000

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    chunk_summaries = []

    # Summarize each chunk individually (TPM-safe)
    for idx, chunk in enumerate(chunks):
        print(f"Summarizing chunk {idx + 1}/{len(chunks)}...")
        time.sleep(20)

        summary = ask_llm(
            "Summarize this text chunk in 3–4 sentences:",
            chunk,
            tokens=150
        )
        chunk_summaries.append(summary)

    # Combine all chunk summaries into a final structured summary
    combined_text = "\n\n".join(chunk_summaries)

    final_summary = ask_llm(
        "Combine all these summaries into a single structured research paper summary with:\n"
        "- Problem Addressed\n"
        "- Methods\n"
        "- Key Findings\n"
        "- Limitations\n"
        "- Conclusion",
        combined_text,
        tokens=400
    )

    return final_summary


# =========================================================
# Final Synthesis
# =========================================================
def combined_summary(qa_pairs, paper_summary):
    merged = "\n\n".join([f"Q: {q}\nA: {a}" for q, a in qa_pairs])
    system_prompt = "Write one coherent combined summary paragraph."
    return ask_llm(system_prompt, merged + "\n\n" + paper_summary, tokens=300)


# =========================================================
# Full Research Pipeline
# =========================================================
def run_full_agent(topic):
    print("\n=== STEP 1: Sub-questions ===\n")
    subqs = generate_subquestions(topic)
    for q in subqs:
        print(q)

    print("\n=== STEP 2: Tavily Answers ===\n")
    qa_pairs = []
    for q in subqs:
        ans, src = answer_with_tavily(q)
        qa_pairs.append((q, ans))
        print(f"Q: {q}\nA: {ans}\nSources: {src}\n")

    print("\n=== STEP 3: PDF Retrieval ===")
    text = find_valid_pdf(topic)

    if text is None:
        text = find_arxiv_pdf(topic)

    if text:
        print("\n=== STEP 4: Paper Summary ===\n")
        paper_summary = summarize_paper(text)
        print(paper_summary)
    else:
        paper_summary = "No valid research paper found."

    print("\n=== STEP 5: Final Summary ===\n")
    final = combined_summary(qa_pairs, paper_summary)
    print(final)

    return {
        "topic": topic,
        "subquestions": subqs,
        "qa_pairs": qa_pairs,
        "paper_summary": paper_summary,
        "final_summary": final
    }


# =========================================================
# PROGRAM ENTRY POINT (WITH HISTORY SYSTEM)
# =========================================================
if __name__ == "__main__":
    history = load_history()
    display_history(history)

    choice = input("Enter topic number OR 0 for new topic: ").strip()

    # Show saved data
    if choice.isdigit() and 1 <= int(choice) <= len(history):
        entry = history[int(choice) - 1]

        print("\n=== Showing Saved Research Data ===\n")

        print("=== Sub-questions ===")
        for q in entry["subquestions"]:
            print(q)
        print()

        print("=== Tavily Answers ===")
        for q, a in entry["qa_pairs"]:
            print(f"Q: {q}")
            print(f"A: {a}\n")
        print()

        print("=== Research Paper Summary ===")
        print(entry["paper_summary"])
        print()

        print("=== Final Summary ===")
        print(entry["final_summary"])
        print()

        exit()

    # New Topic
    topic = input("\nEnter new research topic: ").strip()
    result = run_full_agent(topic)
    history.append(result)
    save_history(history)
    print("\n✔ Research saved to history.")
