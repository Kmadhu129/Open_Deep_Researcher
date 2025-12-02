from tavily import TavilyClient

class SearcherAgent:
    def __init__(self, tavily_key):
        self.client = TavilyClient(api_key=tavily_key)

    def run(self, state):
        results = {}

        for q in state.sub_questions:
            data = self.client.search(q, max_results=5)
            results[q] = data

        return {"search_results": results}
