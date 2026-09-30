#!/usr/bin/env python3
"""Gate harness: assert the `#barrier_check` verdicts appear in a build log.

Issue #3 (Tests: test spec for Rung-5 #barrier_check verdicts). The
`#barrier_check` elaborator in `lean/PleaNP/Calculus/BarrierCalculus.lean`
logs verdict lines during compile — the four abstract unit tests plus the
two concrete P_A/NP_A seeds (issue #82 Pass 1):

  - `thhStatement`          -> "relativizes, not P-vs-NP-shaped -> Inconclusive"
  - `abstractPVsNP`         -> "DEAD - this proof relativizes"
  - `plainRelHeuristic`     -> "relativizes, not P-vs-NP-shaped -> Inconclusive"
  - `nonRelativizingControl` -> "Inconclusive —no Relativizing instance"
  - `concreteClassMembership` -> "DEAD — this proof relativizes"
  - `bgsMetaStatement`        -> "Inconclusive — no Relativizing instance"
  - `PleaNP.Barriers.Williams.williams_transfer`          -> "Inconclusive"
  - `PleaNP.Barriers.Williams.NEXP_not_subset_ACC0`       -> "Inconclusive"
  - `PleaNP.Barriers.Williams.williams_lower_bound_compiled` -> "Inconclusive"

The final three live in CI-compiled modules but were not asserted until issue
#170, so a regression in them passed CI silently — the unasserted tail behind
the "a check that cannot fail is not a check" audit finding. `--check-drift`
guards the same hole going forward: it scans the Lean sources for
`#barrier_check <decl>` invocations and fails if any is absent from EXPECTED,
so a newly-added invocation cannot silently go unasserted.

CI builds the clean modules (see `.github/workflows/ci.yml`); the harness
runs on the captured build log (the build step `tee`s its output to a log
file) and fails if any expected verdict line is missing or wrong — so a
regression in the elaborator's verdicts (a DEAD flipping to Inconclusive, a
message rewrite, an instance that stops synthesizing) kills the build.

Expected-log match: for each (decl, verdict-template) pair, the log must
contain the segment `#barrier_check PleaNP.Calculus.<decl>: <template-prefix>`.
The verdict templates are extracted verbatim from the elaborator source (the
`logInfo m!"..."` strings at BarrierCalculus.lean:276-280;keep in sync
they are els hard-coded below with the `{n}` placeholder replaced by the full
declaration name and the message text verbatim. Only the part upto the final
clause is matched (so file/line/col prefixes,and the unicode dash variants,
don't bake into the assertion;but the verdict-identifying text does.

Usage:
    python3 barrier_check_test.py <log-file>
    python3 barrier_check_test.py --run-lake [MODULE]   # builds in lean/ then checks
    python3 barrier_check_test.py --check-drift [LEAN_ROOT]  # every invocation asserted (stdlib-only)
Exit codes:
    0   all four verdicts present
    1   assertion failure (missing/wrong verdict line),
    2   usage error
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# The four declarations the elaborator checks, with their expected verdict
# segments (verbatim from the `logInfo` templates in BarrierCalculus.lean;the
# final clause after the verdict keyword is dropped so punctuation/line-prefix
# variations don't matter, but the verdict-identifying text is exact).
EXPECTED = [
    ("PleaNP.Calculus.thhStatement",
     "#barrier_check PleaNP.Calculus.thhStatement: relativizes,"),
    ("PleaNP.Calculus.abstractPVsNP",
     "#barrier_check PleaNP.Calculus.abstractPVsNP: DEAD"),
    ("PleaNP.Calculus.plainRelHeuristic",
     "#barrier_check PleaNP.Calculus.plainRelHeuristic: relativizes,"),
    ("PleaNP.Calculus.nonRelativizingControl",
     "#barrier_check PleaNP.Calculus.nonRelativizingControl: Inconclusive"),
    # Concrete Rung-5 seeds (issue #82 Pass 1): a relativizing P-vs-NP-shaped
    # claim over the concrete P_A/NP_A classes is DEAD; the BGS meta-statement
    # over the concrete classes carries no Relativizing instance → Inconclusive.
    ("PleaNP.Calculus.concreteClassMembership",
     "#barrier_check PleaNP.Calculus.concreteClassMembership: DEAD"),
    ("PleaNP.Calculus.bgsMetaStatement",
     "#barrier_check PleaNP.Calculus.bgsMetaStatement: Inconclusive"),
    # Barrier-classification modules (issue #90 Pass 3 / #82): these invocations
    # live in CI-compiled modules but were never asserted until #170 — the
    # unasserted tail that made the audit's "a check that cannot fail" finding
    # stick for the non-relativizing Williams statements. All three are
    # documented Inconclusive (no `Relativizing` instance).
    ("PleaNP.Barriers.Williams.williams_transfer",
     "#barrier_check PleaNP.Barriers.Williams.williams_transfer: Inconclusive"),
    ("PleaNP.Barriers.Williams.NEXP_not_subset_ACC0",
     "#barrier_check PleaNP.Barriers.Williams.NEXP_not_subset_ACC0: Inconclusive"),
    ("PleaNP.Barriers.Williams.williams_lower_bound_compiled",
     "#barrier_check PleaNP.Barriers.Williams.williams_lower_bound_compiled: Inconclusive"),
]

# Every `#barrier_check <ident>` invocation in the Lean sources. Comments are
# stripped before matching (see `_strip_lean_comments`): `#barrier_check` appears
# in doc-comment prose, often indented at the start of a line, and scanning raw
# source would flag that prose as an invocation.
_BARRIER_INVOCATION_RE = re.compile(
    r"^[ \t]*#barrier_check[ \t]+([A-Za-z_][A-Za-z0-9_'.]*)", re.MULTILINE
)


def _strip_lean_comments(text: str) -> str:
    """Blank out Lean block and line comments, preserving line breaks.

    Handles nested `/- ... -/` blocks and `-- ...` line comments. Every other
    character is kept, and newlines are preserved, so a `^`-anchored match still
    lands on the same source line it would on the raw file.
    """
    out: list[str] = []
    i, n, depth = 0, len(text), 0
    while i < n:
        two = text[i:i + 2]
        if depth > 0:
            if two == "/-":
                depth += 1
                out.append("  ")
                i += 2
            elif two == "-/":
                depth -= 1
                out.append("  ")
                i += 2
            else:
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
        elif two == "/-":
            depth += 1
            out.append("  ")
            i += 2
        elif two == "--":
            j = text.find("\n", i)
            j = n if j == -1 else j
            out.append(" " * (j - i))
            i = j
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def check_drift(lean_files: list[Path]) -> list[str]:
    """Return `#barrier_check` invocations in `lean_files` absent from EXPECTED.

    This is the hole the audit's finding really pointed at: a new
    `#barrier_check <decl>` added to a Lean module compiles fine while its
    verdict stays unasserted, so a regression in it passes CI silently. Matching
    is by short-name suffix (EXPECTED carries full names) so no Lean namespace
    resolution is needed.
    """
    asserted = {full.rsplit(".", 1)[-1] for full, _ in EXPECTED}
    missing: list[str] = []
    for path in lean_files:
        text = _strip_lean_comments(path.read_text(encoding="utf-8", errors="replace"))
        for m in _BARRIER_INVOCATION_RE.finditer(text):
            if m.group(1).rsplit(".", 1)[-1] not in asserted:
                missing.append(f"{path}: #barrier_check {m.group(1)}")
    return missing


def iter_lean_files(lean_root: Path) -> list[Path]:
    """Every `.lean` source under `lean_root`, sorted for stable output."""
    return sorted(lean_root.rglob("*.lean"))

#(The dash in "DEAD - this proof" and "Inconclusive - no Relativizing" is an
# em dash in the source (U+2014);match with a tolerant pattern so the
# assertion survives terminal/environment-specific dash re-encoding.)
_EM_DASH = "—"


def verdict_segment(decl: str, template: str) -> str:
    """Rebuild the exact verdict text from the elaborator's logInfo template.


    The template uses `{n}` for the declaration and the em dash is part of the
    human-readable message. The assertion match includes decl + verdict keyword
    with an em-dash-tolerant boundary. Returns a compiled pattern string."""
    # fold the template's placeholder entirely (decl already carries the name).
    # Keep only the leading clause up to the first comma after the keyword, so the
    # line/col prefix and trailing clauses don't bake in.
    return template.format(n=decl)


_DASH_FAMILY = ("—", "\u2013", "\u2012", "\u2015", "-")

def _normalize_dashes(s: str) -> str:
    """Fold every dash-family char to a sentinel for dash-tolerant verdict match."""
    for d in _DASH_FAMILY:
        s = s.replace(d, "\u2003")
    return s

def check_log(text: str) -> list[str]:
    """Return the list of expected verdicts missing from the log."""
    norm = _normalize_dashes(text)
    missing = []
    for decl, template in EXPECTED:
        seg = _normalize_dashes(verdict_segment(decl, template))
        if seg not in norm:
            missing.append(seg)
    return missing

def check_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = check_log(text)
    if missing:
        print(f"barrier-check verdict harness: {len(missing)} expected verdict(s) missing from {path}:")
        for seg in missing:

            print(f"  MISSING: {seg[:90]}...")
        return 1
    print(f"barrier-check verdict harness ok: all {len(EXPECTED)} verdicts present in {path}.")
    return 0


def run_lake(module: str) -> int:
    """Build the module in `lean/` (cwd) and feed the captured output through the
    assertions. Used locally;CI instead tees the existing build step's output
    (so no double build)and hands the log to --log."""
    # force a rebuild so the elaborator's logInfo lines actually print (lake
    # skips up-to-date modules silently).
    src = Path("PleaNP/Calculus/BarrierCalculus.lean")
    if src.exists():
        src.touch()
    proc = subprocess.run(
        ["lake", "build", module],
        capture_output=True, text=True,
    )
    log = proc.stdout + "\n" + proc.stderr
    if proc.returncode != 0:
        print(f"barrier-check verdict harness: lake build failed (exit {proc.returncode})", file=sys.stderr)
        print(log[-4000:], file=sys.stderr)
        return 1
    return check_log_stdout(log)


def check_log_stdout(log: str) -> int:
    missing = check_log(log)
    if missing:
        print(f"barrier-check verdict harness: {len(missing)} expected verdict(s) missing from the build output:")
        for seg in missing:
            print(f"  MISSING: {seg[:90]}...")
        return 1
    print(f"barrier-check verdict harness ok: all {len(EXPECTED)} verdicts present.")
    return 0


def check_drift_cli(lean_root: Path) -> int:
    """Fail if any `#barrier_check` invocation under `lean_root` is unasserted."""
    if not lean_root.is_dir():
        print(f"barrier-check verdict harness: not a directory: {lean_root}", file=sys.stderr)
        return 2
    missing = check_drift(iter_lean_files(lean_root))
    if missing:
        print(f"barrier-check verdict harness: {len(missing)} #barrier_check invocation(s) not asserted in EXPECTED:")
        for item in missing:
            print(f"  UNASSERTED: {item}")
        print("Add each to EXPECTED in barrier_check_test.py (with its expected verdict segment).")
        return 1
    print(f"barrier-check verdict harness drift ok: every #barrier_check invocation has an EXPECTED assertion.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Assert the #barrier_check verdicts in a build log (issue #3)")
    ap.add_argument("log", nargs="?", type=Path, help="build log file to check")
    ap.add_argument("--run-lake", nargs="?", const="PleaNP.Calculus.BarrierCalculus", metavar="MODULE",
                    help="build the module with lake (in lean/) first, then check its output")
    ap.add_argument("--check-drift", nargs="?", const="lean", metavar="LEAN_ROOT",
                    help="fail if any `#barrier_check` invocation under LEAN_ROOT (default: lean/) "
                         "is missing from EXPECTED; stdlib-only, no Lean toolchain needed")
    args = ap.parse_args()

    modes = [bool(args.log), bool(args.run_lake), bool(args.check_drift)]
    if sum(modes) != 1:
        print("barrier-check verdict harness: pass exactly one of <log-file>, --run-lake, or --check-drift",
              file=sys.stderr)
        return 2
    if args.log:
        return check_file(args.log)
    if args.run_lake:
        return run_lake(args.run_lake)
    return check_drift_cli(Path(args.check_drift))


if __name__ == "__main__":
    sys.exit(main())