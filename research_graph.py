from langgraph.graph import StateGraph, END
from agents.planner_agent import PlannerAgent
from agents.searcher_agent import SearcherAgent
from agents.writer_agent import WriterAgent
from state import ResearchState

def create_research_graph(openai_key, tavily_key):
    planner = PlannerAgent(openai_key)
    searcher = SearcherAgent(tavily_key)
    writer = WriterAgent(openai_key)

    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner.run)
    graph.add_node("searcher", searcher.run)
    graph.add_node("writer", writer.run)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "searcher")
    graph.add_edge("searcher", "writer")
    graph.add_edge("writer", END)

    return graph.compile()
