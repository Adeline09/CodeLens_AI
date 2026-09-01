DOMAIN_BY_EXTENSION = {
    ".py": "codebase",
    ".md": "api_docs",
    ".yml": "infrastructure",
    ".yaml": "infrastructure",
}


def get_domain_for_extension(extension: str) -> str | None:
    return DOMAIN_BY_EXTENSION.get(extension)
