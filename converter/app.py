"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          LLM Output Formatting Utility — Markdown → DOCX Converter          ║
║                                                                              ║
║  Converts raw Markdown pasted from Claude / Gemini / ChatGPT into a         ║
║  beautifully styled Microsoft Word (.docx) document using Pandoc's full     ║
║  AST-based pipeline via pypandoc.                                            ║
║                                                                              ║
║  Dependencies:                                                               ║
║    pip install pypandoc python-docx                                          ║
║    Pandoc binary: https://pandoc.org/installing.html                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import messagebox, filedialog
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

from converter.config.defaults import PALETTE
from converter.config.settings import AppSettings
from converter.ui.banner import build_banner
from converter.ui.editor import MarkdownEditor
from converter.ui.options_panel import OptionsPanel
from converter.ui.button_bar import build_button_bar
from converter.ui.status_bar import StatusBar
from converter.ui.validation_dialog import ValidationDialog
from converter.core.pipeline import ConversionPipeline
from converter.core.validator import MarkdownValidator


# ============================================================================
#  Resolve config path — sits next to the entry-point script, not this file
# ============================================================================

def _config_path() -> str:
    """Return the absolute path to ``config.json`` next to the top-level entry point."""
    # When frozen with PyInstaller, sys.executable is the .exe path
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        # Walk up from converter/app.py → project root
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "config.json")


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

        # Load persistent settings
        self._settings = AppSettings.load(_config_path())

        self._build_ui()
        self._check_pandoc()

        # Save settings on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ close
    def _on_close(self):
        """Save settings then destroy the window."""
        self._options_panel.apply_to_settings(self._settings)
        self._settings.save(_config_path())
        self.destroy()

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
        build_banner(outer)

        # ── Editor card ─────────────────────────────────────────────────────
        self._editor = MarkdownEditor(outer)

        # ── Options row ─────────────────────────────────────────────────────
        self._options_panel = OptionsPanel(outer, self._settings)

        # ── Action buttons ──────────────────────────────────────────────────
        self._btn_convert = build_button_bar(
            outer,
            on_clipboard=self._fetch_clipboard,
            on_clear=self._clear_editor,
            on_convert=self._start_conversion,
        )

        # ── Status bar ──────────────────────────────────────────────────────
        self._status = StatusBar(outer)

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
        self._editor.set_content(text)
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
            self._editor.clear()
            self._set_status("Editor cleared.", "info")

    def _start_conversion(self):
        """
        Kick off the Pandoc conversion in a background daemon thread so
        the Tk event loop stays responsive for large inputs.
        """
        if self._converting:
            messagebox.showinfo("Busy", "A conversion is already in progress.")
            return

        markdown_text = self._editor.get_content()
        if not markdown_text:
            messagebox.showwarning(
                "Nothing to Convert",
                "The editor is empty.  Paste some Markdown first.",
            )
            return

        # Sync UI values to settings before conversion
        self._options_panel.apply_to_settings(self._settings)

        # ── Validation step (runs on main thread — fast) ─────────────
        if self._settings.validate_before_convert:
            validator = MarkdownValidator()
            issues = validator.validate(
                markdown_text,
                check_broken_links=self._settings.check_broken_links,
            )
            if issues:
                dialog = ValidationDialog(self, issues)
                self.wait_window(dialog)
                if dialog.result == "cancel":
                    self._set_status("Conversion cancelled after validation.", "info")
                    return

        # Ask the user where to save the file
        timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix      = self._settings.output_prefix or "llm_output"
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
        self._btn_convert.config(state="disabled", text="⏳  Converting…")
        self._set_status("Converting — please wait…", "info")

        thread = threading.Thread(
            target=self._run_conversion,
            args=(markdown_text, output_path),
            daemon=True,
        )
        thread.start()

    # ---------------------------------------------------------------- PANDOC
    def _run_conversion(self, markdown_text: str, output_path: str):
        """
        Execute the conversion pipeline in a worker thread.

        Routes results back to the main thread via self.after().
        """
        pipeline = ConversionPipeline(self._settings)
        result = pipeline.convert(
            markdown_text=markdown_text,
            output_path=output_path,
            progress_callback=lambda msg: self.after(0, self._set_status, msg, "info"),
        )

        if result.success:
            self.after(0, self._on_conversion_success, result)
        else:
            self.after(0, self._on_conversion_error, result.error_message)

    # ---------------------------------------------------------------- CALLBACKS
    def _on_conversion_success(self, result):
        """Called on main thread after a successful conversion."""
        self._converting = False
        self._btn_convert.config(
            state="normal", text="🚀  Convert to Beautiful Word File"
        )

        # Build status message
        status_parts = [f"✔ Saved → {result.output_path}"]
        if result.warnings:
            status_parts.append(f"({len(result.warnings)} warning(s))")
        self._set_status(" ".join(status_parts), "success")

        # Ask if the user wants to open the file immediately
        warning_text = ""
        if result.warnings:
            warning_text = "\n\n⚠ Warnings:\n" + "\n".join(
                f"  • {w}" for w in result.warnings
            )

        open_now = messagebox.askyesno(
            "Conversion Complete 🎉",
            f"Word document created successfully!\n\n"
            f"📄 {os.path.basename(result.output_path)}\n"
            f"📁 {os.path.dirname(result.output_path)}"
            f"{warning_text}\n\n"
            "Open the file now?",
        )
        if open_now:
            try:
                os.startfile(result.output_path)   # Windows — opens with default app
            except AttributeError:
                # macOS / Linux fallback
                import subprocess
                subprocess.Popen(["xdg-open", result.output_path])

    def _on_conversion_error(self, error_msg: str):
        """Called on main thread after a failed conversion."""
        self._converting = False
        self._btn_convert.config(
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
        """Update the status bar."""
        self._status.set(message, level)
