# LLM Output Formatting Utility (Markdown to DOCX Converter)

## 📖 Overview
The **LLM Output Formatting Utility** is a lightweight, standalone desktop GUI application designed to seamlessly convert raw Markdown—such as the output from AI models like Claude, Gemini, or ChatGPT—into beautifully formatted Microsoft Word (`.docx`) documents. 

Rather than relying on crude regular expressions or intermediate HTML, this tool leverages Pandoc's powerful Abstract Syntax Tree (AST) pipeline to ensure complex structures like nested lists, native tables, and fenced code blocks translate perfectly into native Word styles.

---

## 🏗️ Architecture and Tech Stack
- **Frontend GUI:** Built natively using Python's `tkinter`. The interface is styled with a modern dark theme and runs operations asynchronously.
- **Backend Conversion:** Uses `pypandoc` as a wrapper around the Pandoc binary to parse Markdown and generate DOCX files.
- **Watermarking Engine:** A custom `watermark.py` module utilizing `python-docx` and XML (`lxml.etree`) manipulation to inject diagonal VML WordArt directly into document headers.
- **Concurrency:** Conversions are executed in background daemon threads (`threading.Thread`) to ensure the UI remains fully responsive during heavy document processing.

---

## ✨ Core Features

### 1. Robust Markdown Conversion
- **Native AST Parsing:** Flawlessly handles Headers (H1-H6), Bold/Italics/Strikethrough, Bullet and Numbered Lists, Blockquotes, Hyperlinks, and Pipe Tables.
- **Code Syntax Highlighting:** Built-in support for multiple highlight styles for fenced code blocks, including `tango`, `pygments`, `kate`, `monochrome`, `espresso`, `zenburn`, `haddock`, and `breezedark`.

### 2. User-Friendly Interface
- **Clipboard Integration:** "Fetch From Clipboard" button instantly loads text directly from the OS clipboard.
- **Status Tracking:** Real-time status bar updates and pop-up notifications inform users of conversion success or errors.
- **Auto-Dependency Management:** If the underlying Pandoc system binary isn't found, the utility automatically prompts the user and downloads it directly, requiring no manual setup or admin rights.
