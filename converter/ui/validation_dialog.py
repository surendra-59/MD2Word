"""
Validation dialog — modal warning window shown before conversion.

Displays a scrollable list of ``ValidationIssue`` objects with severity
icons, line numbers, messages, and suggestions.  The user can choose
to **Convert Anyway** or **Cancel**.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Literal

from converter.config.defaults import PALETTE
from converter.core.validator import ValidationIssue


# Severity → (icon, color)
_SEVERITY_MAP = {
    "error":   ("🔴", "#FC8181"),
    "warning": ("🟡", "#F6E05E"),
    "info":    ("🔵", "#76E4F7"),
}


class ValidationDialog(tk.Toplevel):
    """
    A modal dialog that presents validation issues to the user.

    Usage::

        dialog = ValidationDialog(parent, issues)
        parent.wait_window(dialog)
        if dialog.result == "continue":
            # proceed with conversion
        else:
            # user cancelled
    """

    def __init__(
        self,
        parent: tk.Tk,
        issues: list[ValidationIssue],
    ) -> None:
        super().__init__(parent)
        self.result: Literal["continue", "cancel"] = "cancel"

        self.title("Markdown Validation Results")
        self.configure(bg=PALETTE["bg_frame"])
        self.resizable(True, True)
        self.minsize(500, 300)
        self.geometry("600x420")

        # Make it modal
        self.transient(parent)
        self.grab_set()

        self._issues = issues
        self._build_ui()

        # Center on parent
        self.update_idletasks()
        pw = parent.winfo_x() + parent.winfo_width() // 2
        ph = parent.winfo_y() + parent.winfo_height() // 2
        w = self.winfo_width()
        h = self.winfo_height()
        self.geometry(f"+{pw - w // 2}+{ph - h // 2}")

        # Handle window close as cancel
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _build_ui(self) -> None:
        """Construct the dialog layout."""

        # ── Header ────────────────────────────────────────────────────────
        error_count   = sum(1 for i in self._issues if i.severity == "error")
        warning_count = sum(1 for i in self._issues if i.severity == "warning")
        info_count    = sum(1 for i in self._issues if i.severity == "info")

        summary_parts = []
        if error_count:
            summary_parts.append(f"🔴 {error_count} error(s)")
        if warning_count:
            summary_parts.append(f"🟡 {warning_count} warning(s)")
        if info_count:
            summary_parts.append(f"🔵 {info_count} info")

        header = tk.Label(
            self,
            text="  Validation Issues Found",
            font=("Segoe UI", 12, "bold"),
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_frame"],
            anchor="w",
        )
        header.pack(fill="x", padx=16, pady=(14, 2))

        summary = tk.Label(
            self,
            text="  " + "   ".join(summary_parts),
            font=("Segoe UI", 9),
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_frame"],
            anchor="w",
        )
        summary.pack(fill="x", padx=16, pady=(0, 8))

        # ── Separator ────────────────────────────────────────────────────
        sep = tk.Frame(self, bg=PALETTE["accent_slate"], height=1)
        sep.pack(fill="x", padx=12)

        # ── Scrollable issues list ───────────────────────────────────────
        list_frame = tk.Frame(self, bg=PALETTE["bg_editor"])
        list_frame.pack(fill="both", expand=True, padx=12, pady=8)

        canvas = tk.Canvas(
            list_frame,
            bg=PALETTE["bg_editor"],
            highlightthickness=0,
            bd=0,
        )
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=canvas.yview
        )
        scrollable = tk.Frame(canvas, bg=PALETTE["bg_editor"])

        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ── Populate issue rows ──────────────────────────────────────────
        for idx, issue in enumerate(self._issues):
            self._build_issue_row(scrollable, issue, idx)

        # ── Button bar ───────────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=PALETTE["bg_frame"])
        btn_frame.pack(fill="x", padx=12, pady=(0, 12))

        # Cancel button
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=("Segoe UI", 10, "bold"),
            bg=PALETTE["accent_red"],
            fg="#FFFFFF",
            activebackground="#FC8181",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._on_cancel,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        # Convert Anyway button
        convert_btn = tk.Button(
            btn_frame,
            text="⚡  Convert Anyway",
            font=("Segoe UI", 10, "bold"),
            bg=PALETTE["accent_indigo"],
            fg="#FFFFFF",
            activebackground=PALETTE["accent_indigo_hover"],
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._on_continue,
        )
        convert_btn.pack(side="right")

    def _build_issue_row(
        self, parent: tk.Frame, issue: ValidationIssue, idx: int
    ) -> None:
        """Build a single issue row in the scrollable list."""
        icon, color = _SEVERITY_MAP.get(issue.severity, ("❓", PALETTE["text_secondary"]))

        # Alternate row background for readability
        bg = PALETTE["bg_editor"] if idx % 2 == 0 else PALETTE["bg_frame"]

        row = tk.Frame(parent, bg=bg, padx=8, pady=6)
        row.pack(fill="x", padx=2, pady=1)

        # Icon + severity
        icon_lbl = tk.Label(
            row,
            text=icon,
            font=("Segoe UI", 11),
            bg=bg,
            anchor="w",
        )
        icon_lbl.pack(side="left", padx=(0, 8))

        # Content frame (message + suggestion)
        content = tk.Frame(row, bg=bg)
        content.pack(side="left", fill="x", expand=True)

        # Line number prefix
        line_prefix = f"Line {issue.line}: " if issue.line else ""

        msg_lbl = tk.Label(
            content,
            text=f"{line_prefix}{issue.message}",
            font=("Segoe UI", 9),
            fg=color,
            bg=bg,
            anchor="w",
            wraplength=450,
            justify="left",
        )
        msg_lbl.pack(anchor="w")

        if issue.suggestion:
            sug_lbl = tk.Label(
                content,
                text=f"💡 {issue.suggestion}",
                font=("Segoe UI", 8),
                fg=PALETTE["text_secondary"],
                bg=bg,
                anchor="w",
                wraplength=450,
                justify="left",
            )
            sug_lbl.pack(anchor="w", pady=(2, 0))

    def _on_continue(self) -> None:
        """User chose to convert despite warnings."""
        self.result = "continue"
        self.grab_release()
        self.destroy()

    def _on_cancel(self) -> None:
        """User cancelled the conversion."""
        self.result = "cancel"
        self.grab_release()
        self.destroy()
