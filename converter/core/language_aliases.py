"""
Language alias normalization for fenced code blocks.

Maps common shorthand language identifiers to their canonical names
so that Pandoc's Skylighting engine can apply proper syntax highlighting.
"""

from __future__ import annotations

import re
from typing import Optional

# ---------------------------------------------------------------------------
# Canonical alias map.  Keys are lowercase; values are the Pandoc-recognized
# language name.  Extend this dict to support additional aliases.
# ---------------------------------------------------------------------------
ALIAS_MAP: dict[str, str] = {
    # Python
    "py":        "python",
    "python3":   "python",
    "py3":       "python",
    # JavaScript / TypeScript
    "js":        "javascript",
    "ts":        "typescript",
    "tsx":       "typescript",
    "jsx":       "javascript",
    # Shell
    "sh":        "bash",
    "shell":     "bash",
    "zsh":       "bash",
    # C / C++
    "c++":       "cpp",
    "cxx":       "cpp",
    "h":         "c",
    "hpp":       "cpp",
    # PowerShell
    "ps1":       "powershell",
    "psm1":      "powershell",
    # Markup
    "yml":       "yaml",
    "md":        "markdown",
    # Other common aliases
    "dockerfile":"docker",
    "rs":        "rust",
    "rb":        "ruby",
    "kt":        "kotlin",
    "cs":        "csharp",
    "m":         "objectivec",
    "mm":        "objectivec",
}

# Regex to match a fenced code block opening:  ```lang  or  ~~~lang
_FENCE_RE = re.compile(
    r"^(?P<indent>\s*)(?P<fence>`{3,}|~{3,})(?P<lang>\S+)?(?P<rest>.*)$",
    re.MULTILINE,
)


def normalize_language(lang: str) -> str:
    """
    Return the canonical language name for *lang*.

    If *lang* is a known alias, the canonical name is returned.
    Otherwise *lang* is returned unchanged (lowercased and stripped).
    """
    return ALIAS_MAP.get(lang.lower().strip(), lang.lower().strip())


def normalize_code_fences(
    markdown: str,
    supported_languages: Optional[set[str]] = None,
) -> tuple[str, list[str]]:
    """
    Scan *markdown* for fenced code block openings, normalize any
    aliased language labels, and return the modified text together with
    a list of unknown (unsupported) language identifiers.

    Parameters
    ----------
    markdown : str
        Raw Markdown source text.
    supported_languages : set[str] | None
        Set of language names that Pandoc can highlight.  If ``None``,
        unknown-language detection is skipped.

    Returns
    -------
    tuple[str, list[str]]
        ``(normalized_markdown, unknown_languages)``
    """
    unknown: list[str] = []

    def _replace(match: re.Match) -> str:
        lang = match.group("lang")
        if lang is None:
            return match.group(0)  # no language specified — leave as-is

        canonical = normalize_language(lang)

        # Track unknown languages
        if supported_languages is not None and canonical not in supported_languages:
            if canonical not in unknown:
                unknown.append(canonical)

        indent = match.group("indent")
        fence  = match.group("fence")
        rest   = match.group("rest")
        return f"{indent}{fence}{canonical}{rest}"

    result = _FENCE_RE.sub(_replace, markdown)
    return result, unknown
