from agents.base_agent import BaseAgent


# Agent that answers infrastructure questions
class InfrastructureAgent(BaseAgent):
    N_RESULTS = 3

    def __init__(self):
        super().__init__(
            name="InfrastructureAgent",
            domain="infrastructure",
            system_prompt="""You are a DevOps engineer answering questions about how this project is built, tested, and deployed.
Reference specific pipeline steps or config values from the context given.""",
        )
