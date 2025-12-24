1. Project Title -

Open Deep Researcher – A Context-Aware AI Research Assistant

2. Project Overview -

   Open Deep Researcher is an AI-powered research assistant designed to help users explore topics, analyze academic papers, and summarize documents through a conversational interface.

Core Objective -

   The main objective of this project is to build a ChatGPT-like research assistant that can:

   Answer general questions using web knowledge

   Retrieve and analyze academic research papers

   Maintain conversational context for follow-up questions

   Summarize PDFs and URLs interactively

   Store and manage chat history for reuse

Problem It Solves -

  Traditional search tools do not support:

  Context-aware follow-up questioning

  Academic paper–specific analysis

  Integrated document and URL summarization in one interface

  This project addresses these limitations by combining LLMs, search APIs, and session memory into a unified system.

3. Software and Hardware Dependencies

Software Dependencies

Programming Language

  Python 3.10+

Libraries & Frameworks

  Streamlit – User Interface

  LangChain & LangChain-Groq – LLM orchestration

  Tavily API – Academic paper search

  BeautifulSoup4 – Web content extraction

  PyPDF2 – PDF text extraction

  ReportLab – Export chat as PDF

  Requests – HTTP requests

  python-dotenv – Environment variable management

APIs Used -

  Groq API – Large Language Model inference

  Tavily API – Research paper search

Hardware Dependencies -

  Minimum 4 GB RAM

  No GPU required (cloud-based LLM inference)

  Works on standard laptops/desktops

4. Architecture Diagram

High-Level Architecture

High-Level Architecture

User
 │
 ▼
Streamlit UI
 │
 ▼
Backend Interface (Controller)
 │
 ├── General Web Mode ──► Groq LLM
 │
 ├── Academic Papers Mode
 │     ├── Tavily Search (first query only)
 │     ├── Paper Context Storage
 │     └── Follow-up handled by LLM
 │
 ├── PDF Summarizer ──► PyPDF2 + Groq
 │
 └── URL Summarizer ──► Web Scraping + Groq
 │
 ▼
Response + References
 │
 ▼
Chat History Storage (JSON)

5. Workflow

Step-by-Step Flow

   User selects a mode from the sidebar:

   General Web

   Academic Papers

   PDF Summarizer

   URL Summarizer

   User enters a query or uploads a document.

Backend processes the request:

  Determines whether it is a new query or a follow-up

  Routes the query to the correct tool or agent

  APIs and LLM are invoked as required.

  Response is generated and displayed in chat format.

  Conversation is saved in history with title, date, and time.

6. Agent Roles (Brief Explanation)

Planner

  Determines whether the query is:

  A new academic search

  A follow-up question

  A URL-based analysis

  Prevents unnecessary repeated searches.

Executor / Writer

  Uses Groq LLM to:

  Generate answers

  Summarize documents

  Analyze research papers

  Ensures answers are context-aware and concise.

Agent Pipeline

  UI → Backend Interface → Appropriate Tool (LLM / Tavily / Scraper)

  Maintains session memory for conversational continuity.

7. Sample Working Demo (Optional)

Example:

Academic Papers Mode

   User: What are recent methods for diabetes prediction?
   Assistant: (answers with references)

   User: Summarize the first paper
   Assistant: (summarizes only the first paper)

Features Demonstrated

   Context-aware follow-up

   Reference-based answering

   Academic content handling

8. Outputs / Results

The system produces:

   Conversational answers

   Academic research summaries

   Reference links to research papers

   PDF summaries (short / medium / long)

   URL content summaries

   Exportable chat history as PDF

9. Limitations

   Academic search depends on Tavily API coverage.

   Very long PDFs may be truncated due to token limits.

   Web page structure variations can affect URL extraction.

   Does not yet support multilingual input/output.

10. Future Enhancements

   User authentication and personalized history

   Support for more academic databases (Semantic Scholar, PubMed)

   Multi-file PDF analysis

   Improved citation formatting (APA/IEEE)

   Fine-grained agent reasoning with LangGraph

   Offline document indexing

11. Deployed Project Link

Live Application:
    https://infosysinternshipproject-3ysxw3lc6mkyi5iwufkyyu.streamlit.app/
