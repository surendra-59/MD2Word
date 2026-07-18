# Implementation Tasks — Phases 1–4

## Phase 1 — Foundation (Structural Refactoring) ✅

- `[x]` Create `converter/` package skeleton with `__init__.py` files
- `[x]` Create `converter/config/defaults.py` — move PALETTE, constants, `_lighten()`
- `[x]` Create `converter/config/settings.py` — AppSettings dataclass + JSON persistence
- `[x]` Create `converter/config/themes.py` — theme color metadata
- `[x]` Extract `converter/ui/banner.py`
- `[x]` Extract `converter/ui/editor.py`
- `[x]` Extract `converter/ui/options_panel.py` (keep current simple layout for now)
- `[x]` Extract `converter/ui/button_bar.py`
- `[x]` Extract `converter/ui/status_bar.py`
- `[x]` Create `converter/app.py` — refactored MarkdownConverterApp
- `[x]` Update root `app.py` to thin launcher
- `[x]` Update `MarkdownToWord.spec`
- `[x]` Verify app launches and converts identically

## Phase 2 — Enhanced Markdown Rendering ✅

- `[x]` Create `converter/core/language_aliases.py` — alias map + normalization
- `[x]` Create `converter/core/preprocessor.py` — pre-processing pipeline
- `[x]` Create `converter/core/postprocessor.py` — table, task list, code block enhancements
- `[x]` Create `converter/core/pipeline.py` — conversion orchestrator
- `[x]` Wire pipeline into `converter/app.py` `_run_conversion()`
- `[x]` Verify enhanced conversion with test Markdown

## Phase 3 — Validation Engine ✅

- `[x]` Create `converter/core/validator.py` — MarkdownValidator with 5 checks
- `[x]` Create `converter/ui/validation_dialog.py` — modal warning dialog
- `[x]` Integrate validator into `_start_conversion()` flow
- `[x]` Verify app launches with validation wired in

## Phase 4 — Expanded Options Panel ✅

- `[x]` Rewrite `converter/ui/options_panel.py` with `ttk.Notebook` tabs
- `[x]` Tab 1: General (prefix, smart typography, validate toggle)
- `[x]` Tab 2: Code Style (theme, font, size, spacing, borders, line numbers)
- `[x]` Tab 3: Tables (autofit, header repeat, alternating shading)
- `[x]` Two-way bind all controls to AppSettings
- `[x]` Wire `apply_to_settings()` to sync all new controls
- `[x]` Verify app launches correctly

## Remaining — Phase 5 & 6

- `[ ]` Phase 5: Style Gallery (4 canvas-based preview cards)
- `[ ]` Phase 6: Polish & edge cases (GitHub theme, long code handling, docs update)
