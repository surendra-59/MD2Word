"""
Highlight theme metadata and font utilities.

Maps each Pandoc highlight style to representative token colors so
the Style Gallery (future phase) can render approximate code samples
without invoking Pandoc.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ThemeColors:
    """Representative syntax token colors for one highlight theme."""
    keyword: str
    string: str
    comment: str
    number: str
    background: str
    foreground: str


# ---------------------------------------------------------------------------
# Mapping of Pandoc built-in theme names → representative colors.
# These are approximations used only for the in-app Style Gallery canvas.
# ---------------------------------------------------------------------------

THEME_COLORS: dict[str, ThemeColors] = {
    "tango": ThemeColors(
        keyword="#204A87",  string="#4E9A06",  comment="#8F5902",
        number="#AD7FA8",   background="#F8F8F8", foreground="#2E3436",
    ),
    "pygments": ThemeColors(
        keyword="#008000",  string="#BA2121",  comment="#408080",
        number="#666666",   background="#FFFFFF", foreground="#000000",
    ),
    "kate": ThemeColors(
        keyword="#1F1C1B",  string="#BF0303",  comment="#898887",
        number="#B08000",   background="#FFFFFF", foreground="#1F1C1B",
    ),
    "monochrome": ThemeColors(
        keyword="#000000",  string="#000000",  comment="#888888",
        number="#000000",   background="#FFFFFF", foreground="#000000",
    ),
    "espresso": ThemeColors(
        keyword="#43A8ED",  string="#049B0A",  comment="#0066FF",
        number="#44AA43",   background="#2A211C", foreground="#BDAE9D",
    ),
    "zenburn": ThemeColors(
        keyword="#F0DFAF",  string="#CC9393",  comment="#7F9F7F",
        number="#8CD0D3",   background="#3F3F3F", foreground="#DCDCCC",
    ),
    "haddock": ThemeColors(
        keyword="#0000FF",  string="#4070A0",  comment="#60A0B0",
        number="#40A070",   background="#F8F8F8", foreground="#000000",
    ),
    "breezedark": ThemeColors(
        keyword="#CFCFC2",  string="#F44F4F",  comment="#7A7C7D",
        number="#F67400",   background="#232629", foreground="#CFCFC2",
    ),
}


def resolve_code_font(preferred: str) -> str:
    """
    Return *preferred* if it is available on the current system,
    otherwise walk a fallback chain and return the first match.

    Uses ``tkinter.font.families()`` for detection.  If tkinter is
    not yet initialised (no root window), returns *preferred* unchanged
    since we cannot enumerate system fonts without a Tk instance.
    """
    fallback_chain = [preferred, "Consolas", "Courier New"]
    try:
        import tkinter.font as tkfont
        available = {f.lower() for f in tkfont.families()}
        for font in fallback_chain:
            if font.lower() in available:
                return font
        # Absolute last resort — guaranteed on every OS
        return "Courier New"
    except Exception:
        return preferred
