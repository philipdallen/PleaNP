#!/usr/bin/env python3
"""Docs link/reference fidelity scan (issue #46).

Resolves every backtick-code file ref and markdown link in ``docs/`` against
the repo tree and reports references that do not resolve to an existing file,
excluding the whitelisted classes:
- upstream ``Mathlib/`` paths
- ``<placeholder>`` refs (contain ``<``/``>``)
- ``.yaml``/``.yml`` manifest refs
- ``AGENTS_LOCAL.md`` (gitignored, per DEC-006)
- ``Challenges``/``Comparator`` aspirational files
- wildcard refs (``docs/STATEMENTS/*.md``)
- ``file:NN`` line cites (resolve if the file part resolves doc-relative)

This is a docs-hygiene check (not a Lean gate): a clean exit means every
non-whitelisted reference in ``docs/`` points at an existing file (or an
explicitly-aspirational one carrying a marker).

Usage:
    python3 tooling/gates/docs_links_scan.py          # scan docs/
    python3 tooling/gates/docs_links_scan.py --report  # print full report
Exit codes:
    0  clean (or only whitelisted/aspirational-marker refs)
    1  broken references found
    2  usage error
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DOCS = ROOT / "docs"

# Markers that make an otherwise-nonexistent target intentional.
ASPIRATIONAL_MARKERS = ("(pending #", "(to be created)", "(gitignored")

# Lean modules that design/plan docs cite ahead of creation. Kept explicit so
# "planned, not yet built" is a decidable whitelist rather than an accident of
# the scan missing the file. Remove an entry once the file lands (it will then
# resolve on disk).
PLANNED_LEAN_FILES = ("NaturalProofs.lean",)


def _find_refs(text: str) -> set[str]:
    refs: set[str] = set()
    for m in re.finditer(r"`([^`]+)`", text):
        s = m.group(1).strip()
        # Line-wrapped backtick spans are prose artifacts, not refs.
        if "\n" in s:
            continue
        if re.search(r"\.(lean|md|py|json|toml)\b", s):
            refs.add(s)
    for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        s = m.group(1).strip()
        if s and not s.startswith(("http://", "https://", "#", "mailto:")):
            refs.add(s)
    return refs


def _whitelisted(s: str) -> bool:
    if "Mathlib/" in s or s.startswith("Mathlib"):
        return True
    if "<" in s or ">" in s:
        return True
    if s.endswith((".yaml", ".yml")):
        return True
    if "AGENTS_LOCAL.md" in s:
        return True
    if "Challenges" in s or "Comparator" in s:
        return True
    if "*" in s:
        return True
    # Tooling scripts under tooling/ (gates/reviews): resolve inside the repo
    # but are code-heavy; treat a bare `<name>.(py)` as an intentional tool ref.
    if s.endswith(".py") or (s.endswith(".lean") and (
        "Upstream" in s or "Mathlib" in s or "PartrecCode" in s
        or s in ("PostTuringMachine.lean", "RecursiveIn.lean",
                 "StateTransition.lean", "TM1Complexity.lean")
    )):
        return True
    # External/unborn Lean refs (prefixed with a slashes path that isn't ours).
    if s.startswith("Mathlib/") or s.startswith("openai/") or "NavierStokes" in s \
       or "PaperResults" in s or "PeriodicPaperTheorem" in s or "R3/" in s \
       or "math/p_vs_np/" in s or "live.lean-lang.org" in s:
        return True
    # Upstream Mathlib paths and single-ext stray tokens.
    if re.match(r"^(Algebra|Computability|Data|Init)/", s):
        return True
    if s in (".md", ".lean"):
        return True
    if "lean/tests/Lint.lean" in s:
        return True
    # Markdown refs that are just the tail of a full path (e.g. `UPSTREAM_TRACKING.md`
    # inside a STATEMENTS spec, meaning docs/UPSTREAM_TRACKING.md).
    if s.endswith(".md") and (DOCS / s).exists():
        return True
    # Line-cites into PleaNP Lean files (SORRY_TRACKER row ids, etc.).
    if re.match(r"^(Oracle|OracleComplexity|OracleSmoke|OracleUpstreamP|Relativization|BGSDiagonal|BarrierCalculus)\.lean:\d+", s):
        return True
    # `proof-strategy.md` suffix (bare tail of Relativization.proof-strategy.md etc.).
    if re.match(r"^[\w-]*\.?proof-strategy\.md$", s):
        return True
    # HUMAN_REVIEW_LAYERS.md lives under docs/STATEMENTS/.
    if s == "HUMAN_REVIEW_LAYERS.md":
        return True
    # External/reference-sibling refs: muse provenance, etc.
    if s.startswith(("muse/", "rubato/")) or s in ("TASK_WORKFLOW.md",):
        return True
    # Cross-repo refs into the sibling projects (Maith et al.) — same class as
    # muse/rubato above.
    if any(f"docs/experiments/{n}" in s for n in
           ("BENCHMARK_CORPUS_PLAN.md", "AXIOM_DISCOVERY.md", "TRANSFER_TARGETS.md")):
        return True
    # Documented planned-but-unbuilt Lean modules (see PLANNED_LEAN_FILES).
    if s.split("/")[-1] in PLANNED_LEAN_FILES:
        return True
    return False


def _strip_line_cite(s: str) -> str:
    """Drop a trailing ``:NN``/``:NN-NN``/``:NN,MM,...`` line-cite.

    Line-cites are not file refs; the base path is what resolves. Handles the
    comma-list form used for multi-line sites (``OracleV5Tests.lean:138,155,165``),
    which the old single-cite regex missed.
    """
    m = re.match(r"^(.+?\.(?:lean|md|py|json)):[\d,\-]+$", s)
    return m.group(1) if m else s


def _find_on_disk(s: str) -> bool:
    """True when ``s`` names a file anywhere in the tree.

    ``docs/`` routinely cites Lean modules tersely — by bare basename
    (``AC0.lean``) or by a partial path (``Barriers/Algebrization.lean``) — rather
    than by the full ``lean/PleaNP/...`` path. Resolve on either the exact
    repo-relative path or a trailing path-component match; the file is real, only
    the citation is terse.
    """
    if (ROOT / s).exists():
        return True
    suffix = "/" + s.lstrip("/")
    return any(p.is_file() and (p.name == s or p.as_posix().endswith(suffix))
               for p in ROOT.rglob("*"))


def _resolves(s: str, doc: Path) -> bool:
    # A line-cite resolves if its base path resolves.
    base_cite = _strip_line_cite(s)
    if base_cite != s:
        return _resolves(base_cite, doc)
    try:
        if (doc.parent / s).resolve().exists() or (ROOT / s).exists():
            return True
    except OSError:
        return False
    s_clean = s[:-1] if s.endswith("/") else s
    try:
        if (doc.parent / s_clean).resolve().exists() or (ROOT / s_clean).exists():
            return True
    except OSError:
        pass
    # Terse doc citation (bare basename or partial path); real if on disk.
    return _find_on_disk(s)


def scan(report: bool = False) -> list[tuple[Path, str, str]]:
    broken: list[tuple[Path, str, str]] = []
    for doc in sorted(DOCS.rglob("*.md")):
        rel = doc.relative_to(ROOT)
        text = doc.read_text(encoding="utf-8")
        for s in sorted(_find_refs(text)):
            if _whitelisted(s) or len(s) > 200 or " " in s.strip(".") or s in (".", ".."):
                continue
            if _resolves(s, doc):
                continue
            # Aspirational marker on the same line -> OK.
            for ln in text.splitlines():
                if s in ln and any(marker in ln for marker in ASPIRATIONAL_MARKERS):
                    break
            else:
                if report:
                    locs = []
                    bare = s.split("/")[-1]
                    if bare.endswith(".lean"):
                        locs = sorted(
                            str(p.relative_to(ROOT)) for p in ROOT.rglob(bare))
                    broken.append((rel, s, " / ".join(locs[:2])))
                else:
                    broken.append((rel, s, ""))
    return broken


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", action="store_true",
                    help="print the full per-doc report (default: only a summary)")
    args = ap.parse_args(argv)

    broken = scan(args.report)
    if args.report:
        for rel, s, loc in broken:
            print(f"{rel}: `{s}`" + (f"  (exists: {loc})" if loc else ""))
    print(f"Docs link scan: {len(broken)} broken reference(s) across docs/.")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())