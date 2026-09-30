# Integrity gates: Tier 1 scanners

Part of the integrity pipeline (`docs/ARCHITECTURE.md`). These Python scanners catch mechanical integrity failures that a grep/AST pass can detect — they need no Lean toolchain and run in the remote authoring environment and in CI. Each is the Tier 1 of its gate; the full gate (Tier 2, requiring `lake build`) is the local agent's job.

## Gate 6 — Hygiene scanner (`hygiene_scan.py`)

Scans for proof-shortcut tokens: `sorry`, `admit`, custom `axiom`, `by decide`/`by exact?` abuse, `irreducible`. Two modes: render-stage (a single `:= by sorry` placeholder allowed during statement rendering) and `--prove-stage` (any `sorry` is a violation once a proof is claimed complete). **Does not catch** `sorry` smuggled via meta-programs — that is Tier 2 (`hygiene_axioms.lean`, `#print axioms`, local agent's job).

## Gate 5 — Vacuity / non-triviality scanner (`vacuity_scan.py`)

Scans for the **dishonest placeholder** pattern: definitions/theorems whose bodies are vacuously true or trivially constructed — "compiles but means nothing." This is the gap Gate 6 doesn't cover: a `sorry` is *honest* (it admits incompleteness), but a `theorem ... : True := by trivial` or `def ... := ∀ x, x ∈ L ↔ True` is a *fake success* that passes hygiene clean. Catches:

- `theorem`/`lemma` with `: True := by trivial` (or `rfl`/`decide`) — a real-looking theorem proving a triviality. Does NOT flag `: True := by sorry` (that's an honest render-stage placeholder, caught by Gate 6).
- `def` with `↔ True` in the body — vacuous equivalence (the `DecidesInTime := ∀ x, x ∈ L ↔ True` pattern).
- `def` with `:= True` — bare equality to True.
- `def` with `:= none` — constant failure masquerading as an implementation (the `stepCountByEvalsToInTime ... := none` pattern).

**Does NOT catch** vacuity that requires understanding what a definition *means* (e.g. a real-looking but subtly-wrong predicate) — that is Gate 4 (read-back) and the review layer's job. "Gate 5 passed" = Tier 1 + review, not Tier 1 alone.

## Gate 2 — Model-consistency scanner (`model_consistency_scan.py`)

Scans for local redefinitions of canonical types and forbidden namespace usage — the "redefine NP weaker and prove the redefined thing" failure mode (Pattern A, Gate 2 in `docs/ARCHITECTURE.md`). Checks:

- Local `def`/`abbrev`/`notation` of complexity-class names (`P`, `NP`, `PSPACE`, `Oracle`, etc.) *outside* the `PleaNP.*` namespace — these should be imported from upstream (DEC-003) or defined under `PleaNP.*`, not as bare top-level names. Tracks namespace context (including nested namespaces inside docstring blocks) so qualified `PleaNP.Oracles.Oracle` defs are NOT false-flagged.
- Usage of the `Complexity.*` namespace — forbidden per DEC-002.

**Does NOT catch** a subtly-weaker redefinition using a different name (e.g. `def MyNP := ...`) — that is Gate 4 (read-back) and the review layer's job. "Gate 2 passed" = Tier 1 + review.

## Gate 8 — Unicode-hygiene scanner (`unicode_scan.py`, 2026-09-12)

Scans for **stray, non-valid characters** in tracked source (`.lean`, `.py`, `.md`, `.yaml`, `.yml`, `.json`, `.toml`) — the class of LLM/CJK-IME authoring artifacts that are not valid parts of Lean 4, the metaprogramming layer, or the project's English prose:

- **fullwidth/halfwidth forms** U+FF01..U+FF5E + U+FF61..U+FFEF (fullwidth parens `U+FF08`/`U+FF09`, fullwidth comma `U+FF0C`, fullwidth plus `U+FF0B` — ASCII swaps)
- **CJK punctuation** U+3000..U+303F (ideographic full stop `U+3002`, ideographic comma `U+3001`, corner-bracket/quote forms) and CJK radicals U+2E80..U+2FDF
- **CJK ideographs/kana/hangul** (keeps non-English text out of the tree)
- **invisible format chars**: zero-width space/joiner (U+200B..U+200D), LRM/RLM/bidi controls (U+200E..U+200F, U+202A..U+202E), invisible operators (U+2060..U+2064), BOM/soft-hyphen/line-sep
- **combining diacritics** U+0300..U+036F — flagged when standalone or glued to a non-letter (the `U+0304`-before-digit heading corruption and the `U+0368`-after-space corruption); legal after a Letter (B + U+0303 = B-tilde, the only correct spelling, used in the Algebrization spec)
- **Devanagari danda** U+0964
- **circled/enclosed alphanumerics** U+2460..U+24FF (enclosed digits like `U+2463` — authoring artifacts as section refs)
- **variation selectors** U+FE00..U+FE0F — VS-16 legal only after an allowed emoji base (the `U+26A0`+`U+FE0F` warning sign used in CLI output)

**Allows** the repo's genuine non-ASCII: Greek, math operators/arrows (∀ ∃ ∈ ⊆ ▸ ⟨⟩ ℕ ∅ …), en/em dash, curly quotes, superscripts/subscripts, box drawing, emoji with VS-16, precomposed accents, and the two bidi-sensitive files' LRM (`docs/decisions/LOG.md`, `docs/LEAN_FORMALIZATION_LESSONS_2026-09-10.md`) reported as SOFT. An audited `--allow` / `--allow-file` escape hatch exists for a future file that genuinely needs a form (document it there, not by smuggling).

Run: `python3 tooling/gates/unicode_scan.py .` — exit 0 clean, 1 violations, 2 usage error.

## REVIEW items on the clean modules (issue #56)

A scan that exits 0 can still print `REVIEW` items (non-fatal findings).
The known REVIEW items on the clean modules — the three
`OracleSmoke.lean` `by decide` smells, the three `OracleV5Tests.lean`
`by decide` smells, the three binder-usage REVIEWs
(`abstractPVsNP_iff_verdictB`, the `NP_A` weak witness,
`P_A_subset_NP_A`), and the two challenge-module REVIEWs on
`PleaNP.Challenges.Relativization` (`equalizing_oracle_statement` /
`separating_oracle_statement`, consumed by the comparator JSON pin
`lean/ComparatorChallenges/Relativization.json`) — are all
**demonstrated-intentional**; their verification and disposition
register live in `docs/GATE_REVIEW_NOTES.md`. When an audit sweep or a
future scan run hits one of these, check that register before
re-flagging it. (`emptyOracle` was a register item until 2026-09-13 —
`OracleV5Tests.lean` (#40) now references it, so it is no longer
flagged.)

## Two tiers (different agents, different trust boundaries)

Both gates are implemented in two tiers, because the sneaky cases require the Lean toolchain:

### Tier 1 — Python scanners (this directory, present)

`hygiene_scan.py` (Gate 6) and `vacuity_scan.py` (Gate 5). No Lean toolchain needed — they read source as text/AST. Run in the remote authoring environment and in CI. **Deliberately partial**: they catch the mechanical patterns, not the semantic ones.

### Tier 2 — Lean-dependent checks (local agent's job)

- Gate 6 Tier 2 (`hygiene_axioms.lean`, spec): `#print axioms` on each frozen statement, checking the axiom set is exactly Mathlib's standard. Catches sorry-smuggled-via-meta. complexitylib's `AxiomGuard` is the prior art.
- Gate 5 Tier 2: (future) a Lean-dependent check that a statement isn't vacuous under the chosen axioms — requires evaluating the statement's semantic content, which needs the Lean kernel.

## What the gates accept / reject

- **Accept:** a frozen statement whose only `sorry` is the render-stage placeholder (Gate 6) and whose definitions have real (non-vacuous) bodies (Gate 5).
- **Reject:** any `sorry`/`admit` in a proven theorem (Gate 6); any `theorem : True := by trivial` or `def := ∀ ... ↔ True` or `def := none` (Gate 5).
- **Flag (not auto-reject):** `by decide` / `by exact?` (Gate 6 smell); `irreducible` (Gate 6 review).

## Scope honesty

Tier 1 alone is **not Gate 5/6 complete.** Treating a grep pass as "Gate passed" is itself an integrity hole. The gates are "passed" only when *both* tiers run. The remote authoring agent's role is to ship Tier 1 and the Tier 2 specs; the local agent completes Tier 2.

## CI enforcement (2026-08-18)

Gate 6 Tier 1 (the hygiene scanner) is enforced in CI via `.github/workflows/ci.yml`, which runs `hygiene_scan.py --prove-stage` on every push/PR to main. Additionally, per-file `set_option warningAsError true` pragmas in PleaNP .lean files make `sorry` a hard build failure.

Gate 5 Tier 1 (the vacuity scanner) should be added to CI alongside the hygiene scanner (run `python3 tooling/gates/vacuity_scan.py lean/PleaNP` in the same workflow). This is a pending CI update — see `docs/STATEMENTS/HygieneEnforcement.spec.md`.

Note: this enforces Tier 1 (grep/AST-scannable patterns) only. Tier 2 (`#print axioms`; semantic vacuity) is still the local agent's separate job. "CI green" is necessary, not sufficient, for "Gate 5/6 passed."

## Gate: prose-corruption scanner (`prose_scan.py`, 2026-09-16)

`prose_scan.py` catches the **#101 signature** — words fused where punctuation
absorbed the following space, and punctuation doubled (`,,`, `;;`, `..`,
`word:joined`, `word,joined`, `word;joined`, `word)joined`). It is the general
guard for the case the unicode scanner cannot see: the corruption is plain
ASCII.

What it scans: Lean **comments** and Lean **string-literal contents** (the
`#barrier_check` verdict templates are machine-authored prose inside `m!"..."`
literals, and they carried the signature too); markdown prose (including
`docs/` and `blockers/`). Code is never flagged. Before matching it blanks
inline code spans and space-free bracketed groups, so legitimate Lean tuple
notation (`⟨n,x⟩`, `(true,true)`) is not mistaken for a fused comma; on
markdown it also skips fenced code blocks (file-level: fences span lines), and
masks links, URLs (`ghcr.io/...:tag`), and the legitimate `status:available` /
`File:Line` label tokens. The doubled-period rule requires whitespace after the
`..`, so it excludes ellipsis (`...`) and path/range forms (`../x`, `Pass 1..n`,
`U+200E..U+200F`) while still catching #101's canonical `rationale.. Issue` case.

Run: `python3 tooling/gates/prose_scan.py .` — exit 0 clean, 1 violations,
2 usage error. `--allow-file <path>` is the audited escape hatch. CI runs it on
the whole tree (scan + unit tests); the unit tests pin the false-positive
classes (tuples, code spans, ellipsis, ranges, markdown paths/URLs/labels) so a
future loosening is a test failure.

## Gate: workflow-file integrity scanner (`workflow_scan.py`, 2026-09-16)

`workflow_scan.py` asserts that every `.github/workflows/*.yml` (a) parses
under `tooling/galaxy/miniyaml.py` (the repo's stdlib parser — no PyYAML), (b)
has the structure GitHub requires (non-empty `jobs` mapping; `steps` a list of
mappings; each step carrying exactly one of `uses`/`run`; no unknown step
keys), and (c) is free of the **#101 corruption signature** — a step-boundary
token (`- name:`/`- uses:`/`- run:`/…) that does not begin its line, i.e. a
step swallowed into the preceding scalar.

This exists because that signature reached `.github/workflows/ci.yml` on `dev`
and three swallowed step boundaries would have made GitHub **reject the whole
workflow** — a silent failure nothing in the repo caught until a human diffed
it (`1037101` repaired it; #101 recorded the pattern, #110 landed this guard).
The unit tests (`tests/test_workflow_scan.py`) include the pre-`1037101`
corruption as a regression fixture, so a guard that stopped detecting it would
be a test failure.

Run: `python3 tooling/gates/workflow_scan.py` — exit 0 clean, 1 violations,
2 usage error. Wired into CI (scan + unit tests).

## Gate: docs-link scanner (`docs_links_scan.py`, 2026-09-30; #46/#172)

`docs_links_scan.py` resolves every backtick-code file ref and markdown link in
`docs/` against the repo tree and reports references that do not resolve to an
existing file. Whitelisted classes (upstream `Mathlib/` paths, `<placeholder>`
refs, `.yaml`/`.yml` manifests, `AGENTS_LOCAL.md`, `Challenges`/`Comparator`
aspirational files, wildcards, and `file:NN` line cites) are excluded. It is a
docs-hygiene check, not a Lean gate: a clean exit means every non-whitelisted
reference in `docs/` points at a real file (or an explicitly-aspirational one
carrying a marker).

Calibrated to exit 0 on `main` in #171 — it resolves terse Lean citations by
bare basename/partial path and strips `file:NN`/`file:NN,MM` line cites before
resolving. This section makes it a **gate**, not just a script: the scan runs in
CI on every push/PR to `main` (`.github/workflows/ci.yml`, step "Docs link scan").

Run: `python3 tooling/gates/docs_links_scan.py` — exit 0 clean, 1 broken refs,
2 usage error. `--report` prints the per-doc breakdown. Wired into CI.

## Wired vs. manual gates (2026-09-30; #172)

"Wired" is a decidable property: a gate script is **CI-wired** iff its own check
(or a smoke invocation of it) is run from `.github/workflows/ci.yml`. A script
whose *unit tests* run in CI but whose *check* does not is **manual check,
CI-wired tests** — the tests pin the scanner's behaviour, but the check itself is
invoked on demand during authoring, not per-push. This register exists so a
"wired" claim is checkable rather than assumed.

| Gate script | Status | Rationale |
|---|---|---|
| `docs_links_scan.py` | **CI-wired (scan)** | Docs-hygiene scan, stdlib-only, deterministic; step added to CI in #172. |
| `lean_readback.py` / `readback.py` | **CI-wired (smoke + tests)** | The read-back smoke step runs a real declaration, and `test_readback.py` runs in CI. The LLM-backed translator half stays off by default (DEC-021 — PleaNP uses no external LLM). |
| `statement_lint.py` | **CI-wired (smoke + tests)** | Smoke on two authored statements plus `test_statement_lint.py` run in CI. |
| `multi_render.py` | **Manual check, CI-wired tests** | `test_multi_render.py` runs in CI. The driver is invoked per-target during authoring (each `churn/<slug>/` campaign is worked individually), so it is not a per-push gate. |
| `corpus_campaign.py` | **Manual check, CI-wired tests** | `test_corpus_campaign.py` runs in CI (counted-table regression guard). Collation runs per-campaign during authoring. |
| `pass_scan.py` | **Manual check, CI-wired tests** | `test_pass_scan.py` runs in CI. The scan is a live-GitHub queue-health sweep (`GITHUB_TOKEN`), run as a start-of-session sweep step, not a per-push CI gate. |
| `effort_summary.py` | **Manual check, CI-wired tests** | `test_effort_summary.py` runs in CI. The re-sum needs live GitHub (or a JSON dump) and is run on demand when the effort ledger is updated. |

## Gate 7 (Tier 1): binder usage / lethality scanner (2026-08-18)

`binder_usage_scan.py` checks that every named parameter, field, and
bound variable in a definition is load-bearing (actually used in the
body). Catches:
- Unused definition parameters (Flaw A shape)
- Declarations never applied / fields never read (Flaw B shape)
- Bound variables absent from their own conjunct (Flaw C shape)

Usage:`python3 binder_usage_scan.py lean/PleaNP`

See `docs/VALIDATION_SUITE.md` for the full validation requirements.

## Gate 3 — Multi-rendering driver (`multi_render.py`)

The multi-rendering engine — "AI produces many renderings; humans mine the
shape." Pipeline (`init` → `render` → `check` → `mine`): independent Lean
renderings of one informal claim are registered in `churn/<slug>/renderings/`,
pairwise machine-verified equivalent via `dual_render`,ford disagreements
become **review points** in the review inbox (`review_inbox.py`; one plain-
language question each), filed as GitHub issues by `review-issue.yml`.

**Merge/registration step (`merge <slug>`; 2026-09-07,#25).** Pulls each
contributor's submission manifest (`churn/<slug>/submissions/<slot>.json`) into
`renderings/`,then re-runs `check`(+ `churn/<slug>/lemmas.json` if present)
and `mine` on the merged set. **Idempotent**: re-running is harmless — re-
registration overwrites the same `<id>.json`,check rewrites `matrix.json`,and
`mine` dedupes review points by stable key (`run` + `decl` pair), so no
duplicate pending points nor GitHub issues are filed (the #7-#16 double-
filing bug class; see `review-issue.yml`'s inbox-id dedupe).

Usage: `python3 tooling/gates/multi_render.py merge <slug> [--lean-dir lean]`

## Process compliance — pass-sizing scanner (`pass_scan.py`, 2026-09-12)

`pass_scan.py` enforces the multi-run pass-sizing rule in
`docs/MULTI_AGENT_WORKFLOW.md` §Task definition: any open issue whose
`**Effort:**` line claims ≥2 runs must carry an explicit `**Passes:**` block
(Pass 1..n, each = one run) so long-horizon epics are worked as successive
claimable passes rather than one oversized claim. Single-run issues and
design/decomposition tasks (whose deliverable *is* the pass list) are exempt.

- **Violation** (exit 1): multi-run `Effort` without a `Passes` block.
- **Warning** (exit 0): `Passes` block counts fewer pass lines than the
  `Effort` max (under-specified), or (with `--warn-no-effort`) legacy issues
  with no `Effort` line.
- **Usage:** `python3 pass_scan.py` (live GitHub, needs `GITHUB_TOKEN`; the
  52 open issues scanned 2026-09-12 give 0 violations) or
  `python3 pass_scan.py --json-file issues.json` (offline, same shape).
- **Sweep step.** Since 2026-09-12 the scanner is a **mandatory start-of-session
  sweep step** (§Claiming step 1a): every sweep runs it and acts on the output
  per the sweep action table (violation → add the `Passes` block or split the
  epic; under-spec warning → complete the pass lines or tighten `Effort`;
  no-Effort → backfill). Umbrella multi-claim epics (e.g. #76) are filed as one
  `status:available` sub-issue per pass so the umbrella's warning resolves
  instead of lingering.
- **Not a Lean gate** — a queue-health scan, like the stale-claim sweep.

## Effort re-sum (`effort_summary.py`, 2026-09-12)

Reproducible recomputation of the per-rung run totals in `docs/EFFORT_ESTIMATE.md`
by summing each in-scope issue's `**Effort:**` line from the live queue (or an
offline JSON dump). One command replaces hand-summing the ledger:

- **Output:** per-rung totals, in-scope total (Rungs 2–8), proof-search entry
  (Rungs 2+3+4+5+6), and the unblocked-now vs upstream-gated (Rung 6) split.
- **`--csv`:** per-issue rows (issue, rung, effort_lo, effort_hi, title).
- **`--table-rows`:** Markdown table rows for `docs/EFFORT_ESTIMATE.md`.
- **Rung map** (`RUNG_MAP` in the file): the single source of truth for
  issue→rung; keep in sync with the ledger when tasks are filed, closed, or
  re-runged.
- **Usage:** `python3 effort_summary.py` (live, needs `GITHUB_TOKEN`) or
  `python3 effort_summary.py --json-file issues.json` (offline). Unit tests in
  `tests/test_effort_summary.py`, CI-wired.


## Rung-5 `#barrier_check` verdict harness (`barrier_check_test.py`; 2026-09-07; #3; extended #170)

Asserts the `#barrier_check` verdicts logged by the elaborator during compile:

  - `PleaNP.Calculus.thhStatement`            -> "relativizes, not P-vs-NP-shaped"
  - `PleaNP.Calculus.abstractPVsNP`           -> "DEAD"
  - `PleaNP.Calculus.plainRelHeuristic`       -> "relativizes, not P-vs-NP-shaped"
  - `PleaNP.Calculus.nonRelativizingControl`  -> "Inconclusive"
  - `PleaNP.Calculus.concreteClassMembership` -> "DEAD"
  - `PleaNP.Calculus.bgsMetaStatement`        -> "Inconclusive"
  - `PleaNP.Barriers.Williams.williams_transfer`             -> "Inconclusive"
  - `PleaNP.Barriers.Williams.NEXP_not_subset_ACC0`          -> "Inconclusive"
  - `PleaNP.Barriers.Williams.williams_lower_bound_compiled` -> "Inconclusive"

The elaborator's verdict print via `logInfo`;CI's build step `tee`s its output
to a log file, then the harness runs on that log and fails if any expected
verdict segment is missing or wrong - so a regression (a DEAD flipping to
Inconclusive, an instance that stops synthesizing, a message rewrite) kills
the build mechanically. Dash-family chars are folded before matching
(terminal/encoding-tolerant).

**Drift guard (#170).** The final three assertions and the `--check-drift` mode
close the hole behind the audit's "a check that cannot fail is not a check"
finding: the harness only asserts declarations it knows about, so a new
`#barrier_check <decl>` added to a Lean module compiled green with its verdict
unasserted. `--check-drift [LEAN_ROOT]` scans the Lean sources (comments
stripped), and CI fails if any `#barrier_check` invocation is absent from
`EXPECTED`. It is stdlib-only and needs no Lean toolchain. Unit tests:
`tests/test_barrier_check_test.py` (stdlib, no Lean, no secrets).

Usage: `python3 barrier_check_test.py <build-log>` (or `--run-lake [MODULE]`
to build locally first, or `--check-drift [LEAN_ROOT]` to scan the sources).
See `docs/STATEMENTS/BarrierCheckVerdicts.spec.md`.