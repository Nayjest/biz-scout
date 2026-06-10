import re

from anyascii import anyascii


def normalise_company_name(name: str) -> str:
    return name.lower().strip()


def collection_id(company_name: str) -> str:
    return f"company_{safe_file_name(normalise_company_name(company_name))}"


def safe_file_name(company_name: str, max_length: int = 100) -> str:
    ascii_name = anyascii(company_name)
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_name).strip("_").lower()
    slug = slug[:max_length].strip("_")
    return slug or "company"
