"""
Application settings with JSON persistence.

Provides an ``AppSettings`` dataclass that holds every user-configurable
option.  Loads from / saves to a JSON file next to the application entry
point; falls back to built-in defaults when the file is missing or corrupt.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class AppSettings:
    """All user-configurable preferences, serializable to JSON."""

    # ── Code highlighting ────────────────────────────────────────────────
    highlight_style: str = "tango"
    code_font: str = "Consolas"
    code_font_size: int = 10
    code_bg_color: str = "#F5F5F5"
    code_line_spacing: float = 1.15
    code_border_visible: bool = True
    code_line_numbers: bool = False
    code_line_wrap: bool = True

    # ── Smart typography ─────────────────────────────────────────────────
    smart_typography: bool = True

    # ── Table options ────────────────────────────────────────────────────
    table_autofit: bool = True
    table_header_repeat: bool = True
    table_alternating_shading: bool = False

    # ── Output ───────────────────────────────────────────────────────────
    output_prefix: str = "llm_output"

    # ── Validation ───────────────────────────────────────────────────────
    validate_before_convert: bool = True
    check_broken_links: bool = False

    # ------------------------------------------------------------------
    #  Persistence helpers
    # ------------------------------------------------------------------

    def save(self, path: str) -> None:
        """Write current settings to *path* as pretty-printed JSON."""
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(asdict(self), fh, indent=2, ensure_ascii=False)
        except OSError:
            # Silently ignore write failures (e.g. read-only filesystem)
            pass

    @classmethod
    def load(cls, path: str) -> "AppSettings":
        """
        Load settings from *path*.

        Returns a default ``AppSettings`` instance when the file is
        missing, empty, or contains malformed JSON.
        """
        if not os.path.isfile(path):
            return cls()
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                return cls()
            # Only feed keys that actually exist on the dataclass so that
            # stale / unknown keys in an old config file are ignored.
            valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
            filtered = {k: v for k, v in data.items() if k in valid_keys}
            return cls(**filtered)
        except (json.JSONDecodeError, TypeError, OSError):
            return cls()
