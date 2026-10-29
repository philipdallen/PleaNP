#!/usr/bin/env python3
"""Gate 5 (Tier 1) -- non-triviality / vacuity scanner for PleaNP Lean source.

Flags statements and definitions whose bodies are vacuously true or trivially
constructed -- the "compiles but means nothing" pattern that a hygiene scan
(sorry/admit/axiom) misses but that the failure audit (Pattern A) warns about.

Catches the DISHONEST placeholder pattern:
- a theorem/lemma whose statement is `True` and proved by `trivial`/`rfl`/
  `decide` (not `sorry`) -- a real-looking theorem proving a triviality
- a definition with `iff True` in the body -- vacuous equivalence
  (the `forall x, x in L iff True` pattern)
- a def whose body is a bare `none` -- constant failure masquerading as an
  implementation (the `stepCountByEvalsToInTime ... := none` pattern)

Does NOT flag the HONEST placeholder: `: True := by sorry` (caught by Gate 6),
or a clearly-marked `-- placeholder` comment. A `sorry` is honest; a `trivial`
proof of `True` is a fake success.

It also carries a report-only **parameter-occurrence** check for `structure`/
`class` fields (issue #234): a field whose type never mentions one of the
enclosing declaration parameters is flagged. This is the #224/#226 failure mode
(DEC-029): the withdrawn `MachineCode.simulates` field never mentioned the
machine parameter `M`, so it certified no machine behaviour -- yet the syntactic
`True`/`↔ True`/`rfl`/`none` patterns above could not see it. The check is
mechanical (parameter-occurrence over the field type, comments stripped) and
needs no Lean semantics.

Tier-1-occurrence ONLY: passing it does NOT certify a field is meaningful, only
that its parameters occur. A field whose parameters all occur can still be
vacuous (the check says nothing about *what* the field means). Known-legit
phantom parameters are allowlisted in `PHANTOM_PARAM_ALLOWLIST` below.

This is the Tier 1 of Gate 5 (non-triviality): static, no Lean semantics.
Like hygiene_scan.py (Gate 6 Tier 1), it CANNOT catch vacuity that requires
understanding what a definition *means* -- that is Gate 4 (read-back) and
the review layer's job. "Gate 5 passed" = Tier 1 + review, not Tier 1 alone.

Usage:
    python3 vacuity_scan.py <path>            # scan one file or dir
    python3 vacuity_scan.py lean/PleaNP        # scan the library

Exit codes:
    0  clean (no vacuity patterns found)
    1  vacuity patterns found (prints a report)
    2  usage error
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Finding:
    file: Path
    line_no: int
    kind: str
    decl_name: str
    snippet: str


def _strip_comments(src: str) -> str:
    """Blank (not delete) block comments /- ... -/ and line comments --.

    Shares the binder_usage_scan approach (issue #60, the shared regex bug):
    comments are replaced by equal-length whitespace so reported line numbers
    stay true file coordinates, and the closing delimiter is `-/` WITHOUT a
    required leading space — so Mathlib-convention docstrings that close with
    ``\\n-/`` are stripped correctly (the old `/-.*? -/` missed those and
    could over-strip from the first `/-` to a later ` -/`, deleting real
    code).
    """
    def _blank(m: re.Match) -> str:
        return "".join("\n" if c == "\n" else " " for c in m.group(0))

    src = re.sub(r"/-.*?-/", _blank, src, flags=re.DOTALL)
    src = re.sub(r"--.*?$", _blank, src, flags=re.MULTILINE)
    return src


# Matches the start of a top-level declaration: def/theorem/lemma/etc.
# We use this to split the source into per-declaration blocks.
DECL_START_RE = re.compile(
    r"^(def|theorem|lemma|structure|class|inductive|instance|abbrev|axiom|constant)\s+(\S+)",
    re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Parameter-occurrence check (issue #234). Report-only.
#
# A `structure`/`class` field whose type never mentions one of the enclosing
# declaration's parameters is the #224/#226 vacuity shape: the field looks like
# a constraint but cannot constrain the parameter it omits.
#
# Known-legit phantom parameters, with the reason each is a false positive for
# this report-only check. Key: (decl_name, field_name, param_name). Every entry
# below was surfaced by the check on the 2026-10-29 tree and dispositioned here
# rather than silently dropped (issue #234 DoD 2). A parameter that is phantom in
# a *new* structure is NOT covered by this list and will be flagged.
PHANTOM_PARAM_ALLOWLIST: dict[tuple[str, str, str], str] = {
    # Sibling field carries the parameter; the flagged field is a data carrier.
    ("MachineCodeBridge", "code", "M"): "sibling `simulates` carries M",
    ("MachineCodeBridge", "code", "oa"): "sibling `simulates` carries oa",
    ("OracleCode", "prog", "Q"): "sibling `oracle` carries Q",
    ("IsRandomRestriction", "nonneg", "p"): "sibling `fixedCount_law` carries p",
    ("IsRandomRestriction", "sum_one", "p"): "sibling `fixedCount_law` carries p",
    ("Cfg", "cfg", "Q"): "sibling `oracle` carries Q",
    ("Cfg", "oracle", "tm"): "sibling `cfg` carries tm",
    ("Machine", "oracle", "tm"): "sibling `decode` carries tm",
    ("Machine", "queryLabel", "Q"): "siblings `oracle`/`decode` carry Q",
    ("Machine", "yesLabel", "Q"): "siblings `oracle`/`decode` carry Q",
    ("Machine", "noLabel", "Q"): "siblings `oracle`/`decode` carry Q",
    # Documented packaging (DEC-029): the structure deliberately carries no
    # simulation claim, so its parameters are phantom by design, not by defect.
    ("MachineCode", "code", "Q"): "documented packaging, no simulation claim",
    ("MachineCode", "code", "tm"): "documented packaging, no simulation claim",
    ("MachineCode", "code", "M"): "documented packaging, no simulation claim",
}

# Lean keywords / binders / punctuation that are never parameter names, so we do
# not treat `Type`/`Prop`/`where`/`:=` as a structure parameter.
_NON_PARAM_TOKENS = {
    "Type", "Type*", "Prop", "Sort", "where", "extends", "deriving",
    "structure", "class", "instance", "abbrev", "def", "theorem", "lemma",
}

# Identifiers of length >= 2 that look like a parameter reference. We require
# a word boundary and exclude single characters, so a parameter `n` is matched
# as `n` only when it occurs as a standalone token.
_IDENT_RE = re.compile(r"[A-Za-z_\u03b1-\u03c9][A-Za-z0-9_'\u03b1-\u03c9]*")


def _split_params(signature: str) -> list[str]:
    """Extract the parameter names from a structure/class signature.

    `signature` is the text from just after the decl name up to the `where`.
    Handles explicit binders `(Q : Type)`, `(tm : FinTM2)`, typeclass binders
    `[DecidableEq tm.Λ]`, and implicit `{Q : Type}`. A bare token group with no
    colon (e.g. an index) is skipped: only binders introduce parameters.
    """
    params: list[str] = []
    # Bindered groups: ( ... ), { ... }, [ ... ].
    for m in re.finditer(r"[\(\[\{]([^\(\)\[\]\{\}]*)[\)\]\}]", signature):
        group = m.group(1)
        if ":" not in group:
            continue
        head = group.split(":", 1)[0].strip()
        # Multiple names may be bound: `(a b : Nat)`.
        for name in head.split():
            if name and name not in _NON_PARAM_TOKENS:
                params.append(name)
    return params


def _check_phantom_params(kind: str, name: str, block: str) -> list[tuple[str, str, int]]:
    """Return (field_name, param_name, field_offset) triples where a field's
    type never mentions a parameter of the enclosing structure/class.

    `field_offset` is the offset of the field line within `block`, so the caller
    can report the field's own line rather than the declaration's. Report-only;
    `block` is the declaration block (comments already stripped) starting at
    `structure`/`class`.
    """
    if kind not in ("structure", "class"):
        return []
    # Split the signature (name .. `where`) from the field body.
    where_m = re.search(r"\bwhere\b", block)
    if where_m is None:
        return []
    where_idx = where_m.start()
    name_idx = block.find(name)
    if name_idx == -1:
        return []
    signature = block[name_idx + len(name):where_idx]
    body = block[where_idx:]
    params = _split_params(signature)
    if not params:
        return []

    triples: list[tuple[str, str, int]] = []
    # Field lines: indented `field : type` (not `:=`). Continuation lines of a
    # type are more-indented and belong to the preceding field.
    field_re = re.compile(r"^[ \t]+([A-Za-z_][A-Za-z0-9_']*)\s*:(?!=)", re.MULTILINE)
    matches = list(field_re.finditer(body))
    for i, m in enumerate(matches):
        field_name = m.group(1)
        type_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        field_type = body[m.end():type_end]
        type_idents = set(_IDENT_RE.findall(field_type))
        field_offset = where_idx + m.start()
        for p in params:
            if p in type_idents:
                continue
            if (name, field_name, p) in PHANTOM_PARAM_ALLOWLIST:
                continue
            triples.append((field_name, p, field_offset))
    return triples


def _split_decls(src: str) -> list[tuple[str, str, int]]:
    """Split source into (decl_kind, decl_name, start_offset) blocks.
    Returns list of (kind, name, offset) for each top-level declaration."""
    decls = []
    for m in DECL_START_RE.finditer(src):
        decls.append((m.group(1), m.group(2), m.start()))
    # Each block runs from its start to the next decl's start (or EOF).
    blocks = []
    for i, (kind, name, start) in enumerate(decls):
        end = decls[i + 1][2] if i + 1 < len(decls) else len(src)
        blocks.append((kind, name, start, src[start:end]))
    return blocks


# Patterns applied WITHIN a single declaration block.

# A theorem/lemma with `: True := by trivial` (or rfl/decide). NOT `sorry`.
THEOREM_TRUE_TRIVIAL_RE = re.compile(r":\s*True\s*:=\s*by\s+(trivial|rfl|decide)\b")

# A block with `iff True` (the unicode arrow). Vacuous equivalence.
IFF_TRUE_RE = re.compile(r"\u2194\s*True\b")

# A def with `:= True` (bare equality to True as a body).
EQ_TRUE_DEF_RE = re.compile(r":=\s*True\b")

# A def whose body is a BARE `none` or `Option.none` (constant failure) —
# meaning none/Option.none IS the whole body, not embedded in a larger
# expression like `some (Cfg.mk { l := Option.none })`. We require the
# body (after :=, skipping whitespace) to be exactly `none` or `Option.none`
# followed by a newline (end of statement). This avoids false-flagging
# legitimate uses of Option.none inside larger terms.
DEF_NONE_RE = re.compile(r":=\s*(?:Option\.)?none\s*$", re.MULTILINE | re.DOTALL)


def scan_file(path: Path) -> list[Finding]:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"warning: could not read {path}: {e}", file=sys.stderr)
        return []
    src = _strip_comments(raw)

    findings: list[Finding] = []
    for kind, name, start, block in _split_decls(src):
        line_no = src.count("\n", 0, start) + 1
        # First line of the block for the snippet.
        snippet = block.split("\n", 1)[0].strip()

        if kind in ("theorem", "lemma"):
            if THEOREM_TRUE_TRIVIAL_RE.search(block):
                findings.append(Finding(path, line_no, "theorem_true_trivial", name, snippet))

        if kind == "def":
            if IFF_TRUE_RE.search(block):
                findings.append(Finding(path, line_no, "vacuous_iff_true", name, snippet))
            elif EQ_TRUE_DEF_RE.search(block):
                findings.append(Finding(path, line_no, "vacuous_eq_true", name, snippet))
            if DEF_NONE_RE.search(block):
                findings.append(Finding(path, line_no, "def_none", name, snippet))

        for field_name, param, field_off in _check_phantom_params(kind, name, block):
            field_line = src.count("\n", 0, start + field_off) + 1
            findings.append(Finding(
                path, field_line, "phantom_param", f"{name}.{field_name}",
                f"parameter `{param}` never occurs in this field's type",
            ))

    return findings


def scan(paths: list[Path]) -> list[Finding]:
    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            files.extend(sorted(p.rglob("*.lean")))
        elif p.suffix == ".lean":
            files.append(p)
    files = sorted(set(files))

    all_findings: list[Finding] = []
    for f in files:
        all_findings.extend(scan_file(f))
    return all_findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate 5 (Tier 1) vacuity scanner")
    ap.add_argument("path", nargs="+", type=Path, help=".lean file or dir to scan")
    args = ap.parse_args()

    findings = scan(args.path)

    if findings:
        print(f"Gate 5 (Tier 1) findings across {len(set(f.file for f in findings))} file(s):")
        for f in findings:
            print(f"  [REVIEW] {f.kind:22} {f.file}:{f.line_no}  {f.decl_name}  | {f.snippet}")
        print()
        print(f"  {len(findings)} vacuity pattern(s) -- review for dishonest placeholders")
        return 1
    else:
        print(f"Gate 5 (Tier 1) clean: no trivially-true/vacuous patterns in {len(args.path)} path(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
