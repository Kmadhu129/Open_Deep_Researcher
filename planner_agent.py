class PlannerAgent:
    def run(self, state):
        return {
            "query": state.query,
            "mode": state.mode
        }
