#!/usr/bin/env python3
"""Tests for the pre-push check (issue #118).

The check exists because the Galaxy regen smoke has no local equivalent and has
broken CI twice (#112, #118). A check that cannot detect staleness is worthless,
so both directions are asserted: an up-to-date tree passes, and a deliberately
staled galaxy.html fails (then `--fix` restores it).

Run: python3 tooling/tests/test_pre_push_check.py
"""
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CHECK = REPO / "tooling" / "pre_push_check.py"
GALAXY = REPO / "tooling" / "galaxy" / "galaxy.html"
INBOX = REPO / "reviews" / "INBOX.md"


def run(*args):
    return subprocess.run([sys.executable, str(CHECK), *args],
                          cwd=str(REPO), capture_output=True, text=True)


class TestPrePushCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._galaxy_backup = GALAXY.read_bytes()
        cls._inbox_backup = INBOX.read_bytes()

    @classmethod
    def tearDownClass(cls):
        GALAXY.write_bytes(cls._galaxy_backup)
        INBOX.write_bytes(cls._inbox_backup)

    def test_clean_tree_passes(self):
        r = run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("up to date", r.stdout)

    def test_stale_is_detected_then_fix_restores(self):
        # Deliberately stale the committed page.
        GALAXY.write_bytes(self._galaxy_backup.replace(b'"repo": "PleaNP"',
                                                       b'"repo": "PleaNP_STALE"', 1))
        r = run()
        self.assertEqual(r.returncode, 1, "stale galaxy.html must fail the check")
        self.assertIn("STALE", r.stdout)

        r = run("--fix")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        r = run()
        self.assertEqual(r.returncode, 0, "after --fix the tree must be clean")

    def test_stale_inbox_is_detected_then_fix_restores(self):
        # The same failure class covers reviews/INBOX.md (issue #119): the CI
        # "Review-inbox index smoke" asserts the tracked index matches a regen.
        INBOX.write_bytes(self._inbox_backup.replace(b"# Review inbox",
                                                     b"# Review inbox STALE", 1))
        r = run()
        self.assertEqual(r.returncode, 1, "stale INBOX.md must fail the check")
        self.assertIn("reviews/INBOX.md is STALE", r.stdout)

        r = run("--fix")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(INBOX.read_bytes(), self._inbox_backup,
                         "--fix must restore the regenerated index")

        r = run()
        self.assertEqual(r.returncode, 0, "after --fix the tree must be clean")


if __name__ == "__main__":
    unittest.main()