import ast
import os
import re

from ingestion.domain_map import get_domain_for_extension

LINE_CHUNK_SIZE = 50


# Direct to the right chunk function
def parse_file(filepath: str) -> list[dict] | None:
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()

    domain = get_domain_for_extension(ext)
    if domain is None:
        return None

    content = _read_text(filepath)
    if content is None:
        return None

    if ext == ".py":
        return _chunk_python(content, filename, filepath, domain)
    if ext == ".md":
        return _chunk_markdown(content, filename, filepath, domain)

    return _chunk_by_lines(content, filename, filepath, domain, ext)


# Split by function
def _chunk_python(content: str, filename: str, filepath: str, domain: str) -> list[dict]:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return [_make_chunk(content, filename, filepath, ".py", domain, 0)]

    lines = content.splitlines()
    top_level = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]

    if not top_level:
        return [_make_chunk(content, filename, filepath, ".py", domain, 0)]

    chunks = []
    for i, node in enumerate(top_level):
        start = node.lineno - 1
        end = top_level[i + 1].lineno - 1 if i + 1 < len(top_level) else len(lines)
        chunk_content = "\n".join(lines[start:end]).strip()
        if chunk_content:
            chunks.append(_make_chunk(chunk_content, filename, filepath, ".py", domain, i))

    return chunks


# Split at headings
def _chunk_markdown(content: str, filename: str, filepath: str, domain: str) -> list[dict]:
    sections = re.split(r"(?=^#{1,6}\s)", content, flags=re.MULTILINE)
    chunks = []
    for i, section in enumerate(s for s in sections if s.strip()):
        chunks.append(_make_chunk(section.strip(), filename, filepath, ".md", domain, i))
    return chunks or [_make_chunk(content, filename, filepath, ".md", domain, 0)]


# Split by line count
def _chunk_by_lines(content: str, filename: str, filepath: str, domain: str, ext: str) -> list[dict]:
    lines = content.splitlines()
    chunks = []
    for i in range(0, len(lines), LINE_CHUNK_SIZE):
        chunk_content = "\n".join(lines[i:i + LINE_CHUNK_SIZE])
        if chunk_content.strip():
            chunks.append(_make_chunk(chunk_content, filename, filepath, ext, domain, i // LINE_CHUNK_SIZE))
    return chunks


# Build one chunk
def _make_chunk(content: str, filename: str, filepath: str, extension: str, domain: str, chunk_index: int) -> dict:
    header = f"File: {filename} | Domain: {domain}"
    return {
        "content": f"{header}\n{content}",
        "metadata": {
            "filename": filename,
            "filepath": filepath,
            "extension": extension,
            "domain": domain,
            "chunk_index": chunk_index,
        },
    }


def _read_text(filepath: str) -> str | None:
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
            return file.read()
    except Exception:
        return None
