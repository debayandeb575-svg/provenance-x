from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import fitz


TOKEN_PATTERN = re.compile(r"^[0-9a-fA-F]{16,128}$")


def _normalise_token(value: Any) -> str:
    if value is None:
        return ""

    value = str(value).strip()

    if TOKEN_PATTERN.fullmatch(value):
        return value.lower()

    return ""


def extract_from_pdf(pdf_path: str | Path) -> dict:
    """
    Extract the structural watermark/trace token from a PDF.

    Returns:
        {
            "recovered": str,
            "confidence": float,
            "method": str
        }
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = fitz.open(pdf_path)

    try:
        # ------------------------------------------------------------
        # 1. Check PDF metadata
        # ------------------------------------------------------------
        metadata = document.metadata or {}

        for key in (
            "watermark_token",
            "trace_id",
            "provenance_token",
            "keywords",
        ):
            token = _normalise_token(metadata.get(key))

            if token:
                return {
                    "recovered": token,
                    "confidence": 1.0,
                    "method": f"metadata:{key}",
                }

        # ------------------------------------------------------------
        # 2. Check page-level metadata
        # ------------------------------------------------------------
        for page_number, page in enumerate(document):
            page_text = page.get_text("text")

            if not page_text:
                continue

            # Look for common trace/watermark labels.
            patterns = [
                r"watermark[_\s:-]+([0-9a-fA-F]{16,128})",
                r"trace[_\s:-]+([0-9a-fA-F]{16,128})",
                r"provenance[_\s:-]+([0-9a-fA-F]{16,128})",
            ]

            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)

                if match:
                    token = _normalise_token(match.group(1))

                    if token:
                        return {
                            "recovered": token,
                            "confidence": 0.90,
                            "method": f"page_text:{page_number + 1}",
                        }

        # ------------------------------------------------------------
        # 3. Nothing recovered
        # ------------------------------------------------------------
        return {
            "recovered": "",
            "confidence": 0.0,
            "method": "not_found",
        }

    finally:
        document.close()


def extract(pdf_path: str | Path) -> dict:
    """
    Backwards-compatible alias used by the demo.
    """
    return extract_from_pdf(pdf_path)
def extract_token_from_pdf(
    pdf_path: str | Path,
    expected_length: int | None = None
) -> tuple[str, float]:
    """
    Compatibility function used by the forensic investigation module.

    Returns:
        (recovered_token, confidence)
    """
    result = extract_from_pdf(pdf_path)

    token = result.get("recovered", "")
    confidence = float(result.get("confidence", 0.0))

    # If an expected token length is supplied, require the
    # recovered token to have that length.
    if expected_length is not None:
        if len(token) != expected_length:
            return "", 0.0

    return token, confidence
