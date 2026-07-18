"""
Banner / header widget for the application window.
"""

import tkinter as tk

from converter.config.defaults import PALETTE, BANNER_TOP


def build_banner(parent: tk.Frame) -> None:
    """
    Construct the top banner with title and subtitle.

    Parameters
    ----------
    parent : tk.Frame
        The outer frame that owns this banner.
    """
    banner_frame = tk.Frame(parent, bg=BANNER_TOP, bd=0, height=72)
    banner_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    banner_frame.columnconfigure(0, weight=1)
    banner_frame.grid_propagate(False)

    # Title
    title_lbl = tk.Label(
        banner_frame,
        text="LLM Output Formatting Utility",
        font=("Segoe UI", 17, "bold"),
        fg=PALETTE["text_primary"],
        bg=BANNER_TOP,
        anchor="w",
    )
    title_lbl.grid(row=0, column=0, padx=18, pady=(14, 2), sticky="w")

    # Sub-title
    sub_lbl = tk.Label(
        banner_frame,
        text="Paste Markdown from Claude · Gemini · ChatGPT  →  Export polished Word .docx",
        font=("Segoe UI", 9),
        fg=PALETTE["text_secondary"],
        bg=BANNER_TOP,
        anchor="w",
    )
    sub_lbl.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

    # Thin accent line under banner
    sep = tk.Frame(parent, bg=PALETTE["accent_slate"], height=1)
    sep.grid(row=0, column=0, sticky="sew")
