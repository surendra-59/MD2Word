"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          LLM Output Formatting Utility — Markdown → DOCX Converter          ║
║                                                                              ║
║  Entry point — delegates to the converter package.                           ║
║                                                                              ║
║  Dependencies:                                                               ║
║    pip install pypandoc python-docx                                          ║
║    Pandoc binary: https://pandoc.org/installing.html                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from converter.app import MarkdownConverterApp


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
