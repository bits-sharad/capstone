from __future__ import annotations

import re
from urllib.parse import urlparse
from typing import Any, Dict, List, Tuple

from Project.state import ProductData


_URL_REGEX = re.compile(
    r"^(https?://)"
    r"(([A-Za-z0-9-]+\.)+[A-Za-z]{2,63})"  # domain
    r"(:\d{1,5})?"  # optional port
    r"(/.*)?$"  # path
)


def validate_url(url: str) -> bool:
    """
    Very small helper to validate that a string looks like a URL.
    This is intentionally lightweight – just enough for quality checks.
    """
    if not url or not isinstance(url, str):
        return False

    if not _URL_REGEX.match(url):
        return False

    parts = urlparse(url)
    return bool(parts.scheme in {"http", "https"} and parts.netloc)


def validate_product_data(product: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Basic validation for required product fields before running quality checks.
    Returns (is_valid, errors).
    """
    errors: List[str] = []

    if not product:
        return False, ["Product data is missing."]

    title = product.get("title")
    description = product.get("description")
    price = product.get("price")
    category = product.get("category")
    images = product.get("images")

    if not title or not isinstance(title, str):
        errors.append("Product title is required.")
    if not description or not isinstance(description, str):
        errors.append("Product description is required.")
    if price is None:
        errors.append("Product price is required.")
    else:
        try:
            if float(price) <= 0:
                errors.append("Product price must be greater than 0.")
        except (TypeError, ValueError):
            errors.append("Product price must be a valid number.")
    if not category or not isinstance(category, str):
        errors.append("Product category is required.")
    if images is None or not isinstance(images, list) or not images:
        errors.append("At least one product image is required.")

    return len(errors) == 0, errors

from __future__ import annotations

import re
from urllib.parse import urlparse


_URL_REGEX = re.compile(
    r"^(https?://)"
    r"(([A-Za-z0-9-]+\.)+[A-Za-z]{2,63})"  # domain
    r"(:\d{1,5})?"  # optional port
    r"(/.*)?$"  # path
)


def validate_url(url: str) -> bool:
    """
    Very small helper to validate that a string looks like a URL.
    This is intentionally lightweight – just enough for quality checks.
    """
    if not url or not isinstance(url, str):
        return False

    if not _URL_REGEX.match(url):
        return False

    parts = urlparse(url)
    return bool(parts.scheme in {"http", "https"} and parts.netloc)

