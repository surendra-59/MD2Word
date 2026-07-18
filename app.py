"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          LLM Output Formatting Utility — Markdown → DOCX Converter          ║
║                                                                              ║
║  Converts raw Markdown pasted from Claude / Gemini / ChatGPT into a         ║
║  beautifully styled Microsoft Word (.docx) document using Pandoc's full     ║
║  AST-based pipeline via pypandoc.                                            ║
║                                                                              ║
║  Dependencies:                                                               ║
║    pip install pypandoc                                                      ║
║    Pandoc binary: https://pandoc.org/installing.html                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import tkinter.font as tkfont
import threading
import datetime
import os
import sys

# ---------------------------------------------------------------------------
# pypandoc import — caught early so the UI can show a helpful error instead
# of crashing silently with an ImportError traceback.
# ---------------------------------------------------------------------------
try:
    import pypandoc
except ImportError:
    import subprocess
    import sys as _sys
    root = tk.Tk()
    root.withdraw()
    answer = messagebox.askyesno(
        "Missing Dependency",
        "The 'pypandoc' package is not installed.\n\n"
        "Would you like to install it now via pip?",
    )
    if answer:
        subprocess.check_call([_sys.executable, "-m", "pip", "install", "pypandoc"])
        import pypandoc
    else:
        _sys.exit(1)


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

# Monospaced font used in the editor widget
EDITOR_FONT_FAMILY = "Consolas"
EDITOR_FONT_SIZE   = 10

# Header banner gradient colors (simulated with canvas)
BANNER_TOP    = "#2D3A4A"
BANNER_BOTTOM = "#1E2229"

# ---------------------------------------------------------------------------
# Pandoc highlight style applied to fenced code blocks.
# Other good options: "tango", "pygments", "kate", "monochrome", "espresso",
#                     "zenburn", "haddock", "breezedark"
# ---------------------------------------------------------------------------
HIGHLIGHT_STYLE = "tango"

# ---------------------------------------------------------------------------
# HOW TO USE A REFERENCE DOCX (company / house style template):
#
#   1. Open a blank Word document, set your preferred styles (Heading 1,
#      Heading 2, Normal, Code Block, Table header colors, fonts, margins…)
#      then save it as  "style_template.docx"  in this project folder.
#
#   2. In the _run_conversion() method below, locate the `extra_args` list
#      and **uncomment** the following line:
#
#          "--reference-doc=style_template.docx",
#
#      Pandoc will map its internal AST node types (Header, Para, CodeBlock,
#      Table, BulletList…) directly onto the named styles from your template.
#      No additional Python code changes are needed.
#
#   3. For absolute paths or a shared network template, replace the string
#      with the full path:
#          "--reference-doc=C:/Company/Templates/house_style.docx",
# ---------------------------------------------------------------------------


# ============================================================================
#  MAIN APPLICATION CLASS
# ============================================================================

class MarkdownConverterApp(tk.Tk):
    """
    Top-level application window.

    Architecture
    ─────────────
    • Inherits from tk.Tk so 'self' IS the root window — no double-window
      anti-pattern.
    • All widget construction is centralized in _build_ui().
    • Pandoc conversion runs in a daemon thread (via threading.Thread) so
      the UI never freezes on large documents.
    • Status messages are written through _set_status() which is always
      called from the main thread using self.after().
    """

    # ------------------------------------------------------------------ init
    def __init__(self):
        super().__init__()

        self.title("LLM Output Formatting Utility")
        self.geometry("720x580")
        self.minsize(620, 480)
        self.configure(bg=PALETTE["bg_root"])

        # Allow the window to stretch
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Track conversion thread so we can prevent double-clicks
        self._converting = False

        self._build_ui()
        self._check_pandoc()

    # --------------------------------------------------------------- pandoc check
    def _check_pandoc(self):
        """
        Verify that the Pandoc binary is reachable on PATH.
        If missing, offer to download it automatically via pypandoc.
        """
        try:
            version = pypandoc.get_pandoc_version()
            self._set_status(f"✔ Pandoc {version} detected — ready.", "success")
        except OSError:
            answer = messagebox.askyesno(
                "Pandoc Not Found",
                "The Pandoc binary could not be found on your system PATH.\n\n"
                "Would you like this utility to download and install Pandoc automatically? (This may take a moment)"
            )
            if answer:
                self._set_status("Downloading Pandoc... please wait.", "info")
                self.update() # Force UI refresh
                try:
                    pypandoc.download_pandoc()
                    version = pypandoc.get_pandoc_version()
                    self._set_status(f"✔ Pandoc {version} installed successfully.", "success")
                    messagebox.showinfo("Success", f"Pandoc {version} installed successfully!")
                except Exception as e:
                    messagebox.showerror(
                        "Error", 
                        f"Failed to download Pandoc: {e}\n\nPlease install it manually from https://pandoc.org/installing.html"
                    )
                    self._set_status("⚠ Pandoc binary not found — install manually.", "error")
            else:
                self._set_status("⚠ Pandoc binary not found — install from pandoc.org", "error")

    # ---------------------------------------------------------------- UI BUILD
    def _build_ui(self):
        """Construct all widgets and lay them out."""

        outer = tk.Frame(self, bg=PALETTE["bg_root"])
        outer.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)   # editor row expands

        # ── Banner ──────────────────────────────────────────────────────────
        self._build_banner(outer)

        # ── Editor card ─────────────────────────────────────────────────────
        self._build_editor_card(outer)

        # ── Options row ─────────────────────────────────────────────────────
        self._build_options_row(outer)

        # ── Action buttons ──────────────────────────────────────────────────
        self._build_button_bar(outer)

        # ── Status bar ──────────────────────────────────────────────────────
        self._build_status_bar(outer)

    # ──────────────────────────────────────────────────────── BANNER
    def _build_banner(self, parent):
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

    # ──────────────────────────────────────────────────────── EDITOR CARD
    def _build_editor_card(self, parent):
        card = tk.Frame(parent, bg=PALETTE["bg_frame"], bd=0,
                        highlightbackground=PALETTE["accent_slate"],
                        highlightthickness=1)
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

        self.editor = scrolledtext.ScrolledText(
            card,
            wrap=tk.WORD,
            font=editor_font,
            bg=PALETTE["bg_editor"],
            fg=PALETTE["text_editor"],
            insertbackground=PALETTE["text_primary"],   # cursor color
            selectbackground=PALETTE["accent_indigo"],
            selectforeground=PALETTE["text_primary"],
            relief="flat",
            padx=10,
            pady=8,
            bd=0,
            undo=True,
        )
        self.editor.grid(row=1, column=0, sticky="nsew", padx=1, pady=(1, 1))

        # Placeholder text
        self._insert_placeholder()

        # Bind focus events to handle placeholder
        self.editor.bind("<FocusIn>",  self._on_editor_focus_in)
        self.editor.bind("<FocusOut>", self._on_editor_focus_out)

    def _insert_placeholder(self):
        placeholder = (
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
        self.editor.insert("1.0", placeholder)
        self.editor.config(fg=PALETTE["text_secondary"])
        self._placeholder_active = True

    def _on_editor_focus_in(self, _event=None):
        if self._placeholder_active:
            self.editor.delete("1.0", tk.END)
            self.editor.config(fg=PALETTE["text_editor"])
            self._placeholder_active = False

    def _on_editor_focus_out(self, _event=None):
        if not self.editor.get("1.0", tk.END).strip():
            self._insert_placeholder()

    # ──────────────────────────────────────────────────────── OPTIONS ROW
    def _build_options_row(self, parent):
        """
        Optional tweaks row — highlight style selector and filename prefix.
        """
        opts = tk.Frame(parent, bg=PALETTE["bg_root"])
        opts.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        opts.columnconfigure(3, weight=1)  # spacer

        # Label: highlight style
        tk.Label(
            opts,
            text="Code highlight:",
            font=("Segoe UI", 9),
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_root"],
        ).grid(row=0, column=0, padx=(0, 6), sticky="w")

        self._highlight_var = tk.StringVar(value=HIGHLIGHT_STYLE)
        styles = ["tango", "pygments", "kate", "monochrome",
                  "espresso", "zenburn", "haddock", "breezedark"]
        style_combo = ttk.Combobox(
            opts,
            textvariable=self._highlight_var,
            values=styles,
            width=14,
            state="readonly",
        )
        style_combo.grid(row=0, column=1, padx=(0, 18), sticky="w")

        # ── ttk style for combobox (dark theme) ──────────────────────────
        combo_style = ttk.Style()
        if "clam" in combo_style.theme_names():
            combo_style.theme_use("clam")
        combo_style.configure(
            "TCombobox",
            fieldbackground=PALETTE["bg_frame"],
            background=PALETTE["bg_frame"],
            foreground=PALETTE["text_primary"],
            selectbackground=PALETTE["accent_indigo"],
            selectforeground=PALETTE["text_primary"],
            bordercolor=PALETTE["accent_slate"],
            arrowcolor=PALETTE["text_secondary"],
        )

        # Label: filename prefix
        tk.Label(
            opts,
            text="Output file prefix:",
            font=("Segoe UI", 9),
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_root"],
        ).grid(row=0, column=2, padx=(0, 6), sticky="w")

        self._prefix_var = tk.StringVar(value="llm_output")
        prefix_entry = tk.Entry(
            opts,
            textvariable=self._prefix_var,
            font=("Segoe UI", 9),
            width=18,
            bg=PALETTE["bg_frame"],
            fg=PALETTE["text_primary"],
            insertbackground=PALETTE["text_primary"],
            relief="flat",
            bd=4,
        )
        prefix_entry.grid(row=0, column=3, padx=(0, 0), sticky="w")

    # ──────────────────────────────────────────────────────── BUTTON BAR
    def _build_button_bar(self, parent):
        bar = tk.Frame(parent, bg=PALETTE["bg_root"])
        bar.grid(row=3, column=0, sticky="ew", pady=(4, 8))

        # ── Helper: create a rounded-ish flat button ──────────────────────
        def make_btn(master, text, bg, fg, cmd, width=None):
            cfg = dict(
                text=text,
                font=("Segoe UI", 10, "bold"),
                bg=bg,
                fg=fg,
                activebackground=_lighten(bg),
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
            # Subtle hover
            btn.bind("<Enter>", lambda e, b=btn, c=_lighten(bg): b.config(bg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
            return btn

        self.btn_clipboard = make_btn(
            bar,
            "📋  Fetch From Clipboard",
            PALETTE["accent_teal"],
            "#FFFFFF",
            self._fetch_clipboard,
        )
        self.btn_clipboard.pack(side="left", padx=(0, 8))

        self.btn_clear = make_btn(
            bar,
            "✕  Clear",
            PALETTE["accent_red"],
            "#FFFFFF",
            self._clear_editor,
        )
        self.btn_clear.pack(side="left", padx=(0, 0))

        self.btn_convert = make_btn(
            bar,
            "🚀  Convert to Beautiful Word File",
            PALETTE["accent_indigo"],
            "#FFFFFF",
            self._start_conversion,
            width=30,
        )
        self.btn_convert.pack(side="right", padx=(8, 0))

    # ──────────────────────────────────────────────────────── STATUS BAR
    def _build_status_bar(self, parent):
        bar = tk.Frame(parent, bg=PALETTE["bg_statusbar"], height=28)
        bar.grid(row=4, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.columnconfigure(0, weight=1)

        self._status_var = tk.StringVar(value="Ready.")
        self._status_lbl = tk.Label(
            bar,
            textvariable=self._status_var,
            font=("Segoe UI", 9),
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_statusbar"],
            anchor="w",
            padx=10,
        )
        self._status_lbl.grid(row=0, column=0, sticky="ew")

    # ================================================================ ACTIONS

    def _fetch_clipboard(self):
        """
        Read text currently held in the OS clipboard and load it into
        the editor, replacing any existing content.
        """
        try:
            text = self.clipboard_get()
        except tk.TclError:
            messagebox.showinfo(
                "Empty Clipboard",
                "The clipboard appears to be empty or contains non-text data.\n"
                "Copy some Markdown text first, then try again.",
            )
            return

        if not text.strip():
            messagebox.showinfo(
                "Empty Clipboard",
                "The clipboard is empty.  Copy some Markdown and try again.",
            )
            return

        # Replace editor content
        self._placeholder_active = False
        self.editor.config(fg=PALETTE["text_editor"])
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", text)
        self._set_status(
            f"✔ Loaded {len(text):,} characters from clipboard.", "success"
        )

    def _clear_editor(self):
        """Wipe the editor and restore the placeholder."""
        confirmed = messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to clear the editor?\nThis cannot be undone.",
        )
        if confirmed:
            self.editor.delete("1.0", tk.END)
            self._insert_placeholder()
            self._set_status("Editor cleared.", "info")

    def _start_conversion(self):
        """
        Kick off the Pandoc conversion in a background daemon thread so
        the Tk event loop stays responsive for large inputs.
        """
        if self._converting:
            messagebox.showinfo("Busy", "A conversion is already in progress.")
            return

        markdown_text = self._get_editor_content()
        if not markdown_text:
            messagebox.showwarning(
                "Nothing to Convert",
                "The editor is empty.  Paste some Markdown first.",
            )
            return

        # Ask the user where to save the file
        timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix      = self._prefix_var.get().strip() or "llm_output"
        default_name = f"{prefix}_{timestamp}.docx"

        output_path = filedialog.asksaveasfilename(
            title="Save Word Document As…",
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx"), ("All Files", "*.*")],
            initialfile=default_name,
        )
        if not output_path:
            # User cancelled the dialog
            return

        self._converting = True
        self.btn_convert.config(state="disabled", text="⏳  Converting…")
        self._set_status("Converting — please wait…", "info")

        thread = threading.Thread(
            target=self._run_conversion,
            args=(markdown_text, output_path),
            daemon=True,
        )
        thread.start()

    def _get_editor_content(self) -> str:
        """Return editor text, stripping placeholder if active."""
        if self._placeholder_active:
            return ""
        raw = self.editor.get("1.0", tk.END)
        return raw.strip()

    # ---------------------------------------------------------------- PANDOC
    def _run_conversion(self, markdown_text: str, output_path: str):
        """
        Execute the Pandoc conversion pipeline.

        Called from a worker thread — never manipulate Tk widgets directly
        here; always route back through self.after().

        ════════════════════════════════════════════════════════════════════
        HOW PANDOC'S AST PIPELINE WORKS
        ════════════════════════════════════════════════════════════════════
        Pandoc parses Markdown into an internal Abstract Syntax Tree (AST)
        whose node types include:
          • Header (level, attr, inlines)
          • Para (inlines)
          • BulletList / OrderedList (list-of-blocks)
          • CodeBlock (attr, text)
          • Table (caption, colspec, head, body, foot)
          • BlockQuote (blocks)

        When writing to .docx, each node is mapped to a named Word style:
          AST Node     →  Word Style Name
          ─────────────────────────────────────
          Header 1     →  "Heading 1"
          Header 2     →  "Heading 2"
          …
          Para         →  "Normal"  (or "First Paragraph")
          CodeBlock    →  "Source Code" (inline → "Verbatim Char")
          BulletList   →  "List Paragraph" (with hanging indent)
          BlockQuote   →  "Block Text"

        If you supply --reference-doc=your_template.docx, Pandoc reads
        ONLY the style *definitions* from that file and writes output into
        a fresh document inheriting those definitions.  The template itself
        is never modified.
        ════════════════════════════════════════════════════════════════════
        """
        try:
            highlight = self._highlight_var.get()

            # ── Extra Pandoc arguments ────────────────────────────────────
            # Carefully extend this list to layer on additional features.
            extra_args = [
                # Code block syntax highlighting theme.
                # Change the value to any of:
                # "tango" | "pygments" | "kate" | "monochrome" |
                # "espresso" | "zenburn" | "haddock" | "breezedark"
                f"--syntax-highlighting={highlight}",

                # Standalone = emit a full docx (required for Word output)
                "--standalone",

                # Table of Contents (uncomment to enable):
                # "--toc",
                # "--toc-depth=3",

                # ── REFERENCE DOC (company / house style template) ────────
                # Step 1: Create your branded template in Word, save it as
                #         "style_template.docx" next to this script.
                # Step 2: Uncomment the line below.
                # Step 3: Every Heading, paragraph, table, and code block
                #         will inherit that template's fonts, colors, and
                #         spacing — zero extra Python code required.
                #
                # "--reference-doc=style_template.docx",
                #
                # For an absolute path (network share, CI environment etc.):
                # "--reference-doc=C:/YourCompany/Templates/house_style.docx",
                # ──────────────────────────────────────────────────────────
            ]

            # ── Invoke Pandoc via pypandoc ────────────────────────────────
            # convert_text()  parameters:
            #   source      – the raw Markdown string
            #   to          – output format ("docx")
            #   format      – input format ("markdown" = Pandoc-extended MD)
            #   outputfile  – write directly to disk (returns None)
            #   extra_args  – list of additional Pandoc CLI flags
            #
            # Pandoc-extended Markdown enables:
            #   pipe_tables, fenced_code_blocks, backtick_code_blocks,
            #   definition_lists, footnotes, yaml_metadata_block, etc.
            pypandoc.convert_text(
                source=markdown_text,
                to="docx",
                format="markdown", # enables smart quotes/dashes by default in modern pandoc
                outputfile=output_path,
                extra_args=extra_args,
            )

            # Route success notification back to the main thread
            self.after(0, self._on_conversion_success, output_path)

        except Exception as exc:
            # Route error notification back to the main thread
            self.after(0, self._on_conversion_error, str(exc))

    # ---------------------------------------------------------------- CALLBACKS
    def _on_conversion_success(self, output_path: str):
        """Called on main thread after a successful conversion."""
        self._converting = False
        self.btn_convert.config(
            state="normal", text="🚀  Convert to Beautiful Word File"
        )
        self._set_status(f"✔ Saved → {output_path}", "success")

        # Ask if the user wants to open the file immediately
        open_now = messagebox.askyesno(
            "Conversion Complete 🎉",
            f"Word document created successfully!\n\n"
            f"📄 {os.path.basename(output_path)}\n"
            f"📁 {os.path.dirname(output_path)}\n\n"
            "Open the file now?",
        )
        if open_now:
            try:
                os.startfile(output_path)   # Windows — opens with default app
            except AttributeError:
                # macOS / Linux fallback
                import subprocess
                subprocess.Popen(["xdg-open", output_path])

    def _on_conversion_error(self, error_msg: str):
        """Called on main thread after a failed conversion."""
        self._converting = False
        self.btn_convert.config(
            state="normal", text="🚀  Convert to Beautiful Word File"
        )
        self._set_status("✖ Conversion failed — see error dialog.", "error")

        messagebox.showerror(
            "Conversion Error",
            f"Pandoc reported an error during conversion:\n\n{error_msg}\n\n"
            "Common causes:\n"
            "  • Pandoc binary missing from PATH\n"
            "  • Invalid or unsupported Markdown syntax\n"
            "  • Output file path is read-only\n"
            "  • Reference doc template is corrupted",
        )

    # ---------------------------------------------------------------- HELPERS
    def _set_status(self, message: str, level: str = "info"):
        """
        Update the status bar label.

        Parameters
        ----------
        message : str
            Text to display.
        level : str
            One of "success" | "error" | "info" — controls text color.
        """
        color_map = {
            "success": PALETTE["text_success"],
            "error":   PALETTE["text_error"],
            "info":    PALETTE["text_info"],
        }
        color = color_map.get(level, PALETTE["text_secondary"])
        self._status_var.set(message)
        self._status_lbl.config(fg=color)


# ============================================================================
#  UTILITY — lighten a hex color for hover states
# ============================================================================

def _lighten(hex_color: str, amount: int = 30) -> str:
    """
    Return a slightly lighter version of `hex_color` (a #RRGGBB string)
    by adding `amount` to each channel (clamped to 255).
    Used for button hover effects.
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = min(r + amount, 255)
    g = min(g + amount, 255)
    b = min(b + amount, 255)
    return f"#{r:02X}{g:02X}{b:02X}"


# ============================================================================
#  ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    app = MarkdownConverterApp()

    # Center the window on the primary display
    app.update_idletasks()
    w = app.winfo_width()
    h = app.winfo_height()
    sw = app.winfo_screenwidth()
    sh = app.winfo_screenheight()
    app.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    app.mainloop()
