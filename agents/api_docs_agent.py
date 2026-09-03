from agents.base_agent import BaseAgent


# Agent that answers API questions
class ApiDocsAgent(BaseAgent):
    N_RESULTS = 3

    def __init__(self):
        super().__init__(
            name="ApiDocsAgent",
            domain="api_docs",
            system_prompt="""You are a technical writer answering questions about this project's documentation.
Explain how to use, set up, or integrate with the project based on the docs given.
If the docs don't cover something, say so instead of guessing.""",
        )
