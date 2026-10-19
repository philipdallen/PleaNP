# Implementation plan: Natural Proofs (Rung 3b) — pass decomposition (#201)

**Status:** working implementation plan for the Rung 3b natural-proofs module.
Written 2026-10-19 (run=20261019-0441-3ynu) during the #201 claim. **NOT a
frozen proof spec and NOT a proof** — a pass decomposition that seeds the
proof work, one pass per agent run, so the multi-run epic is worked as
successive one-run passes rather than one oversized claim (per
`docs/MULTI_AGENT_WORKFLOW.md` §Task definition, the multi-run pass rule).

**Companion docs:** `docs/STATEMENTS/NaturalProofs.md` (the frozen informal
statement — the Gate 1 anchor); `docs/STATEMENTS/NaturalProofs.proof-strategy.md`
(the informal reduction, §2/§3); `docs/STATEMENTS/NaturalProofs.design.md`
(the #67 N1–N6 decomposition this plan executes);
`docs/STATEMENTS/ComparatorChallenge.template.md` (DEC-022 challenge module);
`docs/STATEMENTS/LOCAL_AGENT_WORKFLOW.md` (the render/freeze/prove loop);
`docs/STATEMENTS/ProofIntuition.template.md` (DEC-023 human-legibility record).

---

## 1. What is already in place (verified at plan time, 2026-10-19)

The #67 design note was written 2026-09-13 and its central premise has since
decayed — the circuit substrate it called "the single hard prerequisite" is
**built and landed**. The plan below starts from what actually exists on
`main`, not from the design's "what is missing" list.

- **Circuit substrate — LANDED (#71, closed).** `lean/PleaNP/Circuits/Basic.lean`
  ships `BoolGate` with structural `size`/`depth`, `CircuitFamily`,
  `CircuitFamily.sizeOf`, and the natural-property vocabulary the barrier
  needs: `BoolFunc n := Fin n → Bool` (the `F_n` carrier), `IsPPoly`
  (polynomial-size family predicate), `PropertyFamily`, `Largeness`,
  `Constructive`, and `NaturalProperty := Constructive ∧ Largeness`.
  `lean/PleaNP/Circuits/MustRefute.lean` proves the substrate non-vacuous
  (`empty_not_natural`, `boolfunc_card`). The `P/poly` redefinition trap
  (Gate 2) is already closed by reuse of these names.
- **Circuit semantics — LANDED.** `lean/PleaNP/Circuits/AC0.lean` ships
  `BoolGate.eval` (the bridge from a gate term to the Boolean function it
  computes) and `ComputesParity`. The usefulness predicate keys off `eval`.
- **Statement frozen (informal).** `docs/STATEMENTS/NaturalProofs.md` §1: the
  *conditional* theorem — under an OWF/PRFF hypothesis, no `P`-natural
  property (constructivity + largeness) is useful against `P/poly` for
  superpolynomial circuit-size lower bounds. Scope pins: `P`-natural
  (`poly(2^n)`-time constructivity), largeness density `1/2^n`, hardness
  parameter explicit (`2^{n^ε}`, `ε > 0`), namespace
  `PleaNP.Barriers.NaturalProofs`.
- **Strategy written.** `docs/STATEMENTS/NaturalProofs.proof-strategy.md` §3:
  natural property → distinguisher → contradiction with PRFF pseudorandomness.
  All three conditions are load-bearing.
- **No Lean module yet.** `lean/PleaNP/Barriers/NaturalProofs.lean` does not
  exist; `lean/PleaNP/Barriers/Basic.lean` lists it as a planned stub.

**What is genuinely still open** (carried from `NaturalProofs.md` §7, resolved
inside the passes below rather than hand-waved):

1. the exact hardness parameter `ε` and the "hardness" form (distinguishing
   advantage);
2. the OWF/PRFF object as a **hypothesis** type — never a `theorem`/`axiom`
   (the Gate 5 trap, `NaturalProofs.md` §4);
3. the usefulness predicate against `P/poly` (the third condition, not part of
   the landed `NaturalProperty`, which encodes only constructivity + largeness).

---

## 2. The first Lean target file and the module layout

**First Lean target file:** `lean/PleaNP/Barriers/NaturalProofs.lean` (the
statement/claim root — rendered proof-free, the Gate-1 freeze anchor).

**Module layout** (DEC-022 §3.3 file-layout discipline, mirroring
`Relativization`):

| File | Role | Written by |
|---|---|---|
| `lean/PleaNP/Barriers/NaturalProofs.lean` | statement root: OWF/PRFF hypothesis type, usefulness predicate, the main conditional theorem (honest tracked `sorry` placeholders) | Passes 1–2, then frozen |
| `lean/PleaNP/Barriers/NaturalProofsProof.lean` (to be created) | proof-only module: distinguisher, correctness, assembly. **Must not import the challenge** and the statement root must not import it | Passes 4–6 |
| `lean/PleaNP/Challenges/NaturalProofs.lean` | Comparator reference statement (definitions + theorem types only, no proofs), authored from `NaturalProofs.md` before proof work attaches | Pass 3 |
| `lean/ComparatorChallenges/NaturalProofs.json` | Comparator JSON pin (theorem names + `permitted_axioms`) | Pass 3 |

`NaturalProofs.lean` is added to the CI named build list
(`.github/workflows/ci.yml`, the `lake build …` step) and to the hygiene /
vacuity / model-consistency step lists when it compiles, exactly as the other
`Barriers/*.lean` modules are listed.

---

## 3. The pass decomposition (Pass 1 → Pass 7)

**Passes:** (Pass 1..Pass 7; each is one claimable unit, worked in order)

Each pass is one claimable unit sized to one agent run (≈20 minutes of work),
worked in dependency order. A pass that overruns during its claim is **split
further** (per `docs/MULTI_AGENT_WORKFLOW.md` §Task definition) — it is never
carried as a second checkpoint on the same pass.

### Pass 1 — OWF/PRFF hypothesis module (scaffold + hypothesis type)

**End state:** `lean/PleaNP/Barriers/NaturalProofs.lean` exists with the
`PleaNP.Barriers.NaturalProofs` namespace and the crypto primitive as an
**assumed type**: a seeded function family `f_s : BoolFunc n` and a
`PRFFHyp` structure carrying (i) the seed/index and (ii) the **explicit**
hardness parameter `ε > 0` with the distinguishing-advantage predicate
(`DistAdvantage A f_s ≤ 2^{-(n^ε)}` form). It is a `structure`/`variable`/
`hypothesis`, never a `theorem` and never a custom `axiom` (`NaturalProofs.md`
§4, the Gate 5 trap). No proof body — honest `:= by sorry` placeholders at most.

**Done-evidence:**
- `lake build PleaNP.Barriers.NaturalProofs` (from `lean/`) compiles.
- `python3 tooling/gates/hygiene_scan.py lean/PleaNP/Barriers/NaturalProofs.lean`
  (render stage) — clean: no custom `axiom`, only the honest proof placeholder.
- `python3 tooling/gates/model_consistency_scan.py lean/PleaNP/Barriers/NaturalProofs.lean`
  — clean (no local redefinition of complexity-class names).
- If a `sorry` lands, a matching row in `docs/SORRY_TRACKER.md`
  (`python3 tooling/gates/sorry_tracker_scan.py` clean).

### Pass 2 — usefulness predicate + the frozen main statement

**End state:** the statement root gains (i) the usefulness predicate against
`P/poly` — a property family `C` is useful iff any `{f_n}` with `f_n ∈ C_n`
infinitely often is not computed by any `IsPPoly` family (reusing
`IsPPoly` + `BoolGate.eval` from the landed substrate, no local `P/poly`
redefinition) — and (ii) the **frozen main conditional theorem**
`PRFFHyp → ¬ ∃ C, NaturalProperty C ∧ UsefulAgainstPpoly C`. The statement
type-checks; the proof is the honest placeholder. The statement is then
**frozen** (Gate 1) and read back (Gate 4).

**Done-evidence:**
- `lake build PleaNP.Barriers.NaturalProofs` compiles.
- `python3 tooling/gates/statement_lint.py PleaNP.Barriers.NaturalProofs <MainTheorem>`
  (from `lean/`) — quantifier order / connective skeleton / negation head
  recorded.
- `python3 ../tooling/gates/lean_readback.py "PleaNP.Barriers.NaturalProofs.<MainTheorem>" "PleaNP.Barriers.NaturalProofs"`
  — read-back sentence matches `NaturalProofs.md` §5, with none of its
  "dropping X is a fail" omissions.
- `python3 tooling/gates/vacuity_scan.py lean/PleaNP/Barriers/NaturalProofs.lean`
  — clean (no `: True := by trivial` / `↔ True` shape).

### Pass 3 — Comparator challenge module + JSON pin (DEC-022)

**End state:** `lean/PleaNP/Challenges/NaturalProofs.lean` (definitions +
theorem *types* only, docstring citing `NaturalProofs.md` and Razborov–Rudich
1997) and `lean/ComparatorChallenges/NaturalProofs.json` (theorem names +
`permitted_axioms` = `propext`, `Quot.sound`, `Classical.choice`). Authored
from the frozen informal anchor **before any proof work attaches** (per
`ComparatorChallenge.template.md` §0 independence rule). The proof root does
not import the challenge and the challenge does not import the proof root.

**Done-evidence:**
- `lake build PleaNP.Challenges.NaturalProofs` compiles.
- `python3 tooling/gates/hygiene_scan.py lean/PleaNP/Challenges/NaturalProofs.lean`
  — clean (statement-reference module, no proof).
- Independence: `grep` shows neither module imports the other.
- The JSON parses and its `permitted_axioms` match `axiom_check.py`'s allowance;
  a `formalization.yaml` `comparator_config` row is added in the same commit.

### Pass 4 — distinguisher construction (the crux, part 1)

**End state:** `lean/PleaNP/Barriers/NaturalProofsProof.lean` (to be created)
defines the distinguisher `D`: given oracle access to a function `g`, query
`g` on all `2^n` inputs to obtain its truth table, run `C_n`'s decider (via the
landed `Constructive` predicate), and output "random" iff `g ∈ C_n`, else
"pseudorandom" (`NaturalProofs.proof-strategy.md` §3 step 2).

**Done-evidence:**
- `lake build PleaNP.Barriers.NaturalProofsProof` compiles.
- `python3 tooling/gates/hygiene_scan.py lean/PleaNP/Barriers/NaturalProofsProof.lean`
  — clean.
- The distinguisher's type is rendered and recorded (the query-all-inputs
  shape is the constructivity-to-test bridge).

### Pass 5 — distinguisher correctness + the three condition-lemmas

**End state:** the correctness lemma `∀ g, (g ∈ C_n) ↔ D g = random` plus the
two advantage facts that make `D` a distinguisher: **largeness** gives
`Pr[D(R) = random]` non-negligible (random functions pass), and **usefulness**
plus the small-circuitness of `f_s` gives `D(f_s) = pseudorandom` always
(pseudorandom functions fail). All three conditions are load-bearing
(`NaturalProofs.proof-strategy.md` §3.3).

**Done-evidence:**
- `lake build PleaNP.Barriers.NaturalProofsProof` compiles with the
  correctness and advantage lemmas proved (zero `sorry` in the new lemmas).
- `python3 tooling/gates/binder_usage_scan.py lean/PleaNP/Barriers/NaturalProofsProof.lean`
  — every binder load-bearing.

### Pass 6 — contradiction / assembly → main theorem proved

**End state:** the reduction assembled — `D` distinguishes `f_s` from a truly
random function with non-negligible advantage, contradicting `PRFFHyp`, giving
the main conditional theorem
`PRFFHyp → ¬ ∃ C, NaturalProperty C ∧ UsefulAgainstPpoly C`, **zero `sorry`**.
The statement root's placeholder is discharged by the proof module; the
`docs/SORRY_TRACKER.md` row is resolved.

**Done-evidence:**
- `lake build PleaNP.Barriers.NaturalProofs PleaNP.Barriers.NaturalProofsProof`
  compiles zero-`sorry`.
- `python3 ../tooling/gates/axiom_check.py PleaNP.Barriers.NaturalProofs,PleaNP.Barriers.NaturalProofsProof PleaNP.Barriers.NaturalProofs.<MainTheorem>`
  (from `lean/`) — axiom fingerprint within {propext, Quot.sound,
  Classical.choice}; no `sorryAx`.
- `python3 tooling/gates/hygiene_scan.py --prove-stage lean/PleaNP/Barriers/NaturalProofs.lean lean/PleaNP/Barriers/NaturalProofsProof.lean`
  — clean (proof-stage: any `sorry` is a violation).
- `python3 tooling/gates/sorry_tracker_scan.py` — clean.

### Pass 7 — final gates, read-back, human-legibility record, closeout

**End state:** the full gate set passes on both modules; a `ProofIntuition`
record per DEC-023 is added (`docs/STATEMENTS/NaturalProofs.intuition.md` (to be created) —
5-layer plain-words construction + load-bearing audit + perturbation tests);
`formalization.yaml` rows are updated for the frozen declaration; the module is
added to the CI build/gate lists; the `#201` lineage closes.

**Done-evidence:**
- `python3 tooling/gates/vacuity_scan.py lean/PleaNP/Barriers/NaturalProofs.lean lean/PleaNP/Barriers/NaturalProofsProof.lean`
  — clean.
- `python3 tooling/gates/model_consistency_scan.py …` and
  `python3 tooling/gates/binder_usage_scan.py …` — clean.
- `python3 tooling/gates/dual_render.py --check …` — the two independent
  renderings agree (Gate 3).
- `python3 tooling/gates/lean_readback.py …` — read-back matches
  `NaturalProofs.md` §5 (Gate 4).
- `python3 tooling/gates/docs_links_scan.py` and
  `python3 tooling/gates/unicode_scan.py .` — clean.
- CI green on the widened `lake build` list.

---

## 4. Sizing (`Effort:` line) and the #67 mapping

**Effort:** 7 runs.

The max (7) equals the number of enumerated `Pass N` lines above, per the
`tooling/gates/pass_scan.py` rule (`docs/MULTI_AGENT_WORKFLOW.md` §Task
definition rule 1: fix the Effort line, not the pass list, when they disagree).
The block is written so it can be pasted into the issue body unchanged if the
issue is later made multi-pass.

**Mapping to the #67 design's N1–N6** (`NaturalProofs.design.md` §3.1):

| Plan pass | #67 item | Note |
|---|---|---|
| — | N1 (circuit substrate decision) | **RESOLVED** — `PleaNP.Circuits` landed (#71); no pass needed |
| Pass 1 | N3 (OWF/PRFF hypothesis) | the design's lowest-risk first step |
| Pass 2 | N2 (natural property / usefulness) | reuses landed `NaturalProperty`; adds usefulness |
| Pass 3 | N6 (comparator half) | pulled earlier: the challenge is authored before proof attaches |
| Pass 4 | N4 (distinguisher, part 1) | N4 is the "Hard" crux, split into two passes |
| Pass 5 | N4 (distinguisher, part 2) | correctness + the three condition-lemmas |
| Pass 6 | N5 (contradiction / assembly) | main theorem proved zero-`sorry` |
| Pass 7 | N6 (gates + read-back + layout) | + the DEC-023 intuition record |

---

## 5. Lifecycle and gate discipline (binding on every pass)

Per `docs/MULTI_AGENT_WORKFLOW.md` §Proof / claim lifecycle and
`docs/STATEMENTS/LOCAL_AGENT_WORKFLOW.md`, the statement freeze precedes proof
search:

- **Passes 1–2 render the statement** (Gate 1). The statement root stays
  proof-free; the proof module (Passes 4–6) must not edit it. A statement
  change requires a new `NaturalProofs.md` revision and re-running
  `LOCAL_AGENT_WORKFLOW.md` Steps 1–4.
- **Pass 3 authors the independent reference** before any proof attaches
  (Comparator template §0).
- **Gates 1–6 pass before Gate 7 (proof search)** begins in Pass 4.
- **One claim = one pass.** The claim comment names the pass
  (`claiming Pass N of #201`); a pass-complete commit closes only that pass,
  and the issue stays open until Pass 7 reports the full gate evidence.

---

## 6. Open decisions this plan carries forward (not silently resolved)

These are the `NaturalProofs.md` §7 items; each is a Lean-author decision
landed inside the named pass, not an ambiguity the plan papers over:

1. **The hardness parameter `ε`** and the distinguishing-advantage form — Pass 1.
2. **`P/poly` rendering** — resolved by reuse: `PleaNP.Circuits.IsPPoly`
   (nonuniform polynomial-size family); no local redefinition (Gate 2).
3. **Constructivity class** — v1 pins `P`-natural (`poly(2^n)`-time);
   the landed `Constructive` records the decision-function shape, and the
   machine-substrate refinement is a follow-up if the read-back requires it.
4. **Largeness density** — v1 pins the original `1/2^n`; the landed
   `Largeness` already encodes this (`2^n · |C_n| ≥ |F_n|`).

---

## 7. What this plan does not do

- It does not write Lean (planning only, per #201's DoD).
- It does not choose the constructivity-class machine substrate (a v2 /
  follow-up decision; the v1 shape is the landed `Constructive`).
- It does not build a PRF — the OWF/PRFF stays a hypothesis
  (`docs/ROADMAP.md` Rung 3b; `docs/PRIOR_ART.md` crypto-substrate section).

---

_Last updated: 2026-10-19 (issue #201, implementation plan). This plan is the
#201 deliverable; the `Pass 1 → Pass 7` block is recorded in the #201 issue
body so the epic is worked one pass per claim, per
`docs/MULTI_AGENT_WORKFLOW.md` §Task definition._
