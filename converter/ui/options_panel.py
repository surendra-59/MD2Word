"""
Expanded options panel with tabbed interface.

Replaces the original single-row options bar with a ``ttk.Notebook``
containing three tabs:

  1. **General**   — output prefix, smart typography, validation toggle
  2. **Code Style** — highlight theme, font, size, background, spacing,
                      borders, line numbers
  3. **Tables**    — auto-fit, header repeat, alternating shading
"""

import tkinter as tk
from tkinter import ttk

from converter.config.defaults import (
    PALETTE,
    AVAILABLE_HIGHLIGHT_STYLES,
    AVAILABLE_CODE_FONTS,
)
from converter.config.settings import AppSettings


class OptionsPanel:
    """
    Multi-tab options panel.

    All controls two-way bind to ``tk.StringVar`` / ``tk.BooleanVar``
    instances.  Call ``apply_to_settings()`` to flush current values
    into an ``AppSettings`` dataclass.
    """

    def __init__(self, parent: tk.Frame, settings: AppSettings) -> None:
        # ── ttk dark-theme styling ───────────────────────────────────────
        self._configure_styles()

        # ── Variables bound to controls ──────────────────────────────────
        # General
        self.prefix_var          = tk.StringVar(value=settings.output_prefix)
        self.smart_typo_var      = tk.BooleanVar(value=settings.smart_typography)
        self.validate_var        = tk.BooleanVar(value=settings.validate_before_convert)

        # Code Style
        self.highlight_var       = tk.StringVar(value=settings.highlight_style)
        self.code_font_var       = tk.StringVar(value=settings.code_font)
        self.code_size_var       = tk.IntVar(value=settings.code_font_size)
        self.code_bg_var         = tk.StringVar(value=settings.code_bg_color)
        self.code_spacing_var    = tk.DoubleVar(value=settings.code_line_spacing)
        self.code_border_var     = tk.BooleanVar(value=settings.code_border_visible)
        self.code_linenums_var   = tk.BooleanVar(value=settings.code_line_numbers)

        # Tables
        self.table_autofit_var   = tk.BooleanVar(value=settings.table_autofit)
        self.table_header_var    = tk.BooleanVar(value=settings.table_header_repeat)
        self.table_shading_var   = tk.BooleanVar(value=settings.table_alternating_shading)

        # ── Container frame ──────────────────────────────────────────────
        container = tk.Frame(parent, bg=PALETTE["bg_root"])
        container.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        container.columnconfigure(0, weight=1)

        # ── Notebook ─────────────────────────────────────────────────────
        notebook = ttk.Notebook(container, style="Dark.TNotebook")
        notebook.grid(row=0, column=0, sticky="ew")

        self._tab_general    = self._build_general_tab(notebook)
        self._tab_code_style = self._build_code_style_tab(notebook)
        self._tab_tables     = self._build_tables_tab(notebook)

        notebook.add(self._tab_general,    text="  General  ")
        notebook.add(self._tab_code_style, text="  Code Style  ")
        notebook.add(self._tab_tables,     text="  Tables  ")

    # ==================================================================
    #  Tab builders
    # ==================================================================

    def _build_general_tab(self, notebook: ttk.Notebook) -> tk.Frame:
        """General settings tab."""
        tab = tk.Frame(notebook, bg=PALETTE["bg_frame"], padx=12, pady=10)

        # Row 0: Output file prefix
        self._label(tab, "Output file prefix:", 0, 0)
        prefix_entry = tk.Entry(
            tab,
            textvariable=self.prefix_var,
            font=("Segoe UI", 9),
            width=22,
            bg=PALETTE["bg_editor"],
            fg=PALETTE["text_primary"],
            insertbackground=PALETTE["text_primary"],
            relief="flat",
            bd=4,
        )
        prefix_entry.grid(row=0, column=1, padx=(0, 20), sticky="w")

        # Row 0: Smart typography checkbox
        self._checkbox(tab, "Smart typography", self.smart_typo_var, 0, 2)

        # Row 0: Validate before convert
        self._checkbox(tab, "Validate before convert", self.validate_var, 0, 4)

        return tab

    def _build_code_style_tab(self, notebook: ttk.Notebook) -> tk.Frame:
        """Code block styling tab."""
        tab = tk.Frame(notebook, bg=PALETTE["bg_frame"], padx=12, pady=10)

        # Row 0: Highlight theme
        self._label(tab, "Theme:", 0, 0)
        theme_combo = ttk.Combobox(
            tab,
            textvariable=self.highlight_var,
            values=AVAILABLE_HIGHLIGHT_STYLES,
            width=14,
            state="readonly",
            style="Dark.TCombobox",
        )
        theme_combo.grid(row=0, column=1, padx=(0, 16), sticky="w")

        # Row 0: Font
        self._label(tab, "Font:", 0, 2)
        font_combo = ttk.Combobox(
            tab,
            textvariable=self.code_font_var,
            values=AVAILABLE_CODE_FONTS,
            width=16,
            state="readonly",
            style="Dark.TCombobox",
        )
        font_combo.grid(row=0, column=3, padx=(0, 16), sticky="w")

        # Row 0: Font size
        self._label(tab, "Size:", 0, 4)
        size_spin = tk.Spinbox(
            tab,
            from_=6,
            to=24,
            textvariable=self.code_size_var,
            width=4,
            font=("Segoe UI", 9),
            bg=PALETTE["bg_editor"],
            fg=PALETTE["text_primary"],
            buttonbackground=PALETTE["bg_frame"],
            relief="flat",
            bd=2,
        )
        size_spin.grid(row=0, column=5, padx=(0, 0), sticky="w")

        # Row 1: Line spacing
        self._label(tab, "Line spacing:", 1, 0)
        spacing_spin = tk.Spinbox(
            tab,
            from_=0.8,
            to=3.0,
            increment=0.05,
            textvariable=self.code_spacing_var,
            width=5,
            font=("Segoe UI", 9),
            format="%.2f",
            bg=PALETTE["bg_editor"],
            fg=PALETTE["text_primary"],
            buttonbackground=PALETTE["bg_frame"],
            relief="flat",
            bd=2,
        )
        spacing_spin.grid(row=1, column=1, padx=(0, 16), pady=(6, 0), sticky="w")

        # Row 1: Checkboxes
        self._checkbox(tab, "Show borders", self.code_border_var, 1, 2, pady=(6, 0))
        self._checkbox(tab, "Line numbers", self.code_linenums_var, 1, 4, pady=(6, 0))

        return tab

    def _build_tables_tab(self, notebook: ttk.Notebook) -> tk.Frame:
        """Table formatting tab."""
        tab = tk.Frame(notebook, bg=PALETTE["bg_frame"], padx=12, pady=10)

        self._checkbox(tab, "Auto-fit table width", self.table_autofit_var, 0, 0)
        self._checkbox(tab, "Repeat header row across pages", self.table_header_var, 0, 2)
        self._checkbox(tab, "Alternating row shading", self.table_shading_var, 0, 4)

        return tab

    # ==================================================================
    #  Widget helpers
    # ==================================================================

    def _label(
        self, parent: tk.Frame, text: str, row: int, col: int
    ) -> tk.Label:
        """Create a styled label at the given grid position."""
        lbl = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 9),
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_frame"],
        )
        lbl.grid(row=row, column=col, padx=(0, 6), sticky="w")
        return lbl

    def _checkbox(
        self,
        parent: tk.Frame,
        text: str,
        variable: tk.BooleanVar,
        row: int,
        col: int,
        pady: tuple = (0, 0),
    ) -> tk.Checkbutton:
        """Create a dark-themed checkbutton at the given grid position."""
        cb = tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            font=("Segoe UI", 9),
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_frame"],
            selectcolor=PALETTE["bg_editor"],
            activebackground=PALETTE["bg_frame"],
            activeforeground=PALETTE["text_primary"],
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        cb.grid(row=row, column=col, columnspan=2, padx=(0, 12), pady=pady, sticky="w")
        return cb

    # ==================================================================
    #  Styling
    # ==================================================================

    def _configure_styles(self) -> None:
        """Apply dark-theme styling to ttk widgets."""
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        # Notebook tabs
        style.configure(
            "Dark.TNotebook",
            background=PALETTE["bg_root"],
            borderwidth=0,
        )
        style.configure(
            "Dark.TNotebook.Tab",
            background=PALETTE["bg_frame"],
            foreground=PALETTE["text_secondary"],
            padding=(12, 6),
            font=("Segoe UI", 9),
        )
        style.map(
            "Dark.TNotebook.Tab",
            background=[("selected", PALETTE["accent_indigo"])],
            foreground=[("selected", PALETTE["text_primary"])],
        )

        # Combobox
        style.configure(
            "Dark.TCombobox",
            fieldbackground=PALETTE["bg_editor"],
            background=PALETTE["bg_frame"],
            foreground=PALETTE["text_primary"],
            selectbackground=PALETTE["accent_indigo"],
            selectforeground=PALETTE["text_primary"],
            bordercolor=PALETTE["accent_slate"],
            arrowcolor=PALETTE["text_secondary"],
        )

        # Also configure the default TCombobox for backward compat
        style.configure(
            "TCombobox",
            fieldbackground=PALETTE["bg_frame"],
            background=PALETTE["bg_frame"],
            foreground=PALETTE["text_primary"],
            selectbackground=PALETTE["accent_indigo"],
            selectforeground=PALETTE["text_primary"],
            bordercolor=PALETTE["accent_slate"],
            arrowcolor=PALETTE["text_secondary"],
        )

    # ==================================================================
    #  Sync
    # ==================================================================

    def apply_to_settings(self, settings: AppSettings) -> None:
        """Write all current control values back into the settings dataclass."""
        # General
        settings.output_prefix          = self.prefix_var.get().strip() or "llm_output"
        settings.smart_typography       = self.smart_typo_var.get()
        settings.validate_before_convert = self.validate_var.get()

        # Code Style
        settings.highlight_style     = self.highlight_var.get()
        settings.code_font           = self.code_font_var.get()
        settings.code_border_visible = self.code_border_var.get()
        settings.code_line_numbers   = self.code_linenums_var.get()

        # Handle spinbox values that could be strings
        try:
            settings.code_font_size = int(self.code_size_var.get())
        except (ValueError, tk.TclError):
            settings.code_font_size = 10

        try:
            settings.code_line_spacing = float(self.code_spacing_var.get())
        except (ValueError, tk.TclError):
            settings.code_line_spacing = 1.15

        # Tables
        settings.table_autofit              = self.table_autofit_var.get()
        settings.table_header_repeat        = self.table_header_var.get()
        settings.table_alternating_shading  = self.table_shading_var.get()
