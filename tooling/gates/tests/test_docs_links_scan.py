#!/usr/bin/env python3
"""Tests for the docs-link scanner (PleaNP #171).

The scanner used to be undiscriminating: it flagged every bare/partial Lean
basename cited in `docs/` (32 false positives) and missed comma-list line-cites,
so it exited 1 on a `main` that was in fact clean. These tests pin the
resolution rules that calibrate it, and — because a check that cannot fail is
not a check — pin that a genuinely missing reference is still caught.

Run: python3 tooling/gates/tests/test_docs_links_scan.py
"""
import sys
import unittest
from pathlib import Path

GATE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GATE_DIR))

import docs_links_scan as d  # noqa: E402


class FindRefsTest(unittest.TestCase):
    def test_backtick_ref_found(self):
        self.assertIn("Oracle.lean", d._find_refs("see `Oracle.lean` for"))

    def test_markdown_link_found(self):
        self.assertIn("docs/SPEC.md", d._find_refs("[spec](docs/SPEC.md)"))

    def test_http_link_skipped(self):
        self.assertEqual(d._find_refs("[x](https://example.com/a.md)"), set())

    def test_newline_wrapped_backtick_span_is_not_a_ref(self):
        # A backtick span broken across a Markdown line-wrap is prose, not a ref
        # (the `docs/STATEMENTS/\nSoundness.spec.md` artifact in GATE_REVIEW_NOTES).
        self.assertEqual(d._find_refs("see `docs/STATEMENTS/\nSoundness.spec.md`"), set())


class ResolutionTest(unittest.TestCase):
    doc = d.DOCS / "GATE_REVIEW_NOTES.md"

    def test_bare_basename_that_exists_resolves(self):
        # `Oracle.lean` exists at lean/PleaNP/Computability/OracleSmoke... — pick
        # one known to exist on disk.
        self.assertTrue(d._find_on_disk("OracleSmoke.lean"))

    def test_partial_path_that_exists_resolves(self):
        self.assertTrue(d._find_on_disk("Circuits/AC0.lean"))

    def test_bare_basename_that_does_not_exist_is_broken(self):
        self.assertFalse(d._find_on_disk("NoSuchModuleZZZ.lean"))

    def test_comma_list_line_cite_resolves_to_base(self):
        self.assertEqual(
            d._strip_line_cite("OracleV5Tests.lean:138,155,165"),
            "OracleV5Tests.lean")

    def test_range_line_cite_resolves_to_base(self):
        self.assertEqual(d._strip_line_cite("AC0.lean:10-20"), "AC0.lean")

    def test_json_line_cite_resolves_to_base(self):
        self.assertEqual(
            d._strip_line_cite("churn/barrier-verdict/lemmas.json:2"),
            "churn/barrier-verdict/lemmas.json")

    def test_existing_lean_resolves_via_resolves(self):
        self.assertTrue(d._resolves("OracleSmoke.lean", self.doc))

    def test_missing_lean_is_broken_via_resolves(self):
        self.assertFalse(d._resolves("NoSuchModuleZZZ.lean", self.doc))

    def test_planned_lean_file_is_whitelisted(self):
        self.assertTrue(d._whitelisted("NaturalProofs.lean"))


class ScanOnMainTest(unittest.TestCase):
    def test_main_tree_is_clean(self):
        self.assertEqual(d.scan(), [])


if __name__ == "__main__":
    unittest.main()
