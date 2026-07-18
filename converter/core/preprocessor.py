"""
Markdown pre-processor.

Transforms the raw Markdown *before* handing it to Pandoc:
  1. Normalize code fence language aliases.
  2. Prepare task list markers for older Pandoc versions.

This module is intentionally pure-functional — no side effects,
no file I/O, easily testable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from converter.config.settings import AppSettings
from converter.core.language_aliases import normalize_code_fences


@dataclass
class PreprocessResult:
    """Outcome of the pre-processing step."""
    markdown: str
    unknown_languages: list[str] = field(default_factory=list)


def preprocess(
    markdown: str,
    settings: AppSettings,
    supported_languages: Optional[set[str]] = None,
    pandoc_version: Optional[str] = None,
) -> PreprocessResult:
    """
    Apply all pre-processing transforms to *markdown*.

    Parameters
    ----------
    markdown : str
        Raw Markdown source from the editor.
    settings : AppSettings
        Current application settings.
    supported_languages : set[str] | None
        Pandoc-supported language names (for unknown-language detection).
    pandoc_version : str | None
        Pandoc version string (e.g. "3.1.0").  Used to decide whether
        task list fallback is needed.

    Returns
    -------
    PreprocessResult
        The transformed Markdown and any warnings collected.
    """
    unknown_langs: list[str] = []

    # 1. Normalize code fence language labels
    markdown, unknown_langs = normalize_code_fences(markdown, supported_languages)

    # 2. Task-list fallback for old Pandoc versions (< 2.6)
    #    Modern Pandoc handles task lists natively via +task_lists extension,
    #    so this only activates when running on a very old installation.
    if pandoc_version and _version_lt(pandoc_version, "2.6"):
        markdown = _task_list_fallback(markdown)

    return PreprocessResult(
        markdown=markdown,
        unknown_languages=unknown_langs,
    )


# ---------------------------------------------------------------------------
#  Internal helpers
# ---------------------------------------------------------------------------

def _version_lt(version: str, threshold: str) -> bool:
    """Return True if *version* is strictly less than *threshold*."""
    def _parts(v: str) -> list[int]:
        return [int(x) for x in re.findall(r"\d+", v)]
    return _parts(version) < _parts(threshold)


def _task_list_fallback(markdown: str) -> str:
    """
    Replace GFM task-list markers with Unicode checkbox symbols
    for Pandoc versions that lack the ``+task_lists`` extension.

    ``- [x]`` → ``- ☑``
    ``- [ ]`` → ``- ☐``
    """
    markdown = re.sub(
        r"^(\s*[-*+]\s)\[x\]",
        r"\1☑",
        markdown,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    markdown = re.sub(
        r"^(\s*[-*+]\s)\[ \]",
        r"\1☐",
        markdown,
        flags=re.MULTILINE,
    )
    return markdown
