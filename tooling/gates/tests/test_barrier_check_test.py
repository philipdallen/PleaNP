#!/usr/bin/env python3
"""Unit tests for the `#barrier_check` verdict harness (barrier_check_test.py) - stdlib only.

Tests the harness LOGIC (verdict-segment matching, dash tolerance, log-file
exit codes)using fixed sample logs - no Lean toolchain, no secrets. The
real-lake integration is exercised in CI (the build step tees its output and
the harness runs on the captured log) and by the local `--run-lake` path.

Run:
    python3 tooling/gates/tests/test_barrier_check_test.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import barrier_check_test  # noqa: E402


VERDICT_LINES = """
info: PleaNP/Calculus/BarrierCalculus.lean:287:0: #barrier_check PleaNP.Calculus.thhStatement: relativizes, not P-vs-NP-shaped -> Inconclusive as a P-vs-NP blocker.

info: PleaNP/Calculus/BarrierCalculus.lean:288:0: #barrier_check PleaNP.Calculus.abstractPVsNP: DEAD - this proof relativizes,and concludes a P-vs-NP-shaped claim;so BGS rules it out.



info: PleaNP/Calculus/BarrierCalculus.lean:289:0: #barrier_check PleaNP.Calculus.plainRelHeuristic: relativizes, not P-vs-NP-shaped -> Inconclusive as a P-vs-NP blocker.



info: PleaNP/Calculus/BarrierCalculus.lean:298:0: #barrier_check PleaNP.Calculus.nonRelativizingControl: Inconclusive - no Relativizing instanceon this statement;so it is not ruled out by BGS.



info: PleaNP/Calculus/ConcreteSeed.lean:91:0: #barrier_check PleaNP.Calculus.concreteClassMembership: DEAD - this proof relativizes,and concludes a P-vs-NP-shaped claim;so BGS rules it out.



info: PleaNP/Calculus/ConcreteSeed.lean:92:0: #barrier_check PleaNP.Calculus.bgsMetaStatement: Inconclusive - no Relativizing instanceon this statement;so it is not ruled out by BGS.



info: PleaNP/Barriers/WilliamsTransfer.lean:111:0: #barrier_check PleaNP.Barriers.Williams.williams_transfer: Inconclusive - no Relativizing instanceon this statement;so it is not ruled out by BGS.



info: PleaNP/Barriers/WilliamsTransfer.lean:112:0: #barrier_check PleaNP.Barriers.Williams.NEXP_not_subset_ACC0: Inconclusive - no Relativizing instanceon this statement;so it is not ruled out by BGS.



info: PleaNP/Barriers/LowerBoundCompiler.lean:245:0: #barrier_check PleaNP.Barriers.Williams.williams_lower_bound_compiled: Inconclusive - no Relativizing instanceon this statement;so it is not ruled out by BGS.



"""


class VerdictHarnessTest(unittest.TestCase):
    def test_all_verdicts_present(self):
        missing = barrier_check_test.check_log(VERDICT_LINES)
        self.assertEqual(missing, [])

    def test_missing_verdict_detected(self):
        log = VERDICT_LINES.replace("#barrier_check PleaNP.Calculus.abstractPVsNP: DEAD",
                           "#barrier_check PleaNP.Calculus.abstractPVsNP: DEA D")
        missing = barrier_check_test.check_log(log)
        self.assertEqual(len(missing), 1)
        self.assertIn("#barrier_check PleaNP.Calculus.abstractPVsNP: DEAD", missing)

    def test_dash_tolerance(self):
        # Dashes (em and hyphen) are all folded by the harness;either family
        # must pass.
        log = VERDICT_LINES.replace("\u2014", "-")
        missing = barrier_check_test.check_log(log)
        self.assertEqual(missing, [])

    def test_check_log_tolerates_no_file_prefix(self):
        # The harness matches the declaration+verdict segment without needing
        # the `info:` file/line/col prefix..
        log = VERDICT_LINES.replace("info: PleaNP/Calculus/BarrierCalculus.lean:", "")
        missing = barrier_check_test.check_log(log)
        self.assertEqual(missing, [])

    def test_check_file_missing_reports_failure(self):
        with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as f:
            f.write(VERDICT_LINES.replace("DEAD", "DEA D"))
        try:
            rc = barrier_check_test.check_file(Path(f.name))
            self.assertEqual(rc, 1)
        finally:
            Path(f.name).unlink(missing_ok=True)

    def test_check_file_ok(self):
        with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False)as f:
            f.write(VERDICT_LINES)
        try:
            rc = barrier_check_test.check_file(Path(f.name))
            self.assertEqual(rc, 0)
        finally:
            Path(f.name).unlink(missing_ok=True)

    def test_drift_clean_on_real_tree(self):
        # Every `#barrier_check` invocation in the shipped Lean sources must be
        # asserted; otherwise a regression in it passes CI silently (issue #170).
        repo_root = Path(__file__).resolve().parents[3]
        lean_root = repo_root / "lean"
        self.assertTrue(lean_root.is_dir(), f"expected Lean root at {lean_root}")
        self.assertEqual(barrier_check_test.check_drift(barrier_check_test.iter_lean_files(lean_root)), [])

    def test_drift_detects_unasserted_invocation(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "New.lean"
            src.write_text("namespace X\n#barrier_check brandNewClaim\nend X\n", encoding="utf-8")
            missing = barrier_check_test.check_drift([src])
            self.assertEqual(len(missing), 1)
            self.assertIn("brandNewClaim", missing[0])

    def test_drift_ignores_prose_mentions(self):
        # A backticked ``#barrier_check`` in doc prose is not an invocation.
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "Doc.lean"
            src.write_text("-- mentions `#barrier_check foo` in prose\n", encoding="utf-8")
            self.assertEqual(barrier_check_test.check_drift([src]), [])

    def test_drift_ignores_indented_docblock_mention(self):
        # The real false-positive that motivated comment stripping: an indented
        # `#barrier_check concreteClassEq` living inside a `/-! ... -/` doc block.
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "Doc.lean"
            src.write_text("/-!\n  #barrier_check concreteClassEq   → DEAD\n-/\n#barrier_check realClaim\n",
                           encoding="utf-8")
            self.assertEqual(barrier_check_test.check_drift([src]), ["%s: #barrier_check realClaim" % src])

    def test_strip_lean_comments_handles_nesting(self):
        text = "a /- outer /- inner -/ still -/ b -- trailing\nc\n"
        stripped = barrier_check_test._strip_lean_comments(text)
        self.assertIn("a", stripped)
        self.assertIn("b", stripped)
        self.assertIn("c", stripped)
        self.assertNotIn("trailing", stripped)
        self.assertNotIn("inner", stripped)
        self.assertEqual(stripped.count("\n"), text.count("\n"))

    def test_check_drift_cli_reports_unasserted(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "New.lean").write_text("#barrier_check brandNewClaim\n", encoding="utf-8")
            self.assertEqual(barrier_check_test.check_drift_cli(Path(d)), 1)
        repo_root = Path(__file__).resolve().parents[3]
        self.assertEqual(barrier_check_test.check_drift_cli(repo_root / "lean"), 0)

    def test_check_drift_cli_bad_dir(self):
        self.assertEqual(barrier_check_test.check_drift_cli(Path("/nonexistent/lean")), 2)


if __name__ == "__main__":
    unittest.main()