"""
Conversion pipeline — orchestrates the full Markdown → DOCX workflow.

    Validate → Pre-process → Pandoc Convert → Post-process

This module replaces the inline ``_run_conversion()`` logic in the
original monolithic ``app.py``.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from typing import Callable, Optional

import pypandoc

from converter.config.settings import AppSettings
from converter.core.preprocessor import preprocess
from converter.core.postprocessor import postprocess


@dataclass
class ConversionResult:
    """Outcome of a conversion run."""
    success: bool
    output_path: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    unknown_languages: list[str] = field(default_factory=list)
    error_message: Optional[str] = None


class ConversionPipeline:
    """
    Stateless conversion orchestrator.

    Construct once with the current ``AppSettings``, then call
    ``convert()`` from the worker thread.
    """

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._pandoc_version: Optional[str] = None
        self._supported_languages: Optional[set[str]] = None

    # ------------------------------------------------------------------
    #  Pandoc introspection (lazy, cached)
    # ------------------------------------------------------------------

    def _get_pandoc_version(self) -> str:
        if self._pandoc_version is None:
            try:
                self._pandoc_version = pypandoc.get_pandoc_version()
            except OSError:
                self._pandoc_version = "0.0.0"
        return self._pandoc_version

    def _get_supported_languages(self) -> set[str]:
        """
        Query Pandoc for the list of languages it can highlight.
        Cached after the first call.
        """
        if self._supported_languages is None:
            try:
                result = subprocess.run(
                    ["pandoc", "--list-highlight-languages"],
                    capture_output=True, text=True, timeout=10,
                )
                self._supported_languages = {
                    lang.strip().lower()
                    for lang in result.stdout.splitlines()
                    if lang.strip()
                }
            except Exception:
                self._supported_languages = set()
        return self._supported_languages

    # ------------------------------------------------------------------
    #  Format string construction
    # ------------------------------------------------------------------

    def _build_format_string(self) -> str:
        """
        Construct the Pandoc input format string with the appropriate
        extensions enabled.
        """
        extensions = [
            "+pipe_tables",
            "+strikeout",
            "+footnotes",
            "+fenced_code_blocks",
            "+backtick_code_blocks",
            "+fenced_code_attributes",
            "+inline_code_attributes",
            "+definition_lists",
            "+yaml_metadata_block",
            "+tex_math_dollars",
        ]

        # Smart typography
        if self._settings.smart_typography:
            extensions.append("+smart")

        # Task lists (Pandoc ≥ 2.6)
        version = self._get_pandoc_version()
        if self._version_gte(version, "2.6"):
            extensions.append("+task_lists")

        return "markdown" + "".join(extensions)

    @staticmethod
    def _version_gte(version: str, threshold: str) -> bool:
        """Return True if *version* ≥ *threshold*."""
        def _parts(v: str) -> list[int]:
            return [int(x) for x in re.findall(r"\d+", v)]
        return _parts(version) >= _parts(threshold)

    # ------------------------------------------------------------------
    #  Main conversion
    # ------------------------------------------------------------------

    def convert(
        self,
        markdown_text: str,
        output_path: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ConversionResult:
        """
        Execute the full conversion pipeline.

        This runs in the **worker thread** — never call Tk methods
        directly from here.

        Parameters
        ----------
        markdown_text : str
            Raw Markdown from the editor.
        output_path : str
            Destination ``.docx`` file path.
        progress_callback : callable | None
            Optional ``fn(status_message)`` called at each stage.

        Returns
        -------
        ConversionResult
        """
        warnings: list[str] = []

        try:
            # ── 1. Pre-process ────────────────────────────────────────
            if progress_callback:
                progress_callback("Pre-processing Markdown…")

            pre_result = preprocess(
                markdown=markdown_text,
                settings=self._settings,
                supported_languages=self._get_supported_languages(),
                pandoc_version=self._get_pandoc_version(),
            )
            processed_md = pre_result.markdown
            unknown_langs = pre_result.unknown_languages

            if unknown_langs:
                warnings.append(
                    f"Unknown language(s): {', '.join(unknown_langs)} "
                    "— code will be formatted without highlighting."
                )

            # ── 2. Pandoc conversion ──────────────────────────────────
            if progress_callback:
                progress_callback("Converting with Pandoc…")

            input_format = self._build_format_string()
            highlight = self._settings.highlight_style

            extra_args = [
                f"--highlight-style={highlight}",
                "--standalone",
            ]

            pypandoc.convert_text(
                source=processed_md,
                to="docx",
                format=input_format,
                outputfile=output_path,
                extra_args=extra_args,
            )

            # ── 3. Post-process ───────────────────────────────────────
            if progress_callback:
                progress_callback("Applying document enhancements…")

            postprocess(output_path, self._settings)

            return ConversionResult(
                success=True,
                output_path=output_path,
                warnings=warnings,
                unknown_languages=unknown_langs,
            )

        except Exception as exc:
            return ConversionResult(
                success=False,
                error_message=str(exc),
                warnings=warnings,
            )
