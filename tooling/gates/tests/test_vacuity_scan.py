#!/usr/bin/env python3
"""Unit tests for the Gate 5 vacuity scanner's comment-stripping (issue #60).

Regression-guards the shared docstring-strip regex fix: the old
`/-.*? -/` (requires a space before `-/`) missed Mathlib-convention
docstrings that close with ``\\n-/`` and could over-strip real code.
Now uses the blanking approach from binder_usage_scan (issue #60).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vacuity_scan  # noqa: E402


class TestStripComments(unittest.TestCase):
    MATHLIB_DOCSTRING = """/-!
A docstring that closes with a newline before the closer,
as the Mathlib convention does.
-/
def realDef : Nat := 1
"""

    def test_mathlib_nl_docstring_closer_is_stripped(self):
        out = vacuity_scan._strip_comments(self.MATHLIB_DOCSTRING)
        self.assertNotIn("docstring", out)
        self.assertIn("def realDef : Nat := 1", out)
        # Comments blanked, not deleted: output has same length as input.
        self.assertEqual(len(out), len(self.MATHLIB_DOCSTRING))

    def test_real_code_after_docstring_preserved(self):
        src = self.MATHLIB_DOCSTRING + "theorem t : True := by trivial\n"
        out = vacuity_scan._strip_comments(src)
        self.assertIn("theorem t : True", out)
        self.assertIn("def realDef", out)

    def test_line_numbers_preserved(self):
        src = "line1\n" + self.MATHLIB_DOCSTRING + "lineN\n"
        out = vacuity_scan._strip_comments(src)
        # 'def realDef' must appear on the same line number as in the source.
        src_line = src.split("\n").index("def realDef : Nat := 1")
        out_line = out.split("\n").index("def realDef : Nat := 1")
        self.assertEqual(src_line, out_line)

    def test_line_comment_stripped(self):
        src = "def x : Nat := 1 -- a comment\ntheorem t : True := by trivial\n"
        out = vacuity_scan._strip_comments(src)
        self.assertNotIn("a comment", out)
        self.assertIn("theorem t : True", out)

    def test_overstrip_does_not_happen_mid_file(self):
        # A ` -/` elsewhere must not swallow the rest of the file.
        src = """/-! first docstring -/
def a := 1
/- some comment with ` -/` inside a string -/
def b := 2
"""
        out = vacuity_scan._strip_comments(src)
        self.assertIn("def a := 1", out)
        self.assertIn("def b := 2", out)


class TestPhantomParam(unittest.TestCase):
    """The parameter-occurrence check for structure/class fields (issue #234).

    Reproduces the #224/#226 withdrawn-field shape: a field whose type never
    mentions the enclosing parameter. Uses the mock fixture `case14`, not a
    reintroduction of the vacuous claim into `lean/`.
    """

    FIXTURE = Path(__file__).resolve().parent / "case14_phantom_param.lean"

    def _kinds(self, path: Path) -> list[tuple[str, str]]:
        return [(f.kind, f.decl_name) for f in vacuity_scan.scan_file(path)]

    def test_withdrawn_field_is_flagged(self):
        kinds = self._kinds(self.FIXTURE)
        self.assertIn(("phantom_param", "Withdrawn.simulates"), kinds)
        # The data-carrier sibling field mentions no parameter either, but it is
        # also phantom: `code : Nat` omits M. Both are reported (report-only).
        self.assertIn(("phantom_param", "Withdrawn.code"), kinds)

    def test_clean_structure_not_flagged(self):
        findings = [f for f in vacuity_scan.scan_file(self.FIXTURE)
                    if f.decl_name.startswith("Clean")]
        self.assertEqual(findings, [], f"Clean control flagged: {findings}")

    def test_single_char_param_occurrence(self):
        # A parameter `M` used as a standalone token must count as occurring.
        src = "structure S (M : Nat) where\n  f : Nat -> Nat\n  g : M = M\n"
        findings = vacuity_scan._check_phantom_params("structure", "S", src)
        names = [(f, p) for f, p, _ in findings]
        # `f` omits M (flagged); `g` mentions M (not flagged).
        self.assertIn(("f", "M"), names)
        self.assertNotIn(("g", "M"), names)

    def test_no_false_positive_on_multichar_substring(self):
        # Parameter `M` must not be considered to occur inside identifier `MyType`.
        src = "structure S (M : Nat) where\n  f : MyType -> Nat\n"
        findings = vacuity_scan._check_phantom_params("structure", "S", src)
        self.assertIn(("f", "M"), [(f, p) for f, p, _ in findings])

    def test_class_is_checked_too(self):
        src = "class C (p : Prop) where\n  h : Nat -> Nat\n"
        findings = vacuity_scan._check_phantom_params("class", "C", src)
        self.assertIn(("h", "p"), [(f, p) for f, p, _ in findings])

    def test_non_structure_decl_ignored(self):
        src = "def d (M : Nat) : Nat := 0\n"
        self.assertEqual(vacuity_scan._check_phantom_params("def", "d", src), [])

    def test_field_line_reported(self):
        # The finding points at the offending field line, not the declaration.
        kinds = [(f.kind, f.decl_name, f.line_no)
                 for f in vacuity_scan.scan_file(self.FIXTURE)]
        self.assertIn(("phantom_param", "Withdrawn.simulates", 17), kinds)

    def test_allowlist_suppresses_documented_phantom(self):
        key = ("S", "f", "M")
        vacuity_scan.PHANTOM_PARAM_ALLOWLIST[key] = "test"
        try:
            src = "structure S (M : Nat) where\n  f : Nat -> Nat\n"
            self.assertEqual(vacuity_scan._check_phantom_params("structure", "S", src), [])
        finally:
            del vacuity_scan.PHANTOM_PARAM_ALLOWLIST[key]


if __name__ == "__main__":
    unittest.main(verbosity=2)