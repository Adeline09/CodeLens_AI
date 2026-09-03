import os

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from config import CHROMA_DB_PATH, DOMAINS, PROJECT_NAME, PROJECT_ROOT
from ingestion.parser import parse_file

SKIP_DIRS = {".git", "venv", ".venv", "__pycache__", "chroma_db", ".pytest_cache", "node_modules"}
BATCH_SIZE = 100

_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
_embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")


# Get domain's collection
def get_collection(domain: str):
    name = f"{PROJECT_NAME}_{domain}"
    return _client.get_or_create_collection(
        name=name,
        embedding_function=_embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )


# Walk the repo and index every file
def index_project(root_path: str = PROJECT_ROOT) -> dict:
    chunks_by_domain = {domain: [] for domain in DOMAINS}

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            chunks = parse_file(filepath)
            if not chunks:
                continue
            for chunk in chunks:
                chunks_by_domain[chunk["metadata"]["domain"]].append((filepath, chunk))

    counts = {}
    for domain, items in chunks_by_domain.items():
        collection = get_collection(domain)

        if collection.count() > 0 or not items:
            counts[domain] = collection.count()
            continue

        ids, documents, metadatas = [], [], []
        for filepath, chunk in items:
            rel_path = os.path.relpath(filepath, root_path)
            ids.append(f"{rel_path}::chunk_{chunk['metadata']['chunk_index']}")
            documents.append(chunk["content"])
            metadatas.append(chunk["metadata"])

        # Add chunks to ChromaDB
        for i in range(0, len(ids), BATCH_SIZE):
            collection.add(
                ids=ids[i:i + BATCH_SIZE],
                documents=documents[i:i + BATCH_SIZE],
                metadatas=metadatas[i:i + BATCH_SIZE],
            )

        counts[domain] = len(ids)

    return counts


# Search one domain, or all domains for "overview" questions
def query_collection(question: str, domain: str = None, n_results: int = 5, min_similarity: float = None) -> str:
    domains_to_search = DOMAINS if domain is None else [domain]

    results = []
    for d in domains_to_search:
        collection = get_collection(d)
        if collection.count() == 0:
            continue
        r = collection.query(query_texts=[question], n_results=n_results)
        for doc, meta, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0]):
            if min_similarity is not None and (1 - dist) < min_similarity:
                continue
            results.append((dist, doc, meta))

    if domain is None:
        results.sort(key=lambda x: x[0])
        results = results[:n_results]

    return "\n".join(doc for _, doc, _ in results)
