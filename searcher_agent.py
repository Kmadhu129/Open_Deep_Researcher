from tavily import TavilyClient
import os

class SearcherAgent:
    def __init__(self, tavily_key=None):
        self.client = TavilyClient(api_key=tavily_key or os.getenv("TAVILY_API_KEY"))

    def run(self, query: str):
        res = self.client.search(
            query=query,
            max_results=3,
            search_depth="advanced"
        )

        papers = []
        for r in res["results"]:
            papers.append({
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content", "")
            })
        return papers
