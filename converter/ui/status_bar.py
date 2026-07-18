"""
Status bar at the bottom of the application window.
"""

import tkinter as tk

from converter.config.defaults import PALETTE


class StatusBar:
    """
    A thin status strip showing context messages.

    Call ``set(message, level)`` to update the text and color.
    """

    _COLOR_MAP = {
        "success": PALETTE["text_success"],
        "error":   PALETTE["text_error"],
        "info":    PALETTE["text_info"],
    }

    def __init__(self, parent: tk.Frame) -> None:
        bar = tk.Frame(parent, bg=PALETTE["bg_statusbar"], height=28)
        bar.grid(row=4, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.columnconfigure(0, weight=1)

        self._var = tk.StringVar(value="Ready.")
        self._lbl = tk.Label(
            bar,
            textvariable=self._var,
            font=("Segoe UI", 9),
            fg=PALETTE["text_secondary"],
            bg=PALETTE["bg_statusbar"],
            anchor="w",
            padx=10,
        )
        self._lbl.grid(row=0, column=0, sticky="ew")

    def set(self, message: str, level: str = "info") -> None:
        """
        Update the status bar.

        Parameters
        ----------
        message : str
            Text to display.
        level : str
            ``"success"`` | ``"error"`` | ``"info"`` — controls text color.
        """
        color = self._COLOR_MAP.get(level, PALETTE["text_secondary"])
        self._var.set(message)
        self._lbl.config(fg=color)
