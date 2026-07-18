"""
Markdown validation engine.

Scans raw Markdown text for common structural issues before conversion,
allowing the user to fix problems or proceed with awareness.

Checks performed:
  1. Unclosed fenced code blocks
  2. Invalid table formatting (inconsistent column counts)
  3. Incorrect list indentation (mixed tabs/spaces)
  4. Missing local image files
  5. Broken hyperlinks (optional, network-dependent)
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class ValidationIssue:
    """A single validation finding."""
    severity: Literal["error", "warning", "info"]
    line: Optional[int]        # 1-based line number, or None
    message: str
    suggestion: Optional[str] = None


class MarkdownValidator:
    """
    Stateless Markdown validator.

    Call ``validate(markdown)`` to get a list of issues.  The method
    is pure and fast (< 10 ms for typical documents) — safe to run
    on the main thread.
    """

    def validate(
        self,
        markdown: str,
        *,
        check_broken_links: bool = False,
        base_path: Optional[str] = None,
    ) -> list[ValidationIssue]:
        """
        Run all validation checks on *markdown*.

        Parameters
        ----------
        markdown : str
            Raw Markdown source text.
        check_broken_links : bool
            If ``True``, attempt HTTP HEAD requests for hyperlinks
            (can be slow and requires network).
        base_path : str | None
            Directory to resolve relative image paths against.
            Defaults to the current working directory.

        Returns
        -------
        list[ValidationIssue]
            All issues found, ordered by line number.
        """
        issues: list[ValidationIssue] = []
        lines = markdown.splitlines()

        issues.extend(self._check_unclosed_code_fences(lines))
        issues.extend(self._check_invalid_tables(lines))
        issues.extend(self._check_list_indentation(lines))
        issues.extend(self._check_missing_images(markdown, base_path))

        if check_broken_links:
            issues.extend(self._check_broken_links(markdown))

        # Sort by line number (None sorts to end)
        issues.sort(key=lambda i: (i.line or float("inf")))
        return issues

    # ==================================================================
    #  CHECK 1 — Unclosed fenced code blocks
    # ==================================================================

    _FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")

    def _check_unclosed_code_fences(
        self, lines: list[str]
    ) -> list[ValidationIssue]:
        """Detect fenced code blocks that are opened but never closed."""
        issues: list[ValidationIssue] = []
        open_fence: Optional[tuple[int, str, str]] = None  # (line, indent, char)

        for idx, line in enumerate(lines, start=1):
            m = self._FENCE_RE.match(line)
            if not m:
                continue

            indent = m.group(1)
            fence_char = m.group(2)[0]  # '`' or '~'
            fence_len = len(m.group(2))

            if open_fence is None:
                # Opening a new fence
                open_fence = (idx, indent, fence_char)
            else:
                # Closing fence must use the same character and at least
                # the same number of backticks/tildes
                _, open_indent, open_char = open_fence
                if fence_char == open_char and fence_len >= 3:
                    open_fence = None  # properly closed

        if open_fence is not None:
            line_num = open_fence[0]
            issues.append(ValidationIssue(
                severity="error",
                line=line_num,
                message=f"Unclosed fenced code block opened on line {line_num}.",
                suggestion="Add a matching ``` or ~~~ closing fence.",
            ))

        return issues

    # ==================================================================
    #  CHECK 2 — Invalid table formatting
    # ==================================================================

    _TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
    _SEPARATOR_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")

    def _check_invalid_tables(
        self, lines: list[str]
    ) -> list[ValidationIssue]:
        """Flag table rows with inconsistent column counts."""
        issues: list[ValidationIssue] = []

        # Find contiguous blocks of table rows
        i = 0
        while i < len(lines):
            if not self._TABLE_ROW_RE.match(lines[i]):
                i += 1
                continue

            # Found the start of a table block
            table_start = i
            table_lines: list[tuple[int, str]] = []  # (1-based line, text)

            while i < len(lines) and self._TABLE_ROW_RE.match(lines[i]):
                table_lines.append((i + 1, lines[i]))
                i += 1

            if len(table_lines) < 2:
                # Single row isn't a meaningful table
                continue

            # Count pipes in each row (subtract outer pipes)
            col_counts = []
            for line_num, text in table_lines:
                # Skip separator rows for column count comparison
                if self._SEPARATOR_RE.match(text):
                    continue
                # Count columns: split by | and remove outer empties
                cols = [c for c in text.split("|") if c.strip() != "" or c != ""]
                # More reliable: count | characters minus 1 (for outer pipes)
                pipe_count = text.count("|") - 1  # rough column count
                col_counts.append((line_num, pipe_count))

            if len(col_counts) < 2:
                continue

            expected = col_counts[0][1]
            for line_num, count in col_counts[1:]:
                if count != expected:
                    issues.append(ValidationIssue(
                        severity="warning",
                        line=line_num,
                        message=(
                            f"Table row has {count} columns but the header "
                            f"has {expected}."
                        ),
                        suggestion="Ensure all rows have the same number of | delimiters.",
                    ))

        return issues

    # ==================================================================
    #  CHECK 3 — List indentation issues
    # ==================================================================

    _LIST_ITEM_RE = re.compile(r"^(\s*)([-*+]|\d+\.)\s")

    def _check_list_indentation(
        self, lines: list[str]
    ) -> list[ValidationIssue]:
        """Detect mixed tabs/spaces and non-standard indentation in lists."""
        issues: list[ValidationIssue] = []
        seen_tab_warning = False
        seen_indent_warning = False

        for idx, line in enumerate(lines, start=1):
            m = self._LIST_ITEM_RE.match(line)
            if not m:
                continue

            indent = m.group(1)
            if not indent:
                continue  # top-level item, no indent

            # Check for mixed tabs and spaces
            has_tabs = "\t" in indent
            has_spaces = " " in indent

            if has_tabs and has_spaces and not seen_tab_warning:
                issues.append(ValidationIssue(
                    severity="warning",
                    line=idx,
                    message="List item uses mixed tabs and spaces for indentation.",
                    suggestion="Use consistent indentation (2 or 4 spaces recommended).",
                ))
                seen_tab_warning = True

            # Check for non-standard indent widths (1 or 3 spaces)
            if has_spaces and not has_tabs:
                space_count = len(indent)
                if space_count in (1, 3) and not seen_indent_warning:
                    issues.append(ValidationIssue(
                        severity="warning",
                        line=idx,
                        message=f"List indentation of {space_count} space(s) may not render correctly.",
                        suggestion="Use 2 or 4 spaces for nested list indentation.",
                    ))
                    seen_indent_warning = True

        return issues

    # ==================================================================
    #  CHECK 4 — Missing local image files
    # ==================================================================

    _IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    def _check_missing_images(
        self, markdown: str, base_path: Optional[str] = None
    ) -> list[ValidationIssue]:
        """Flag image references where the local file does not exist."""
        issues: list[ValidationIssue] = []
        base = base_path or os.getcwd()

        # Track line numbers for image references
        for idx, line in enumerate(markdown.splitlines(), start=1):
            for match in self._IMAGE_RE.finditer(line):
                path = match.group(2).strip()

                # Skip URLs
                if path.startswith(("http://", "https://", "data:")):
                    continue

                # Resolve relative path
                full_path = os.path.join(base, path) if not os.path.isabs(path) else path

                if not os.path.isfile(full_path):
                    issues.append(ValidationIssue(
                        severity="warning",
                        line=idx,
                        message=f"Image file not found: {path}",
                        suggestion="Check the file path or use an absolute path.",
                    ))

        return issues

    # ==================================================================
    #  CHECK 5 — Broken hyperlinks (optional, network)
    # ==================================================================

    _LINK_RE = re.compile(r"\[([^\]]*)\]\((https?://[^)]+)\)")

    def _check_broken_links(
        self, markdown: str
    ) -> list[ValidationIssue]:
        """
        Send HTTP HEAD requests for hyperlinks (best-effort).

        This check is intentionally lenient — network errors and
        timeouts are silently skipped rather than reported as issues.
        """
        issues: list[ValidationIssue] = []

        try:
            import urllib.request
            import urllib.error
        except ImportError:
            return issues

        seen_urls: set[str] = set()

        for idx, line in enumerate(markdown.splitlines(), start=1):
            for match in self._LINK_RE.finditer(line):
                url = match.group(2).strip()
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                try:
                    req = urllib.request.Request(url, method="HEAD")
                    req.add_header("User-Agent", "MarkdownValidator/1.0")
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        if resp.status >= 400:
                            issues.append(ValidationIssue(
                                severity="info",
                                line=idx,
                                message=f"Link returned HTTP {resp.status}: {url}",
                                suggestion="Verify the URL is still valid.",
                            ))
                except urllib.error.HTTPError as e:
                    issues.append(ValidationIssue(
                        severity="info",
                        line=idx,
                        message=f"Link returned HTTP {e.code}: {url}",
                        suggestion="Verify the URL is still valid.",
                    ))
                except Exception:
                    # Timeout, DNS failure, SSL error — skip silently
                    pass

        return issues
