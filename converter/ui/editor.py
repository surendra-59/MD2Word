"""
Markdown source editor with placeholder support.
"""

import tkinter as tk
from tkinter import scrolledtext
import tkinter.font as tkfont

from converter.config.defaults import PALETTE, EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE


class MarkdownEditor:
    """
    Wraps a ``ScrolledText`` widget with placeholder text handling.

    Attributes
    ----------
    widget : scrolledtext.ScrolledText
        The underlying text widget (for direct access by the app).
    """

    PLACEHOLDER_TEXT = (
        "# Paste your Markdown here…\n\n"
        "Or click  📋 Fetch From Clipboard  to load directly from the clipboard.\n\n"
        "Supported elements:\n"
        "  • Headers (# H1 through ###### H6)\n"
        "  • **Bold**, *italic*, ~~strikethrough~~\n"
        "  • Bullet lists & numbered lists (including nested)\n"
        "  • | Pipe | Tables |\n"
        "  • > Blockquotes\n"
        "  • ```fenced code blocks``` with syntax highlighting\n"
        "  • Inline `code`\n"
        "  • [Hyperlinks](https://example.com)\n"
    )

    def __init__(self, parent: tk.Frame) -> None:
        self._placeholder_active = False

        card = tk.Frame(
            parent,
            bg=PALETTE["bg_frame"],
            bd=0,
            highlightbackground=PALETTE["accent_slate"],
            highlightthickness=1,
        )
        card.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        # Card header label
        hdr = tk.Label(
            card,
            text="  Markdown Source",
            font=("Segoe UI", 9, "bold"),
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_frame"],
            anchor="w",
            pady=6,
        )
        hdr.grid(row=0, column=0, sticky="ew")

        thin_sep = tk.Frame(card, bg=PALETTE["accent_slate"], height=1)
        thin_sep.grid(row=0, column=0, sticky="sew")

        # The monospaced scrolled editor
        editor_font = tkfont.Font(
            family=EDITOR_FONT_FAMILY, size=EDITOR_FONT_SIZE
        )

        self.widget = scrolledtext.ScrolledText(
            card,
            wrap=tk.WORD,
            font=editor_font,
            bg=PALETTE["bg_editor"],
            fg=PALETTE["text_editor"],
            insertbackground=PALETTE["text_primary"],
            selectbackground=PALETTE["accent_indigo"],
            selectforeground=PALETTE["text_primary"],
            relief="flat",
            padx=10,
            pady=8,
            bd=0,
            undo=True,
        )
        self.widget.grid(row=1, column=0, sticky="nsew", padx=1, pady=(1, 1))

        # Placeholder text
        self._insert_placeholder()

        # Bind focus events to handle placeholder
        self.widget.bind("<FocusIn>",  self._on_focus_in)
        self.widget.bind("<FocusOut>", self._on_focus_out)

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------

    def get_content(self) -> str:
        """Return editor text, returning empty string if placeholder is showing."""
        if self._placeholder_active:
            return ""
        return self.widget.get("1.0", tk.END).strip()

    def set_content(self, text: str) -> None:
        """Replace editor content with *text*, clearing placeholder."""
        self._placeholder_active = False
        self.widget.config(fg=PALETTE["text_editor"])
        self.widget.delete("1.0", tk.END)
        self.widget.insert("1.0", text)

    def clear(self) -> None:
        """Wipe the editor and restore the placeholder."""
        self.widget.delete("1.0", tk.END)
        self._insert_placeholder()

    @property
    def placeholder_active(self) -> bool:
        return self._placeholder_active

    # ------------------------------------------------------------------
    #  Internal
    # ------------------------------------------------------------------

    def _insert_placeholder(self) -> None:
        self.widget.insert("1.0", self.PLACEHOLDER_TEXT)
        self.widget.config(fg=PALETTE["text_secondary"])
        self._placeholder_active = True

    def _on_focus_in(self, _event=None) -> None:
        if self._placeholder_active:
            self.widget.delete("1.0", tk.END)
            self.widget.config(fg=PALETTE["text_editor"])
            self._placeholder_active = False

    def _on_focus_out(self, _event=None) -> None:
        if not self.widget.get("1.0", tk.END).strip():
            self._insert_placeholder()
