"""
Action button bar — Clipboard, Clear, and Convert buttons.
"""

import tkinter as tk

from converter.config.defaults import PALETTE, lighten


def build_button_bar(
    parent: tk.Frame,
    on_clipboard: callable,
    on_clear: callable,
    on_convert: callable,
) -> tk.Button:
    """
    Build the action button bar.

    Parameters
    ----------
    parent : tk.Frame
        Container frame.
    on_clipboard, on_clear, on_convert : callable
        Command callbacks for each button.

    Returns
    -------
    tk.Button
        The convert button reference (needed to toggle state during conversion).
    """
    bar = tk.Frame(parent, bg=PALETTE["bg_root"])
    bar.grid(row=3, column=0, sticky="ew", pady=(4, 8))

    def make_btn(master, text, bg, fg, cmd, width=None):
        cfg = dict(
            text=text,
            font=("Segoe UI", 10, "bold"),
            bg=bg,
            fg=fg,
            activebackground=lighten(bg),
            activeforeground=fg,
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=cmd,
        )
        if width:
            cfg["width"] = width
        btn = tk.Button(master, **cfg)
        btn.bind("<Enter>", lambda e, b=btn, c=lighten(bg): b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
        return btn

    btn_clipboard = make_btn(
        bar,
        "📋  Fetch From Clipboard",
        PALETTE["accent_teal"],
        "#FFFFFF",
        on_clipboard,
    )
    btn_clipboard.pack(side="left", padx=(0, 8))

    btn_clear = make_btn(
        bar,
        "✕  Clear",
        PALETTE["accent_red"],
        "#FFFFFF",
        on_clear,
    )
    btn_clear.pack(side="left", padx=(0, 0))

    btn_convert = make_btn(
        bar,
        "🚀  Convert to Beautiful Word File",
        PALETTE["accent_indigo"],
        "#FFFFFF",
        on_convert,
        width=30,
    )
    btn_convert.pack(side="right", padx=(8, 0))

    return btn_convert
