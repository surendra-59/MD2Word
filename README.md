# Markdown to DOCX Converter

A standalone, lightweight Python GUI utility that accepts raw Markdown copy-pasted from AI chatbots (Claude, OpenAI, Gemini) and converts it into a beautifully formatted Microsoft Word (`.docx`) document. 

Built using standard `tkinter` and `pypandoc`, this tool leverages Pandoc's native Abstract Syntax Tree (AST) parsing. Unlike crude regular expressions or HTML converters, this guarantees that complex elements like nested lists, pipe tables, and fenced code blocks translate perfectly into native Microsoft Word styles.

## 📄 Conversion Quality Comparison

See the difference before and after using the converter:

- [Without_MD2WORD_CONVERTER.docx](Testing_Files_For_MD2WORD/Without_MD2WORD_CONVERTER.docx) — Standard Markdown to Word conversion.
- [With_MD2WORD_CONVERTER.docx](Testing_Files_For_MD2WORD/With_MD2WORD_CONVERTER.docx) — Generated with this application, preserving headings, tables, lists, code blocks, and professional formatting.

Click either document to preview or download it directly from GitHub.

## Features

- **Clipboard Integration:** "One-click" fetch feature automatically grabs text directly from your OS clipboard.
- **Native AST Parsing:** Flawlessly handles Headers, Bold/Italics, Bullet Points, Blockquotes, and Native Word Tables.
- **Syntax Highlighting:** Choose between multiple built-in code highlighting themes (`tango`, `zenburn`, `pygments`, etc.) for your fenced code blocks.
- **Auto-Download:** If the underlying Pandoc system binary isn't found, the utility will automatically prompt you and download it directly from the official source, without requiring admin rights.
- **Custom Templates:** Supports `--reference-doc` to allow you to inherit your company's official corporate Word style template.
- **Threaded UI:** Conversion runs in a background daemon thread, ensuring the UI remains smooth and responsive, even for massive documents.

## Screenshots

*(Add your screenshots here!)*

---

## Installation & Setup (For Developers)

### Prerequisites

- Python 3.8+
- The `pypandoc` package

### 1. Clone the repository

```bash
git clone https://github.com/your-username/markdown-to-docx-converter.git
cd markdown-to-docx-converter
```

### 2. Install dependencies

```bash
pip install pypandoc
```

### 3. Run the application

```bash
python app.py
```
*(On first run, if you don't have Pandoc installed on your system, the app will ask you if you want it to automatically download the Pandoc binary.)*

---

## Building a Standalone Executable (Windows/Linux/macOS)

You can package this utility into a single, double-clickable executable file using `PyInstaller`. This bundles Python, Tkinter, and `pypandoc` so you can share it with users who do not have Python installed.

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the app:
```bash
pyinstaller --noconsole --onefile --name "MarkdownToWord" app.py
```

3. Find your executable in the generated `dist/` folder. You can safely share this file; no installation is required!

---

## Customizing Word Styles (Corporate Templates)

By default, Pandoc maps Markdown elements to standard Word styles (e.g., `# Header 1` becomes the "Heading 1" Word style). 

If you want to use a customized template (like your company's branded letterhead with specific fonts and colors):

1. Create a blank Word document.
2. Modify the styles to your liking (Heading 1, Heading 2, Normal, Code Block, etc.).
3. Save it as `style_template.docx` in the same folder as `app.py`.
4. Open `app.py` and navigate to the `_run_conversion` function.
5. Uncomment the following line inside the `extra_args` list:
   ```python
   # "--reference-doc=style_template.docx",
   ```
6. Re-run the script. Every conversion will now inherit your custom styles automatically!

---

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it as you see fit.
