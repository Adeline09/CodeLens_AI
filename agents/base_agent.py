from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, AGENT_MODEL
from ingestion.indexer import query_collection


# Base agent that owns the query pipeline
class BaseAgent:
    N_RESULTS = 5
    SIMILARITY_THRESHOLD = None

    def __init__(self, name: str, domain: str, system_prompt: str):
        self.name = name
        self.domain = domain
        self.system_prompt = system_prompt
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

    # Searches ChromaDB for relevant chunks
    def retrieve(self, question: str) -> str:
        return query_collection(
            question,
            domain=self.domain,
            n_results=self.N_RESULTS,
            min_similarity=self.SIMILARITY_THRESHOLD,
        )

    # Calls Claude with retrieved context and returns answer
    def ask(self, question: str) -> str:
        context = self.retrieve(question)
        user_message = f"Context from the repository:\n{context}\n\nQuestion: {question}"

        message = self.client.messages.create(
            model=AGENT_MODEL,
            max_tokens=800,
            thinking={"type": "disabled"}, # Keep responses cheap and fast
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        return "".join(r.text for r in message.content if r.type == "text")