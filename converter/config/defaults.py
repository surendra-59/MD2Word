"""
Centralized constants, color palette, and utility functions.

All visual tokens and default values that were previously scattered
across the top of the monolithic app.py are collected here.
"""

# ============================================================================
#  COLOR PALETTE & STYLE TOKENS
# ============================================================================

PALETTE = {
    # Backgrounds
    "bg_root":      "#1E2229",   # Very dark slate — root window
    "bg_frame":     "#252A34",   # Slightly lighter — inner frames
    "bg_editor":    "#1A1D24",   # Near-black — the markdown text editor
    "bg_statusbar": "#161A20",   # Darkest — status strip at bottom

    # Accent colors
    "accent_slate": "#4A5568",   # Muted blue-grey — separators / subtle labels
    "accent_teal":  "#38B2AC",   # Teal — clipboard button
    "accent_red":   "#E53E3E",   # Soft red — clear button
    "accent_indigo":"#5A67D8",   # Indigo — primary convert action
    "accent_indigo_hover": "#667EEA",

    # Text
    "text_primary":   "#E2E8F0", # Near-white — main label text
    "text_secondary": "#A0AEC0", # Grey — sub-labels / placeholders
    "text_editor":    "#D1FAE5", # Very light green tint — MD source text
    "text_success":   "#68D391", # Soft green — success status messages
    "text_error":     "#FC8181", # Soft red — error status messages
    "text_info":      "#76E4F7", # Cyan — informational
}

# Header banner gradient colors (simulated with canvas)
BANNER_TOP    = "#2D3A4A"
BANNER_BOTTOM = "#1E2229"

# Monospaced font used in the editor widget
EDITOR_FONT_FAMILY = "Consolas"
EDITOR_FONT_SIZE   = 10

# ---------------------------------------------------------------------------
# Default Pandoc highlight style
# ---------------------------------------------------------------------------
DEFAULT_HIGHLIGHT_STYLE = "tango"

# Available Pandoc highlight styles
AVAILABLE_HIGHLIGHT_STYLES = [
    "tango", "pygments", "kate", "monochrome",
    "espresso", "zenburn", "haddock", "breezedark",
]

# Available monospaced code fonts
AVAILABLE_CODE_FONTS = [
    "Consolas",
    "Cascadia Code",
    "Fira Code",
    "JetBrains Mono",
    "Courier New",
]

DEFAULT_CODE_FONT      = "Consolas"
DEFAULT_CODE_FONT_SIZE = 10


# ============================================================================
#  UTILITY — lighten a hex color for hover states
# ============================================================================

def lighten(hex_color: str, amount: int = 30) -> str:
    """
    Return a slightly lighter version of *hex_color* (a ``#RRGGBB`` string)
    by adding *amount* to each channel (clamped to 255).

    Used for button hover effects.
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = min(r + amount, 255)
    g = min(g + amount, 255)
    b = min(b + amount, 255)
    return f"#{r:02X}{g:02X}{b:02X}"
