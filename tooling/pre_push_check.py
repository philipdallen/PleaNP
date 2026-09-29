#!/usr/bin/env python3
"""pre_push_check — run the CI-only checks locally before pushing (issue #118).

Twice now (issues #112, #118) a change to a tracked doc broke CI on a step that
has no local equivalent: the **Galaxy regen smoke**, which asserts the committed
`tooling/galaxy/galaxy.html` still matches the output of regenerating it from
the repo artifacts. `docs/SORRY_TRACKER.md`, `docs/ROADMAP.md`, `formalization.yaml`
and the review points are all embedded in that page, so editing any of them
requires a regen — and neither the Tier-1 scanners nor `pytest` catch a stale
copy. The failure only shows up in CI (this repo's sanctioned "build oracle"),
which costs a round trip.

This script is the local equivalent: it regenerates each tracked generated
artifact and reports whether the committed copy is stale, so the fix
(regenerate + include it in the commit) happens before the push rather than
after.

The same failure class covers **any** CI step that asserts a *tracked* artifact
matches a regeneration (issue #119). Rather than add one-off scripts, the
generated artifacts are listed in `CHECKS`; a new CI-only staleness step extends
that list. `reviews/INBOX.md` (CI step "Review-inbox index smoke") is the second
such artifact.

Usage:
    python3 tooling/pre_push_check.py          # check only (exit 1 if stale)
    python3 tooling/pre_push_check.py --fix    # regenerate in place if stale

Exit codes: 0 up to date, 1 stale (or regen failed), 2 usage error.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GALAXY = REPO / "tooling" / "galaxy" / "galaxy.html"
INBOX = REPO / "reviews" / "INBOX.md"


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)


def _regen_galaxy() -> bytes:
    """Regenerate galaxy.html into a temp file and return its bytes."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "galaxy.html"
        r = _run([sys.executable, "tooling/galaxy/galaxy.py", "--repo", ".", "--out", str(out)])
        if r.returncode != 0:
            raise RuntimeError(f"galaxy regen FAILED:\n{r.stderr[-2000:]}")
        return out.read_bytes()


def _regen_inbox() -> bytes:
    """Regenerate reviews/INBOX.md and return its bytes.

    `review_inbox.py index` writes in place, so the committed file is snapshotted
    and restored before returning; the caller writes the fresh bytes itself only
    under `--fix`.
    """
    original = INBOX.read_bytes() if INBOX.exists() else b""
    r = _run([sys.executable, "tooling/reviews/review_inbox.py", "index"])
    if r.returncode != 0:
        raise RuntimeError(f"review-inbox regen FAILED:\n{r.stderr[-2000:]}")
    fresh = INBOX.read_bytes() if INBOX.exists() else b""
    if fresh != original:
        INBOX.write_bytes(original)
    return fresh


# (path, label, CI step name, regenerator)
CHECKS = (
    (GALAXY, "galaxy.html", "Galaxy regen smoke", _regen_galaxy),
    (INBOX, "reviews/INBOX.md", "Review-inbox index smoke", _regen_inbox),
)


def check(fix: bool) -> int:
    stale = []
    for path, label, ci_step, regen in CHECKS:
        try:
            fresh = regen()
        except RuntimeError as exc:
            print(f"pre_push_check: {label}: {exc}", file=sys.stderr)
            return 1
        committed = path.read_bytes() if path.exists() else b""
        if fresh == committed:
            print(f"pre_push_check: {label} is up to date.")
            continue
        stale.append(label)
        if fix:
            path.write_bytes(fresh)
            print(f"pre_push_check: {label} was STALE — regenerated (re-add it to the commit).")
        else:
            print(f"pre_push_check: {label} is STALE — CI's '{ci_step}' will fail.")
    if stale and not fix:
        print("  Fix: python3 tooling/pre_push_check.py --fix && "
              "git add " + " ".join(stale))
        return 1
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="pre-push CI-equivalent checks")
    ap.add_argument("--fix", action="store_true",
                    help="regenerate stale artifacts in place")
    args = ap.parse_args(argv[1:])
    return check(args.fix)


if __name__ == "__main__":
    sys.exit(main(sys.argv))