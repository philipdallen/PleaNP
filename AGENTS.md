# AGENTS.md

> Condensed project reference for AI agents working in this repo. Dense by design.
> For human-readable introductions see `README.md`; for the rung ladder see `docs/ROADMAP.md`.


## Portfolio front door — read this before you start work

This repository is one part of a wider portfolio. Before you claim or start work
here, spend five minutes in **`philipdallen/portfolio-ops`** (private), in this order:

1. `HANDOFF.md` — current portfolio state, what is blocked and on whom.
2. `EXECUTION_PLAN.md` — the week's priorities and the sequencing principles.
3. `RISK_REGISTER.md` and `AGENTS.md` — open risks, and the rules that apply to you.

Why this is worth five minutes: it is the only place that records **decisions already
made** and **work already owned by a human**. Skipping it is how a session redoes
someone else's work, contradicts a recorded decision, or spends its run on something
a human must do anyway.

**If you are an unattended automation run, skip this step** — the operating contract
is already inlined at the top of your prompt, and this orientation is for
human-directed and ad-hoc sessions.

**Do not confuse the two queues.** Work here is claimed and executed locally. Janitorial
work — lint sweeps, stale references, mechanical hygiene — is deliberately tracked
privately in `portfolio-ops`, not filed here. If you find mechanical work, do not file
it publicly; note it in your run output so it can be routed.

## Branches

`main` is the working branch and the GitHub default — every commit lands here, and it is
the branch visitors and all tooling read. `dev` also exists and is kept level with `main`;
it is a legacy name, and nothing should be committed to it. If the two ever differ, treat
`main` as authoritative.

**Edit workflows on `main`.** A `schedule:` trigger fires only from the default branch, so
a workflow that exists only on `dev` will not run. The sweep and audit workflows check out
`main` and push there for the same reason — the status snapshot must land where the default
branch points, or the dashboard reads a stale log.
## Project overview

PleaNP is a Lean 4 / Mathlib project that formalizes the **barrier landscape** of computational complexity theory — the meta-theorems (relativization, natural proofs, algebrization) showing which proof techniques provably cannot resolve P vs NP — plus the circuit-complexity and proof-complexity infrastructure those barriers require.

- **Domain:** computational complexity theory (Lean 4 / Mathlib)
- **Core contribution:** the first formalized barrier library + the integrity gates that make AI-assisted proof search honest
- **Deliberate non-goal:** defining P/NP/reductions from scratch (upstream Mathlib's job — see `docs/UPSTREAM_TRACKING.md`)

## Key terms

| Term | Meaning |
|---|---|
| **Barrier** | A meta-theorem proving a class of proof techniques cannot resolve P vs NP |
| **Relativization** | Baker–Gill–Solovay (1975): relativizing proofs can't separate P from NP |
| **Natural proofs** | Razborov–Rudich (1994): natural lower-bound techniques would break OWFs |
| **Algebrization** | Aaronson–Wigderson (2008): third barrier, refining the first two |
| **Gate** | A validation step in the integrity pipeline (see `docs/ARCHITECTURE.md`) |
| **Rung** | A level in the development ladder (see `docs/ROADMAP.md`) |

##The rung ladder (summary)

| Rung | Goal | Status |
|---|---|---|
| 1 | Gap audit of Mathlib complexity coverage | Done (see `docs/GAP_AUDIT.md`; track upstream changes) |
| 2 | Computational model + canonical P/NP (upstream-tracked) | Blocked on upstream |
| 3 | Formalize the barrier theorems | Not started |
| 4 | Formalize lower-bound techniques + their failures | Not started |
| 5 | **Barrier Calculus** (Relativizing typeclass + `#barrier_check`; unit-test vs. THH) | In progress (prototype in `lean/PleaNP/Calculus/`) |
| 6 | **Anchor Object** (P/NP model-equivalence anchor + Levin-search `P_eq_NP_iff`) | Blocked on upstream (gap lemma formulable once one model lands) |
| 7 | Graded benchmark | Not started |
| 8 | **Lower-Bound Compiler**(Williams transfer as a Lean elaborator) | Not started (placeholder note in ROADMAP) |
| 9 | AI proof-search loop (retrieval + gates) | Not started |
| 10 | Open problems below P vs NP | Not started |
| 11 | Novel barrier-evasion arguments | Not started |

Scope note (2026-09-06, DEC-012): three components added — Barrier Calculus (Rung 5), Anchor Object (Rung 6), Lower-Bound Compiler (Rung 8) — in that priority order. Core bet: *negative-space specification* — formalize the constraints a proof must satisfy, not the proof itself;, `#barrier_check` is the demand-pull artifact. Update `docs/ROADMAP.md` for the full rung details.

## File map

| Path | Contents |
|---|---|
| `README.md` | Human-readable project introduction |
| `docs/GAP_AUDIT.md` | Rung 1 deliverable: Mathlib gap analysis + upstream tracking |
| `docs/ROADMAP.md` | The rung ladder with detail |
| `docs/ARCHITECTURE.md` | The gate pipeline (integrity architecture) |
| `docs/FAILURE_AUDIT.md` | Prior attempts at "formalized P vs NP" and how they failed |
| `docs/PRIOR_ART.md` | Cross-assistant prior-art survey + AI-tooling landscape (validates "no barriers formalized anywhere") |
| `docs/LEAN_FORMALIZATION_LESSONS_2026-09-10.md` | **Lessons from the 2026-09-08 AI-assisted Navier–Stokes/Euler Lean releases** (`openai/NavierStokesAndEuler`, `tristanbuckmaster/fluid_lean`) — verified facts, what they do/don't establish, three adoptions (Comparator challenge, `formalization.yaml`, standalone-paper-theorem files) per DEC-022, and anti-patterns not copied. Read before touching statement-fidelity machinery or the BGS proof path (`#18`). |
| `docs/STATEMENTS/ComparatorChallenge.template.md` | **Template: independent machine-checkable reference statement ("Comparator challenge") for every frozen PleaNP statement** (DEC-022): challenge module in `lean/PleaNP/Challenges/` must **not** be imported bythe proof root; JSON pin(theorem names + `permitted_axioms`); `lake exe comparator`-style check when available. **Read before rendering any barrier statement into Lean.** |
| `docs/STATEMENTS/ProofIntuition.template.md` | **Template: proof-intuition record (human-legibility deliverable for an AI-discovered formal claim,** DEC-023: 5-layer plain-words construction, load-bearing-choice audit, perturbation tests, cheap-outs confession, steelman, reviewer checklist——the "explanation" slot authority at the frontier. File per AI-discovered claim, reviewed with Gate 4,before citing as authoritative. **Run the load-bearing-choice audit (also in `docs/VALIDATION_SUITE.md`) alongside Gate 4 for any barrier/lower-bound proof.** |
| `formalization.yaml` | **Repo-root machine-readable statement manifest (v0.4, DEC-022):** per declaration: informal source ↔ Lean declaration ↔ file ↔ sorry_count ↔ axioms ↔ comparator_config ↔ review status. Declarative data; the gate scanners remain the executables. **Checked artifact — must be parse-valid YAML at commit time** (parsed by `tooling/galaxy/miniyaml.py`; Galaxy/CI consume it). Add/update rows in the same commit as every proof freeze (same rule as `docs/SORRY_TRACKER.md`). |
| `docs/PLAYBOOK.md` | **Prior groundwork indexed by trigger point** — at each rung / workflow step, which prior art applies and what to do with it (imitate / import / cite / avoid). Consulted at workflow Step 0 and when starting a rung. Keeps the learnings actionable instead of rediscovered. |
| `docs/SORRY_TRACKER.md` | Tracks every open `sorry` in the Lean codebase — what it's pending on, what unblocks it, and its priority. Prevents `sorry`s from being forgotten or filled in wrong. **Update when adding/resolving a `sorry`.** |
| `docs/UPSTREAM_TRACKING.md` | Tracking the active Mathlib complexity efforts (currently #1–#8) |
| `docs/VALIDATION_SUITE.md` | Validation suite requirements — must-prove lemmas, must-refute lemmas, smoke tests, the typed → validated → frozen status ladder, red-team pass, and CI staging rules. **Read before claiming any definition is "frozen" or "validated."** |
| `docs/STATEMENTS/` | **Frozen, human-verified statement specs (Gate 1 anchors / Gate 4 read-back refs).** One per barrier theorem, plus the oracle-machine design spec. Six-part template, prose-only (no Lean rendering — that's the local agent's job). Start here when beginning Rung 2 (oracle substrate) or Rung 3. |
| `docs/STATEMENTS/README.md` | Why a non-Lean driver writes the specs; the template; index of the specs |
| `docs/MATHLIB_SUBMISSION.md` | **Submitting to Mathlib (2026-09-06):** the real process (Zulip-first, small PRs, bors/CI), the 5 realistic rejection paths (too-early, too-big, design-objection, duplicate, substantive-criticism) and how to handle each, the **rejection-lessons log** (record root cause, gate that catches it, fix, lesson for every rejection), and the reputation non-negotiables (never submit a sorry; submit the oracle substrate not the barrier theorems; cite prior art; follow process; one human anchor). Read before any Mathlib submission. |
| `docs/CREATIVE_PROTOCOL.md` | **Idea-generation for hard steps (2026-09-06, DEC-019):** structured creative protocol (excavate/cartograph/transplant/synthesize/bridge). For hard open-ended sub-tasks: run it to generate novel candidate strategies, then route through the gates. Novelty without verification is crank-adjacent. |
| `docs/EXPLAINER_P_VS_NP.md` | **A plain-words explainer of P vs NP and PleaNP** (no math background needed, no external links) — for podcast/explainer use. Covers checking-vs-solving, Turing machines, oracles, the three barriers, Lean 4, the AI pipeline, and the GitHub workflow. |
| `docs/AGENT_HANDOFF.md` | **START HERE for a new agent context (2026-09-06):** how to pick up work from the issue queue (one claim, run-ids, sweep, gate evidence), current repo state, and the highest-value open issues. Read this + MULTI_AGENT_WORKFLOW + AGENTS.md before claiming anything. |
| `docs/REVIEW_INBOX.md` | **The human review surface (2026-09-06):** non-blocking, async inbox. Agents file one review point (one claim = one plain-language question) and never wait; the human reads `reviews/INBOX.md`, answers `confirm`/`flag`, and a flag reopens the claim retrospectively. Multi-stream safe. Read before asking the owner to review anything. |
| `docs/STATEMENTS/HUMAN_REVIEW_LAYERS.md` | **How the non-proof-writing owner reviews semantics:** the three-layer map (mechanical / read-back / probe-checklist) + the tiny vocabulary list (exists-vs-forall, subset-direction, at-most-vs-exactly, oracle, witness). Answer 3–5 single-choice probes; never read Lean, never arbitrate. Read before asking the owner to approve any claim. |
| `docs/STATEMENTS/SEMANTIC_APPROVAL.md` | **How the non-Lean-literate owner approves semantics**: two independent read-backs must agree, concrete must-prove/must-refute examples, `#barrier_check` verdicts, gate evidence — never read Lean, never adjudicate conflicting translations. Read before asking the owner to approve any claim. |
| `docs/STATEMENTS/Oracle.lean.spec.md` | Rung 2 local piece — oracle-machine design spec (totality discipline, Mathlib composition, acceptance criteria). v1 built against TM1 (partial); §4 superseded by the TM2 recompose. |
| `docs/STATEMENTS/OracleTM2Recompose.spec.md` | Oracle.lean v2 recomposition spec — DEC-010 Option B: recompose against core `TM2ComputableInTime`'s step-counting. The three traps (function→language bridge; oracle query = 1 step in `EvalsToInTime`; `P^∅ = P` compatibility). **Read before recomposing Oracle.lean.** |
| `docs/STATEMENTS/OracleComplexity.lean.spec.md` | P^A / NP^A complexity-class spec — the layer on top of `Oracle.lean`. The four traps (polynomial-bound encoding; nondeterminism encoding; extensionality; `P^∅ = P` carry-through). Waits on `Oracle.lean` freeze. |
| `docs/STATEMENTS/Relativization.md` | Rung 3a spec (Baker–Gill–Solovay 1975) — cleanest first barrier target; waits on Oracle.lean.spec |
| `docs/STATEMENTS/Relativization.lean.spec.md` | BGS Lean *statement* rendering spec — the Gate-1 frozen formal target for `lean/PleaNP/Barriers/Relativization.lean`. Three rendering traps (computability hypothesis; set-vs-predicate equality; query-type parameter). Waits on `OracleComplexity.lean`. |
| `docs/STATEMENTS/Relativization.proof-strategy.md` | Informal BGS proof strategy (sandwich + diagonalization). **NOT a frozen proof spec** — prep doc; frozen proof spec comes after statement freeze |
| `docs/STATEMENTS/NaturalProofs.md` | Rung 3b spec (Razborov–Rudich 1994) — OWF as hypothesis, not constructed |
| `docs/STATEMENTS/NaturalProofs.proof-strategy.md` | Informal RR proof strategy (natural-property→distinguisher reduction). NOT a frozen proof spec |
| `docs/STATEMENTS/Algebrization.md` | Rung 3c spec (Aaronson–Wigderson 2008) — AW09 multiquadratic v1 pinned |
| `docs/STATEMENTS/Algebrization.proof-strategy.md` | Informal AW09 proof strategy (low-degree extension + hiding lemma + two-sided oracles). NOT a frozen proof spec |
| `docs/STATEMENTS/LOCAL_AGENT_WORKFLOW.md` | The test-as-you-go loop the local agent follows to turn specs into validated Lean (Steps 0–6: substrate check → render → hygiene → model-consistency → read-back → freeze → proof search). **Read before any Lean execution.** |
| `docs/STATEMENTS/HygieneEnforcement.spec.md` | CI hygiene enforcement spec — sorry-as-error + Mathlib linters + `.github/workflows/ci.yml`. The "stricter compiler" lever; local agent's job (needs `lake` + CI run). |
| `docs/STATEMENTS/Oracle.v4-repair.spec.md` | **DRAFT repair work order (track A)** — v3→v4 reachability wiring for `Oracle.lean`/`OracleComplexity.lean`. v3 headers claim the three flaws are fixed but the bodies are still vacuous (Flaw A: `DecidesInTime` no `EvalsToInTime`; Flaw C: `AcceptsInTime` vacuous + applied to `x` not `(x,y)`; plus a duplicate-binder compile bug). Has exact Mathlib v4.31.0 API signatures + code templates. **Read before the v4 repair.** |
| `docs/decisions/LOG.md` | Chronological decision log (DEC-0XX) |
| `docs/MULTI_AGENT_WORKFLOW.md` | **Task coordination (muse-adapted, 2026-09-06):** one task = one GitHub issue; run-ids, atomic label claims (`status:available/claimed/done/blocked-needs-input`), blockers dir, sweeps, end-of-session report. **Read before claiming any issue.** |
| `docs/CONTRIBUTIONS.md` | **Community/Zulip intake:** how external contributors file issues/PRs, how contributions are triaged into the queue and passed through the integrity gates. |
| `lean/PleaNP/Computability/Oracle.lean` | **Oracle machine (v4):** oracle type (`Oracle Q := Q → Bool`, total by construction), `Cfg`/`Machine` (FinTM2 + oracle + query/yes/no labels), `step` (branches on query label, consults oracle, routes to yes/no label — load-bearing), `DecidesInTime` (halts + output encodes χ_L), `outputEncodesChi`, `step_none`, `evalsTo_unique_result` (determinism of halted endpoints). **Builds green** (0 sorries). |
| `lean/PleaNP/Computability/OracleComplexity.lean` | **P^A / NP^A complexity classes (v4):** `P_A` (composes `DecidesInTime`; query-alphabet constraint `hΓ : tm'.Γ tm'.k₀ = Q`, `M.oracle = hΓ.symm ▸ A`), `NP_A` (uses per-input `AcceptsInTime` — Flaw C fix), `P_A ⊆ NP^A` (**proved both directions** via `evalsTo_unique_result`). **Builds green** (0 sorries). |
| `lean/PleaNP/Computability/OracleSmoke.lean` | **Oracle-sensitivity smoke test:** one machine program (`smokeTM`), two oracles (`oracleTrue`/`oracleFalse`) — `smoke_accepts_true` (accept, by evaluation) and `smoke_rejects_false` (reject, by determinism + evaluation). The executable check that Flaw B stays fixed. **Builds green.** |
| `lean/PleaNP/Computability/OracleUpstreamP.lean` | **Upstream-P tracking anchor:** `P_empty_eq_upstream_P_class` (2 sorries, including a statement-level sorry — Gate-5 concern, pending upstream P / DEC-003). Isolated so `warningAsError` doesn't cascade. **Expected to fail the build** until upstream P lands. |
| `docs/ACTIVATION_CHECKLIST.md` | **DEC-013 owner checklist:** what is automated vs. the one remaining human step (GitHub account billing lock blocks Actions/Codespaces job starts). Check here first when CI is red or a Codespace fails to boot. |
| `.devcontainer/` | **DEC-013 Active:** warm Lean 4 + Mathlib devcontainer (elan + lean4 extension; `postCreateCommand` runs `lake exe cache get` + builds the clean modules). The browser-based persistent environment (Codespaces/Gitpod). |
| `docs/TOOLCHAIN_SOLUTIONS.md` | Persistent & cloud toolchain options for Lean 4 + Mathlib (devcontainer/Codespaces/Gitpod, CI-as-build-oracle, lean4web playgrounds, cache-based compartmentalization). The "how to get a warm Lean env without the M4 box or a from-scratch sandbox build" reference. Recommendation for a future DEC — not yet a decision. |
| `lean/PleaNP/Barriers/Relativization.lean` | **BGS statement (rendered):** `exists_equalizing_oracle` (clause a) and `exists_separating_oracle` (clause b), both `sorry`'d. Quantifies over `P_A`/`NP_A` from `OracleComplexity.lean`. **Not frozen** — depends on unvalidated class definitions. |
| `lean/PleaNP/Calculus/BarrierCalculus.lean` | **Rung 5 (new, in progress):** `Relativizing` prop-carrying typeclass + composition/application/quantifier propagation instances + `#barrier_check` elaborator (walks dependency closure; emits `DEAD: this proof relativizes` if every leaf relativizesand the conclusion separates/collapses `P`/`NP`, else `Inconclusive`) + time-hierarchy-theorem unit test(THH is relativizing — must emit DEAD). Meta-level: does NOT depend on upstream P/NP substrate. |
| `tooling/gates/hygiene_scan.py` | Gate 6 Tier 1: scans for `sorry`/`admit`/`axiom` in Lean source. `--prove-stage` treats every `sorry` as a violation (for freeze PRs); without it, `sorry`s are tracked warnings. |
| `tooling/gates/unicode_scan.py` | **Gate 8 Tier 1 (2026-09-12):** scans tracked source for stray/non-valid characters (fullwidth ASCII swaps U+FF01..FF5E, CJK punctuation U+3000..U+303F, zero-width/bidi/format chars, stray combining diacritics, Devanagari danda, circled digits) — the LLM/CJK-IME authoring-artifact class. Allows the repo's genuine math/Lean glyphs, emoji with VS-16, and reports LRM in the two bidi-sensitive files as SOFT (exit 0). Audited `--allow`/`--allow-file` escape hatch. **Run before committing ANY doc/code change that may carry foreign or invisible characters.** |
| `tooling/gates/vacuity_scan.py` | Gate 5 Tier 1: scans for `True := by trivial`, `↔ True`, `:= none` patterns (dishonest placeholders). Catches top-level vacuity but not deep vacuity (a `True` buried inside `∃` — see DEC-011). |
| `tooling/gates/model_consistency_scan.py` | Gate 2 Tier 1: scans for local redefinitions of complexity-class names or forbidden namespaces (`Complexity.*`). |
| `tooling/gates/binder_usage_scan.py` | Gate 7 Tier 1 (lethality scanner): checks that every named parameter, field, and bound variable in a definition is load-bearing (actually used in the body). Catches unused params (Flaw A), dead binders (Flaw C), and unreferenced declarations (Flaw B). **Run before claiming any definition is "fixed" or "load-bearing."** |
| `tooling/gates/hygiene_axioms.lean` | Gate 6 Tier 2: `#print axioms` check for sorry-smuggled-via-meta (separate from Tier 1 grep). |
| `tooling/gates/axiom_check.py` | **Gate 6 Tier 2 (CI-wired 2026-09-06):** runs `#print axioms` on the clean-module theorems and fails on any non-standard axiom or `sorryAx` (smuggled sorry via meta-programs). The machine guarantee behind SEMANTIC_APPROVAL. |
| `tooling/gates/lean_readback.py` | **Gate 4 (read-back, deterministic half):** extracts a Lean declaration's type via `lake env lean` and renders a structural English skeleton. Runnable in CI with no secrets. |
| `tooling/gates/readback.py` | **Gate 4 harness (2026-09-06):** two independent translators must AGREE on the plain-English meaning; disagreement BLOCKS the claim. **Architecture (DEC-021): no external LLM — the second translator is an independent OpenHands agent pass, not an API call; the LLM hook is optional/off-by-default.** Unit-tested (stdlib, no secrets). |
| `tooling/gates/dual_render.py` | **Gate 3 harness (2026-09-06):** dual-rendering fidelity. `self` mode = CI-safe single-rendering self-check (prop-shaped); `check` mode = machine-verified equivalence of two independent renderings (rfl/simpa/simp, then parameterized ∀-quantified form) — NOT equivalent = BLOCKED, never a fabricated AGREE. Unit-tested in `tooling/gates/tests/test_dual_render.py`; CI runs both. |
| `tooling/gates/probe_check.py` | **Gate 4 Layer 3 (2026-09-06):** the "probe checklist" for a non-proof-writing, intro-math/CS reviewer (intro-level). Turns a claim into 3–5 tiny independent single-choice probes (quantifier, direction, bound, existence); one wrong answer = BLOCKED with the specific probe named. Specs in `tooling/gates/specs/`; unit-tested in `tooling/gates/tests/test_probe_check.py`; CI runs the approve/block smoke. |
| `tooling/gates/multi_render.py` | **Gate 3 multi-rendering driver (2026-09-06):** the AI-multi-rendering → human-mine loop. init/render/check/mine: N independent Lean renderings per informal claim, pairwise machine-verified equivalence (dual_render), and each DISAGREEMENT becomes a review point the human mines via GitHub issues. Incrementally maps the shape of every barrier. Unit-tested in `tooling/gates/tests/test_multi_render.py`. |
| `tooling/reviews/review_inbox.py` | **Review inbox tool (2026-09-06):** add/index/confirm/flag review points (YAML, one per claim) + generate `reviews/INBOX.md`. Non-blocking by design — agents file and continue; the human answers in batch. Unit-tested in `tooling/reviews/tests/test_review_inbox.py`. |
| `tooling/gates/statement_lint.py` | **Pure-code statement linter (2026-09-06):** classifies a Lean statement's SHAPE (quantifiers, connectives, relations =/≠/⊆/∈, oracle-dependence, class constants) mechanically from its syntax — no LLM, no human. This is the "use Lean itself as validator" answer: the probe facts are machine-derived. It CANNOT decide whether the shape matches an informal intention (Tarski floor) — that single confirmation is the irreducible human step. Unit-tested; CI smoke on authored statements. |
| `tooling/gates/tests/` | Test cases for the gate scanners (case1–case13: placeholder, real-sorry, axiom, smells, clean, dead-binder, clean-binders, unused-param, dead-decl, vacuous-binder, clean, docstring-swallow, elab-check-refs). |

## Build and test

**Lean (agent-sandbox bootstrap — DEC-013; no M4 box or Codespace needed):**
```bash
# 1. elan (Lean version manager) — seconds
tooling/install_elan.sh   # checksum-pinned; see PleaNP #136
export PATH="$HOME/.elan/bin:$PATH"
# 2. toolchain + Mathlib precompiled oleans (community Azure cache) — minutes
cd lean && lake exe cache get
# 3. build the clean modules (v4 substrate + Barrier Calculus compile green)
lake build PleaNP.Basic PleaNP.Calculus.BarrierCalculus \
 PleaNP.Computability.Oracle PleaNP.Computability.OracleComplexity PleaNP.Computability.OracleSmoke
# 4. full tree (fails ONLY on the two documented pending-sorry modules:
# OracleUpstreamP = upstream-P anchor; Relativization = BGS statement)
lake build
```
**Faster cold start for agents (Plan E, 2026-09-13):** the repo pushes a warm
Lean+Mathlib image to `ghcr.io/philipdallen/pleanp:main` on every `main`
push (workflow `warm-toolchain.yml`). Prefer pulling it over the curl-bootstrap
above where Docker is available: `docker pull ghcr.io/philipdallen/pleanp:main`
then mount the repo — elan + Lean + Mathlib oleans already warm. And use
`python3 ../tooling/leancheck.py <module.lean>` (first-error typechecker) +
`watch_leancheck.py` (poll-until-clean) for the edit→check loop. Details:
`docs/TOOLCHAIN_AGENTS.md`, `docs/TOOLCHAIN_SOLUTIONS.md` §Plan E.
CI (`.github/workflows/ci.yml`) runs the same recipe on every push/PR; a sandbox
that reproduces the CI steps is a reliable local oracle. On a long-lived
workstation you can install the toolchain once (`AGENTS_LOCAL.md`, gitignored)
and reuse it.

> Note: exact paths and whether lake is available depend on the local machine.
> See `AGENTS_LOCAL.md` (gitignored, not in this repo).

## Git workflow

**Branch discipline: work on `main`.** `main` is the working branch and the
GitHub default. Commit and push there directly — `git push origin main`
immediately after every commit, before closing the issue or citing the commit in
a done comment. The system of record is `git log origin/main`; work that exists
only in a local clone is invisible to siblings and counts as undone until pushed.

`dev` still exists as a **legacy name**, kept level with `main`. Do not commit
to it. (Before 2026-09-22 the flow was `dev`-first with review before `main`;
that was superseded — see `portfolio-ops` `OPERATING_CADENCE.md` §5.)

```bash
# 1. Work on main
git fetch origin
git checkout main

# 2. Commit (identifies as AI agent)
git -c user.name="openhands" -c user.email="openhands@all-hands.dev" commit -m "message"

# 3. Push
git push origin main
```

The integrity control did not disappear with the branch change: the *review
evidence* requirement still stands (gate commands and their output pasted in the
done comment), and `needs-review` still marks work that a human must accept.
What changed is only where the commit lands.

## Conventions

- **Decision log:** Append-only; format `### DEC-0XX` with Date, Status, Scope, Decision, Rationale
- **Playbook first:** Before starting a rung or rendering a statement (workflow Step 0), consult `docs/PLAYBOOK.md` for the prior groundwork that applies — import / imitate / cite / avoid. When the groundwork moves, update the playbook row in the same commit that changes the plan.
- **Namespace:** Project-specific declarations live under `PleaNP.*`, not `Complexity.*` (that namespace is contested upstream — see `docs/UPSTREAM_TRACKING.md`)
- **Mathlib style:** All Lean code follows Mathlib naming and style conventions
- **Gate discipline:** No proof search runs against a statement that hasn't passed the fidelity gates (see `docs/ARCHITECTURE.md`)
- **Duplicate-work prevention (DEC-026, 2026-09-13):** three rules in
  `docs/MULTI_AGENT_WORKFLOW.md` — (1) the **recent-activity guard** (§Claiming
  step 1): before claiming an `available` item whose subject overlaps a
  recently-active `claimed` item, check `git log origin/main` for sibling
  commits in the last ~1h *even when the claim comment is stale* (an agent can be
  mid-session with an aged comment — the #63 duplicate mode); (2) the
  **claim-race rule**: the *earlier* claim comment wins; the later claimant backs
  off and restores `status:available`; (3) the **duplicate-work rule**: never
  push a second copy of a pass/statement a sibling already landed — drop or
  merge-and-reconcile in one commit.
- **Review-fatigue protection (2026-09-06):** after a review point is confirmed, an agent SHOULD `review_inbox.py perturb <id>` (recheck-control twin with one load-bearing element flipped — it should be flagged) and sweep `review_inbox.py fatigue` in session reports. A human confirming a control = fatigue → the original is AUTO-REQUEUED immediately (no sweep needed; `reopened_by` records it). Controls are disclosed honestly; their identity is not pre-marked.
- **Review-inbox discipline (2026-09-06):** at the irreducible semantic hop, file a review point (`tooling/reviews/review_inbox.py add .`) and CONTINUE — never block on the human. A `flag` reopens the claim in a later sweep; it is not a blocker. One point = one claim = one question. Expected answers come from the Lean, not the wish-list.
- **Barrier-calculus discipline (Rung 5):** Any theorem claiming a P-vs-NP-shaped conclusion (`P = NP`, `P ≠ NP`, or separation of oracle-relative classes) should be triaged with `#barrier_check` before being cited as evidence — if it emits **DEAD: this proof relativizes**, it cannot resolve P vs NP (per BGS). If it emits "Inconclusive," non-relativizing potential survives. The `Relativizing` typeclass is meta-level: instances state "uniform in the oracle," and propagation instances carry it through composition/quantification automatically. New definitions that *should* relativize get explicit `Relativizing` instances; new definitions that can't are the interesting case — leave them instance-free so `#barrier_check` reports Inconclusive. **Do not hand-annotate a whole proof as `Relativizing`** — that would bypass the dependency-walk the elaborator performs.
- **Lethality scan (Gate 5 Tier 1b):** Before claiming a definition is "fixed" or "load-bearing," run `python3 tooling/gates/binder_usage_scan.py --allow-unreferenced '^(exists_equalizing_oracle|exists_separating_oracle|smoke_accepts_true|smoke_rejects_false)$' lean/PleaNP` and require 0 violations. It catches the three 2026-08-19 flaw shapes: unused definition parameters, discarded `let _x := …` bindings, unreferenced declarations, and quantifier witnesses that don't constrain their bodies. Every parameter, binder, and declaration must be load-bearing — verified in the *body*, not asserted in the docstring.
- **Sorry tracking:** Every `sorry` in `lean/PleaNP/` must be recorded in `docs/SORRY_TRACKER.md` — what it's pending on, what unblocks it, and its priority. When you add a `sorry` (new placeholder, new pending proof), add a row. When you resolve one, mark it "Resolved" with the commit. When you push changes that add/remove `sorry`s, update the tracker in the same commit. The hygiene scanner (`tooling/gates/hygiene_scan.py --prove-stage`) catches `sorry`s mechanically; the tracker documents what each one *means* so none are forgotten or filled in wrong (the exact failure mode `docs/FAILURE_AUDIT.md` Pattern A warns about). A `sorry` with no tracker entry is a process violation — add it before pushing.

## Pitfalls to avoid

- Don't define P, NP, or reductions locally — import from upstream Mathlib (track via `docs/UPSTREAM_TRACKING.md`)
- Don't claim the `Complexity` namespace — it's being actively designed by the Mathlib community
- Don't let the same pipeline formalize the statement *and* search for its proof — that's the #1 failure mode (see `docs/FAILURE_AUDIT.md`)
- Don't trust a green Lean checkmark as proof of correctness *of the statement* — the statement-to-informal mapping is the weak link (read the failure audit)
- Don't let a module header claim a flaw is "fixed" or a parameter is "load-bearing" when the body still leaves it unused — v3 did exactly this (headers ahead of bodies). The header is not evidence; the lethality scan + validation suite are. Verify the body, then update the header.
- Don't declare a statement a "Gate-1 frozen anchor" while the definitions it references are unvalidated — freeze is dependency-ordered (typed → validated → frozen; see `docs/VALIDATION_SUITE.md`). A `sorry` is only "honest" over validated definitions; three of the first seven sat on false statements.
- Don't cite upstream P/NP numbers without checking `docs/UPSTREAM_TRACKING.md` — the computational model is contested and numbers don't transfer across models
- Don't commit machine-specific configuration (paths, SSH, local toolchain) — that belongs in `AGENTS_LOCAL.md`, which is gitignored

### GitHub token lifecycle (verified 2026-09-27, all surfaces)

`GITHUB_TOKEN` is short-lived and has no agent-side refresh step: the platform
re-injects the current value into each command whose text contains the literal
string `GITHUB_TOKEN`. A fresh value arrives by referencing it again in a new
command, not by retrying.

- Do not trust an early `export`: a later command that names `GITHUB_TOKEN` gets
  the platform's current value and overwrites whatever the shell held.
- A long-running process (server, supervisor) captures the token at start. After
  a rotation it 401s on every call until restarted.
- `git push` with the token embedded in the `origin` URL is the same trap: after
  a rotation it prompts for a password and reads as a hang. Re-point the remote
  and use `GIT_TERMINAL_PROMPT=0`.

401 bodies: `Bad credentials` = rotated (transient - reference `$GITHUB_TOKEN`
again in a new command); `Requires authentication` = no token sent; `Resource not
accessible by integration` = App permission gap (permanent, stop).

`gh` prefers `GH_TOKEN` over `GITHUB_TOKEN`. Do not `unset` it; pin it so `gh`
cannot fall back to a stale or absent one:

```bash
export GH_TOKEN=$GITHUB_TOKEN && gh api user -q .login
```

Full mechanism and evidence: `portfolio-ops/ACCESS_AND_IDENTITIES.md`.
