from agents.base_agent import BaseAgent


# Agent that answers codebase questions
class CodebaseAgent(BaseAgent):
    N_RESULTS = 8
    SIMILARITY_THRESHOLD = 0.05   # Needs tuning against more query results

    def __init__(self):
        super().__init__(
            name="CodebaseAgent",
            domain="codebase",
            system_prompt="""You are a senior engineer explaining this codebase to another developer.
Explain what the code does, how pieces connect, and flag anything that looks off.
Reference specific files and functions from the context. Keep answers concise and technical.""",
        )
