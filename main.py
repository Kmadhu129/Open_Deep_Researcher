import os
from state import ResearchState
from graph.research_graph import create_research_graph

def main():
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    graph = create_research_graph(openai_key, tavily_key)

    question = input("Enter research question: ")

    state = ResearchState(question=question)

    result = graph.invoke(state)

    print("\n===== FINAL ANSWER =====\n")
    print(result["final_answer"])

if __name__ == "__main__":
    main()
