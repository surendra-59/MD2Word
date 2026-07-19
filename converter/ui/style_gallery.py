"""
Style Gallery Component.

Provides a horizontal strip of four sample cards (Heading, Paragraph,
Table, Code) that instantly reflect changes to the AppSettings.
"""

import tkinter as tk
import tkinter.font as tkfont
from converter.config.defaults import PALETTE
from converter.config.settings import AppSettings
from converter.config.themes import THEME_COLORS, resolve_code_font

class StyleGallery(tk.Frame):
    def __init__(self, parent: tk.Widget, settings: AppSettings):
        super().__init__(parent, bg=PALETTE["bg_root"])
        self._settings = settings

        # Label
        lbl = tk.Label(
            self,
            text="Style Preview",
            font=("Segoe UI", 9, "bold"),
            fg=PALETTE["text_primary"],
            bg=PALETTE["bg_root"],
            anchor="w"
        )
        lbl.pack(side=tk.TOP, fill=tk.X, pady=(10, 5))

        # Container for cards
        self._card_container = tk.Frame(self, bg=PALETTE["bg_root"])
        self._card_container.pack(side=tk.TOP, fill=tk.X, expand=True)

        self._heading_canvas = self._create_card("Heading")
        self._paragraph_canvas = self._create_card("Paragraph")
        self._table_canvas = self._create_card("Table")
        self._code_canvas = self._create_card("Code Block")

        self.refresh()

    def _create_card(self, title: str) -> tk.Canvas:
        frame = tk.Frame(self._card_container, bg=PALETTE["bg_frame"], padx=5, pady=5)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        lbl = tk.Label(frame, text=title, font=("Segoe UI", 8), fg=PALETTE["text_secondary"], bg=PALETTE["bg_frame"])
        lbl.pack(side=tk.TOP, anchor="w")
        
        canvas = tk.Canvas(frame, width=190, height=110, bg="#FFFFFF", highlightthickness=0)
        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(5, 0))
        return canvas

    def refresh(self, *args) -> None:
        self._render_heading_sample()
        self._render_paragraph_sample()
        self._render_table_sample()
        self._render_code_sample()

    def _render_heading_sample(self):
        c = self._heading_canvas
        c.delete("all")
        c.configure(bg="#FFFFFF")
        c.create_text(10, 20, text="Heading 1", font=("Cambria", 16, "bold"), fill="#2F5496", anchor="nw")
        c.create_text(10, 50, text="Heading 2", font=("Cambria", 13, "bold"), fill="#2F5496", anchor="nw")
        c.create_text(10, 75, text="Heading 3", font=("Cambria", 11, "bold"), fill="#1F3763", anchor="nw")

    def _render_paragraph_sample(self):
        c = self._paragraph_canvas
        c.delete("all")
        c.configure(bg="#FFFFFF")
        
        text = "Lorem ipsum dolor sit amet,\nconsectetur adipiscing elit.\nSed do eiusmod tempor\nincididunt ut labore."
        if self._settings.smart_typography:
            text = text.replace("Lorem", "“Lorem”")
            text = text.replace("-", "—")
            
        c.create_text(10, 15, text=text, font=("Calibri", 10), fill="#000000", anchor="nw", justify=tk.LEFT)

    def _render_table_sample(self):
        c = self._table_canvas
        c.delete("all")
        c.configure(bg="#FFFFFF")
        
        # Draw a small 3x3 table
        col_widths = [50, 50, 50]
        row_height = 20
        start_x = 10
        start_y = 10
        
        # Header shading
        c.create_rectangle(start_x, start_y, start_x + sum(col_widths), start_y + row_height, fill="#D9D9D9", outline="")
        
        # Alternating shading
        if self._settings.table_alternating_shading:
            c.create_rectangle(start_x, start_y + row_height*2, start_x + sum(col_widths), start_y + row_height*3, fill="#F2F2F2", outline="")
            
        # Lines
        for i in range(4): # 4 rows
            y = start_y + i * row_height
            c.create_line(start_x, y, start_x + sum(col_widths), y, fill="#808080")
            
        for i in range(4): # 4 cols
            x = start_x + sum(col_widths[:i])
            c.create_line(x, start_y, x, start_y + row_height*3, fill="#808080")
            
        # Text
        font = ("Calibri", 9)
        bold_font = ("Calibri", 9, "bold")
        for i, header in enumerate(["Col 1", "Col 2", "Col 3"]):
            c.create_text(start_x + sum(col_widths[:i]) + 5, start_y + 3, text=header, font=bold_font, anchor="nw")
            
        for r in range(1, 3):
            for i, val in enumerate(["Data", "Data", "Data"]):
                c.create_text(start_x + sum(col_widths[:i]) + 5, start_y + r*row_height + 3, text=val, font=font, anchor="nw")

    def _render_code_sample(self):
        c = self._code_canvas
        c.delete("all")
        
        theme_name = self._settings.highlight_style
        # Default to tango if not found
        theme = THEME_COLORS.get(theme_name, THEME_COLORS.get("tango"))
        if not theme:
            return
            
        bg_color = theme.background
        # Handle 'None' background
        if self._settings.code_bg_color.lower() == "none" or not self._settings.code_bg_color:
             bg_color = "#FFFFFF" # Default word background
        
        c.configure(bg=bg_color)
        
        # Draw border
        if self._settings.code_border_visible:
            c.create_rectangle(2, 2, 188, 108, outline="#D9D9D9", width=1)
            
        # Setup font
        font_family = resolve_code_font(self._settings.code_font)
        # Scale down font size for preview canvas if it's very large
        font_size = min(max(self._settings.code_font_size - 2, 6), 11)
        font = (font_family, font_size)
        
        line_spacing = self._settings.code_line_spacing
        line_height = int(font_size * 1.5 * line_spacing)
        
        start_y = 10
        start_x = 10
        
        # Line numbers
        if self._settings.code_line_numbers:
            c.create_text(start_x, start_y, text="1\n2\n3", font=font, fill="#888888", anchor="nw")
            start_x += 20
            
        # Render tokens
        # def hello(name="world"):
        #     print("Hello " + name)
        #     return 42
        
        c.create_text(start_x, start_y, text="def", font=(font_family, font_size, "bold"), fill=theme.keyword, anchor="nw")
        c.create_text(start_x + 25, start_y, text=" hello(name=", font=font, fill=theme.foreground, anchor="nw")
        c.create_text(start_x + 95, start_y, text='"world"', font=font, fill=theme.string, anchor="nw")
        c.create_text(start_x + 145, start_y, text="):", font=font, fill=theme.foreground, anchor="nw")
        
        start_y += line_height
        c.create_text(start_x + 15, start_y, text="print(", font=font, fill=theme.foreground, anchor="nw")
        c.create_text(start_x + 55, start_y, text='"Hello "', font=font, fill=theme.string, anchor="nw")
        c.create_text(start_x + 105, start_y, text="+ name)", font=font, fill=theme.foreground, anchor="nw")
        
        start_y += line_height
        c.create_text(start_x + 15, start_y, text="return ", font=(font_family, font_size, "bold"), fill=theme.keyword, anchor="nw")
        c.create_text(start_x + 60, start_y, text="42", font=font, fill=theme.number, anchor="nw")
