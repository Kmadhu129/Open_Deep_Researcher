import streamlit as st
import os
from history_manager import load_history, save_history, new_chat
from backend_interface import run_research
from summarizers.pdf_summarizer import run_pdf_summary
from summarizers.url_summarizer import run_url_summary
from export_chat import export_chat_to_pdf

st.set_page_config(page_title="Open Deep Researcher", layout="wide")


def main():
    history = load_history()

    if "chat_id" not in st.session_state:
        st.session_state.chat_id = history[0]["id"] if history else new_chat()

    history = load_history()
    chat = next(c for c in history if c["id"] == st.session_state.chat_id)

    # ---- SAFETY DEFAULTS ----
    chat.setdefault("title", "New Chat")
    chat.setdefault("created_at", "")
    chat.setdefault("mode", "General Web")
    chat.setdefault("messages", [])
    chat.setdefault("papers", [])

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.title("🧠 Open Deep Researcher")

        if st.button("➕ New Chat"):
            st.session_state.chat_id = new_chat()
            st.rerun()

        # ✅ EXPORT CHAT AS PDF (SAFE ADDITION)
        if st.button("📄 Export Chat as PDF"):
            filename = f"chat_{chat['id']}.pdf"
            export_chat_to_pdf(chat, filename)
            st.success("Chat exported successfully!")
            st.download_button(
                label="⬇ Download PDF",
                data=open(filename, "rb"),
                file_name=filename,
                mime="application/pdf"
            )

        st.subheader("Chat History")

        for c in history:
            title = c.get("title", "New Chat")
            time = c.get("created_at", "")
            label = f"{time} — {title}" if time else title

            if st.button(label, key=c["id"]):
                st.session_state.chat_id = c["id"]
                st.rerun()

        st.divider()

        tool = st.radio(
            "Choose Tool",
            ["Research Assistant", "PDF Summarizer", "URL Summarizer"]
        )

        if tool == "Research Assistant":
            chat["mode"] = st.radio(
                "Search Focus",
                ["General Web", "Academic Papers"],
                index=0 if chat["mode"] == "General Web" else 1
            )

    # ---------- MAIN ----------
    st.title(tool)

    # ---------- RESEARCH CHAT ----------
    if tool == "Research Assistant":
        for m in chat["messages"]:
            st.chat_message(m["role"]).markdown(m["content"])

        query = st.chat_input("Ask your question")
        if query:
            chat["messages"].append({"role": "user", "content": query})

            answer, refs = run_research(query, chat, chat["mode"])

            response = answer
            if refs:
                response += "\n\n### References\n"
                for r in refs:
                    response += f"- {r}\n"

            chat["messages"].append({
                "role": "assistant",
                "content": response
            })

            if chat["title"] == "New Chat":
                chat["title"] = query[:50]

            save_history(history)
            st.rerun()

    # ---------- PDF SUMMARIZER ----------
    elif tool == "PDF Summarizer":
        length = st.radio("Summary Length", ["Short", "Medium", "Long"])
        pdf = st.file_uploader("Upload PDF", type=["pdf"])

        if pdf:
            summary = run_pdf_summary(pdf, length)
            st.write(summary)

    # ---------- URL SUMMARIZER ----------
    elif tool == "URL Summarizer":
        length = st.radio("Summary Length", ["Short", "Medium", "Long"])
        url = st.text_input("Enter URL")

        if url:
            summary = run_url_summary(url, length)
            st.write(summary)


if __name__ == "__main__":
    main()
