"""High-performance translation service for Market Intelligence.

Uses zero-cost Google Translate API with in-memory caching and intelligent chunking.
Preserves Markdown structure, headings, bold syntax, lists, emojis, and numbers.
"""

from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# In-memory translation cache to eliminate redundant network calls
_CACHE: Dict[str, str] = {}


def translate_text(text: str, target_lang: str = "hi", source_lang: str = "en") -> str:
    """Translate plain text string into target language (default: Hindi)."""
    if not text or not text.strip():
        return text

    cache_key = f"{source_lang}:{target_lang}:{text.strip()}"
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    try:
        url = (
            f"https://translate.googleapis.com/translate_a/single?"
            f"client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q="
            + urllib.parse.quote(text)
        )
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko)"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated = "".join([part[0] for part in data[0] if part and part[0]])
            _CACHE[cache_key] = translated
            return translated
    except Exception as exc:
        logger.warning("Translation failed for '%s...': %s", text[:40], exc)
        return text


def translate_batch(texts: List[str], target_lang: str = "hi") -> List[str]:
    """Translate a list of strings efficiently."""
    return [translate_text(t, target_lang=target_lang) for t in texts]


def translate_markdown(md_text: str, target_lang: str = "hi") -> str:
    """Translate markdown document chunk by chunk while preserving formatting."""
    if not md_text or not md_text.strip():
        return md_text

    lines = md_text.split("\n")
    translated_lines: List[str] = []
    chunk: List[str] = []
    chunk_len = 0

    for line in lines:
        # Don't translate empty lines or separators
        if not line.strip() or line.strip() in ("---", "***"):
            if chunk:
                batch_text = "\n".join(chunk)
                translated_lines.append(translate_text(batch_text, target_lang=target_lang))
                chunk = []
                chunk_len = 0
            translated_lines.append(line)
            continue

        if chunk_len + len(line) > 1000:
            batch_text = "\n".join(chunk)
            translated_lines.append(translate_text(batch_text, target_lang=target_lang))
            chunk = [line]
            chunk_len = len(line)
        else:
            chunk.append(line)
            chunk_len += len(line) + 1

    if chunk:
        batch_text = "\n".join(chunk)
        translated_lines.append(translate_text(batch_text, target_lang=target_lang))

    return "\n".join(translated_lines)
