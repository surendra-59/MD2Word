# Markdown to DOCX Converter — Architecture Analysis

## 1. Overview
The **LLM Output Formatting Utility** is a Tkinter-based desktop application that converts Markdown text (from LLMs like Claude or ChatGPT) into heavily styled Microsoft Word (`.docx`) files. 

It leverages **Pandoc** (via the `pypandoc` wrapper) for AST-based document parsing and generation, and uses **python-docx** for post-processing enhancements (tables, code styling, checklists).

## 2. Technical Stack
- **Language**: Python 3.8+
- **GUI Framework**: Tkinter (Standard Library)
- **Core Dependencies**:
  - `pypandoc` (Wrapper for Pandoc binary)
  - `python-docx` (XML manipulation of the generated Word document)
- **Build System**: PyInstaller (`MarkdownToWord.spec`)

## 3. Directory Structure
The application has recently been refactored from a monolithic `app.py` into a modular package structure:

```
Markdown_Converter/
├── app.py                          ← Thin entry point launcher
├── MarkdownToWord.spec             ← PyInstaller spec
├── config.json                     ← User preferences (auto-generated)
│
├── converter/                      ← Main application package
│   ├── app.py                      ← MarkdownConverterApp (main Tkinter window)
│   │
│   ├── config/                     
│   │   ├── defaults.py             ← Color PALETTE and UI constants
│   │   ├── settings.py             ← AppSettings dataclass (JSON load/save)
│   │   └── themes.py               ← Highlight themes mapping and fallback fonts
│   │
│   ├── ui/                         
│   │   ├── banner.py               ← Header UI
│   │   ├── editor.py               ← ScrolledText markdown editor
│   │   ├── options_panel.py        ← Dropdowns for highlight style and filename
│   │   ├── button_bar.py           ← Clipboard, Clear, Convert buttons
│   │   └── status_bar.py           ← Bottom status indicator
│   │
│   └── core/                       
│       ├── pipeline.py             ← Orchestrates the full conversion process
│       ├── preprocessor.py         ← Normalizes aliases, fixes checkboxes
│       ├── postprocessor.py        ← Python-docx XML manipulation (tables/code)
│       └── language_aliases.py     ← Maps 'py' -> 'python', etc.
```

## 4. Conversion Pipeline (`converter.core.pipeline.ConversionPipeline`)
The conversion operates on a background daemon thread to keep the UI responsive. It involves four main stages:

1. **Validation** (Upcoming Phase): Scans for unclosed code blocks, malformed tables, missing images, and alerts the user.
2. **Pre-processing** (`preprocessor.py`): 
   - Normalizes fenced code block languages (e.g., `py` to `python`) using `language_aliases.py`.
   - Modifies GFM task list markers if older Pandoc versions are detected.
3. **Pandoc Conversion** (`pypandoc`): 
   - Uses format extensions: `+pipe_tables`, `+task_lists`, `+strikeout`, `+footnotes`, `+smart`, `+tex_math_dollars`.
   - Transforms Markdown AST directly into a `.docx` file using native Word styles.
4. **Post-processing** (`postprocessor.py`):
   - **Tables**: Auto-fits to window, repeats header rows across pages, applies borders, and adds alternating row shading.
   - **Task Lists**: Changes Unicode checkboxes into Wingdings characters for native Word support.
   - **Code Blocks**: Adjusts the `Source Code` paragraph style to apply custom fonts, backgrounds, borders, line spacing, and keep-together rules.

## 5. UI Architecture
- **State Management**: The UI components interact with a central `AppSettings` dataclass.
- **Asynchrony**: `_start_conversion` spawns a `threading.Thread`. Operations in the thread send UI updates back to the main event loop using `self.after()`.
- **Styling**: The app uses a dark theme with manual canvas drawing for gradients and `ttk` styling for comboboxes.

## 6. Important Notes for Future Development
- When editing UI components, remember that the root application `MarkdownConverterApp` manages the instantiation in `_build_ui()`.
- The `python-docx` modifications in `postprocessor.py` rely heavily on XML manipulation (`OxmlElement`, `qn`) because standard `python-docx` API lacks certain features (like `<w:tblHeader/>` for repeating headers or `<w:shd>` for paragraph backgrounds).
- Future additions include an expanded `options_panel.py` (multi-tabbed using `ttk.Notebook`) and a `style_gallery.py` for rendering live style previews on Tkinter Canvases.
