from anthropic import Anthropic

from agents.base_agent import BaseAgent
from agents.codebase_agent import CodebaseAgent
from agents.api_docs_agent import ApiDocsAgent
from agents.infrastructure_agent import InfrastructureAgent
from config import ANTHROPIC_API_KEY, ROUTER_MODEL, DOMAINS

CLASSIFY_SYSTEM_PROMPT = """You are a router for a codebase Q&A system.
Classify the user's question into exactly one of these domains:
1. codebase       - source code, functions, modules, architecture
2. api_docs       - documentation, usage, setup, integration
3. infrastructure - deployment, CI/CD, config, how the project is built
4. overview       - spans multiple domains, or asks about the project as a whole

Examples:
Q: "How does the parser split python files?"      -> codebase
Q: "How do I set up my API key?"                  -> api_docs
Q: "What does the CI pipeline run?"               -> infrastructure
Q: "What does this project do?"                   -> overview
Q: "How is this project built, tested, and used?" -> overview

Reply with only one word: codebase, api_docs, infrastructure, or overview."""


class Orchestrator:

    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.agents = {
            "codebase": CodebaseAgent(),
            "api_docs": ApiDocsAgent(),
            "infrastructure": InfrastructureAgent(),
        }
        self.overview_agent = BaseAgent(
            name="OverviewAgent",
            domain=None,
            system_prompt="""You are answering a general question about this project by drawing on its code, documentation, and infrastructure 
            config together. Mention which kind of source each fact comes from when it's relevant. Keep the answer concise.""",
        )

    # Ask Haiku which domain this question belongs to
    def classify(self, question: str) -> str:
        response = self.client.messages.create(
            model=ROUTER_MODEL,
            max_tokens=20,
            system=CLASSIFY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": question}],
        )

        domain = response.content[0].text.strip().lower().strip(".,\n ")

        if domain not in DOMAINS and domain != "overview":
            domain = "overview"

        return domain

    def ask(self, question: str) -> str:
        domain = self.classify(question)
        print(f"Orchestrator routing to: {domain}")

        if domain == "overview":
            return self.overview_agent.ask(question)

        return self.agents[domain].ask(question)