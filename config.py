import os
from dotenv import load_dotenv

load_dotenv()

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ROUTER_MODEL = "claude-haiku-4-5"
AGENT_MODEL = "claude-sonnet-5"

# Vector store
CHROMA_DB_PATH = "./chroma_db"

# Domains
DOMAINS = ["codebase", "api_docs", "infrastructure"]

# Indexed project
PROJECT_NAME = "codelens_ai"
PROJECT_ROOT = os.getenv("PROJECT_ROOT", ".")
