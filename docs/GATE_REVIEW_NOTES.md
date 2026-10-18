# Gate REVIEW notes — clean modules (issue #56)

> **Purpose.** A resolution record for the non-zero `REVIEW` items the
> Tier-1 gate scanners surface on the repo's "clean" modules
> (`Oracle.lean`, `OracleComplexity.lean`, `OracleSmoke.lean`,
> `BarrierVerdictB.lean`). Each item below was verified against the
> repo tree; the disposition is **no-action** (option (c) of issue #56):
> the clean modules stay clean, the scans exit 0, and the REVIEW items
> are demonstrated-intentional. Future scanners/auditors read this
> file instead of re-flagging the same items blind. The GitHub issue
> queue + `git log origin/dev` remain the system of record.
>
> **Sweep lineage:** filed by audit sweep run=20260911-1125-p4np,
> resolved by run=20260913-0942-d946 (issue #56).

## 1. Gate 6 (Tier 1) hygiene REVIEWs — `OracleSmoke.lean` `by decide`

`hygiene_scan.py --prove-stage` reports three `by decide` smells inside
the smoke test's proof bodies:

- `OracleSmoke.lean:92` — `⟨⟨⟨2, rfl⟩, by decide⟩⟩` (accept run: the
  `2`-step bound / timeout comparison)
- `OracleSmoke.lean:109` — `steps_le_m := by decide` (reject run:
  same timeout comparison)
- `OracleSmoke.lean:119` — `exact absurd hOutput (by decide)` (reject
  run: `[true] ≠ [false]` over a concrete two-element Bool stack)

**Verification.** All three are discharges of concrete finiteness /
arithmetic obligations on literal data (`2 ≤ 2`, `[true] ≠ [false]`).
They appear *inside proofs*, not as statement placeholders. The module
documentation (`OracleSmoke.lean` header, "Oracle-sensitivity smoke
test") states the intended check strength explicitly: the accept
direction is closed by evaluation (`rfl`) and the reject direction uses
determinism (`evalsTo_unique_result`) plus evaluation — "the strongest
check short of `decide` over the existential (Cfg contains function
fields, so the ∃ is not decidable)". The oracle-sensitivity claim is
carried by the reachability/acceptance structure, not by the `by
decide`s.

**Disposition.** No-action, demonstrated-intentional. Treated as extra
gate evidence per the scanner's REVIEW contract; no code change.

## 2. Gate 5 (Tier 1b) binder REVIEW — `abstractPVsNP_iff_verdictB` "unreferenced"

`binder_usage_scan.py` flags
`BarrierVerdictB.lean:46` (`theorem abstractPVsNP_iff_verdictB`) as
"referenced by no other scanned declaration". The scanner walks only
the *Lean* declarations in the scanned path set; it does not see the
corpus/churn provenance.

**Verification.** The lemma is the Gate-7 equivalence proof consumed by
the barrier-verdict corpus map:

- `churn/barrier-verdict/matrix.json:8` — `"Equivalent by proved lemma PleaNP.Calculus.abstractPVsNP_iff_verdictB."`
- `churn/barrier-verdict/lemmas.json:2` — `"A|B": "PleaNP.Calculus.abstractPVsNP_iff_verdictB"`

**Disposition.** No-action. The churn matrices are the legit external
reference; the scanner's "unreferenced" is a false dead-code verdict
limited to its scan set.

## 3. Gate 5 (Tier 1b) binder REVIEW — `emptyOracle` "unreferenced"

`binder_usage_scan.py` flags `Oracle.lean:172`
(`def emptyOracle (Q : Type) : Oracle Q := fun _ => false`) as
"referenced by no other scanned declaration". The scanned clean set
(`Oracle.lean`, `OracleComplexity.lean`, `OracleSmoke.lean`,
`Calculus/*`) does not include the module that uses it.

**Verification.** The `P^∅ = P` upstream anchor uses it directly:
`OracleUpstreamP.lean:28` —
`P_A (alpha := alpha) (emptyOracle Q) = { L | sorry }`.
`OracleUpstreamP.lean` is intentionally outside the clean scan set (it
carries the tracked `sorry`s per `docs/SORRY_TRACKER.md`; it is
isolated so `warningAsError` does not cascade).

**Disposition.** No-action. The upstream-anchor module is the legit
reference; the declaration is load-bearing.

## 4. Gate 5 (Tier 1b) binder REVIEW — weakly-constrained witness in `NP_A` (`∃ y`)

`binder_usage_scan.py` flags `OracleComplexity.lean:63` — inside `NP_A`,
the conjunct `M.oracle = hΓ.symm ▸ A` does not mention the existential
witness `y`.

**Verification.** This is correct and intended. In `NP_A`'s membership
body (`OracleComplexity.lean:57-71`), the certificate `y` is load-bearing
through the *next* conjunct, `@AcceptsInTime tm' (alpha × List alpha) h
ea oa M (x, y) (fun n => p.eval n)` — the oracle machine accepts the
pair `(x, y)`. The conjunct that the scanner top-level-splits on is
an `M`-side oracle-wiring statement; the witness appears in the second
conjunct. The scanner only conjunct-splits the top level, so this is a
false positive shape.

**Disposition.** No-action, verified-intentional. The certificate `y`
is load-bearing via `AcceptsInTime M (x, y)`; the docstring above
`NP_A` records this (Flaw C fix carried from the v4 repair).

## 5. Gate 5 (Tier 1b) binder REVIEW — `P_A_subset_NP_A` "unreferenced" (RESOLVED)

`binder_usage_scan.py` previously flagged `OracleComplexity.lean`
(`theorem P_A_subset_NP_A`) as "referenced by no other scanned
declaration" — the scanner sees only Lean declarations, not CI/tooling
name references. **Resolved 2026-09-13 (issue #63 Pass 3):** the new
`RelativizationProof.P_subset_NP_console` theorem *instantiates*
`P_A_subset_NP_A`, so the binder scanner no longer flags it; it is
removed from the register EXPECTED set.

**Historical verification** (why it was noted before resolution). The
theorem was referenced by name from CI and tooling:

- `.github/workflows/ci.yml` — the Gate 6 Tier 2 `axiom_check.py` step
  checks the clean-module theorems (including `P_A_subset_NP_A`) for
  `sorryAx`/non-standard axioms
- `tooling/gates/axiom_check.py` — the checked-theorem list
- `tooling/galaxy/tests/test_galaxy_render.py` — statement-manifest
  render tests
- `lean/PleaNP/Barriers/BoundaryProbe.lean` — in-module consumer

**Disposition.** No-action. CI/tooling name references are the legit
external reference; it is structurally load-bearing (the `P_A ⊆ NP_A`
self-check).

---

## Register (for future scan runs)

| Scanner | Review item | Location | Legit reference / disposition |
|---|---|---|---|
| hygiene (`--prove-stage`) | `by decide` smell ×3 | `OracleSmoke.lean:92,109,119` | Proof-body finiteness discharges, documented in module header; no-action |
| binder | `abstractPVsNP_iff_verdictB` unreferenced | `BarrierVerdictB.lean:46` | `churn/barrier-verdict/matrix.json` + `lemmas.json`; no-action |
| binder | weak witness `∃ y` | `OracleComplexity.lean:69` | `AcceptsInTime M (x, y)` next conjunct; no-action |
| binder | `P_A_subset_NP_A` unreferenced | `OracleComplexity.lean:86` | RESOLVED (#63 Pass 3): referenced by `P_subset_NP_console`; dropped from register |
| binder | `UpstreamPolyTime` unreferenced | `OracleComplexity.lean:40` | `P^∅ = P` compatibility anchor RHS (function→language bridge, OracleTM2Recompose Trap 1; #4/#40 upstream-P work); no-action |
| binder | `equalizing_oracle_statement` / `separating_oracle_statement` (challenge) unreferenced | `Challenges/Relativization.lean` | statement references consumed by comparator JSON pin `lean/ComparatorChallenges/Relativization.json` (proof-root `theorem_names`); no-action |
| binder | `uniform_collapse_contradicted_by_separating` / `uniform_separation_contradicted_by_equalizing` / `no_uniform_resolution_of_p_vs_np` unreferenced | `Barriers/RelativizationProof.lean` | DEC-022 §3.3 proof-work lemmas (issue #66): the BGS barrier-consequence corollaries, consumed onward by #37/#63 assembly — not dead code; no-action |
| binder | `algebrizing_separation_statement` / `algebrizing_equalization_statement` unreferenced | `Barriers/Algebrization.lean` | AW09 v1 statement references (issue #69 Pass 1): consumed by AZ5's proof assembly — not dead code; no-action |
| binder | `size_pos` / `depth_size_le` / `CircuitFamily.depthOf` / `univ_largeness` unreferenced | `Circuits/Basic.lean` | Rung-4 circuit substrate API (issues #71 Pass 1-2): the typed circuit-family + P/poly + natural-property foundation consumed by Rung-4 lower bounds — not dead code; no-action |
| binder | `IsPPoly` **RESOLVED (2026-09-13, #88 Pass 1)** | `Circuits/Basic.lean` | now referenced by `Williams.IsACC0` — no longer flagged |
| binder | `williams_classification_asserted` unreferenced | `Barriers/WilliamsTransfer.lean` | Williams transfer classification record (issue #90 Pass 3): consumed by #91 assembly — not dead code; no-action. `williams_transfer` is no longer flagged (#90 Pass 3's `#barrier_check williams_transfer` references it). |

| binder | `williams_transfer` / `williams_classification_asserted` unreferenced | `Barriers/WilliamsTransfer.lean` | Williams transfer theorem statement + classification record (issue #90 Pass 3): consumed by #91 assembly — not dead code; no-action |
| binder | `assembled_williams_transfer` / `assembled_classification` unreferenced | `Barriers/WilliamsAssembly.lean` | Williams transfer assembly (issue #91 Pass 4)
| binder | `IsACC0` / `NEXP_membership` **RESOLVED (2026-09-13, #90 Pass 3)** | `Barriers/Williams.lean` | now referenced by `WilliamsTransfer.NEXP_not_subset_ACC0` — no longer flagged |
| binder | `monotone_eval_preserves_order` / `MonotoneFamily.sizeOf` / `monAnd2` unreferenced | `Circuits/Monotone.lean` | Monotone-circuit model (issue #74 Pass 1): the monotone gate basis + monotonicity theorem, consumed by Pass 2/3 (Razborov CLIQUE) + the #73 monotone classification — not dead code; no-action |
| binder | `eval` / `depth` / `size_pos` (Monotone) **RESOLVED (2026-09-13, #74 Pass 1)** | `Circuits/Monotone.lean` | referenced in-module (monotonicity theorem, size examples) in the full scan set — no longer flagged |
| binder | `NaturalProperty` **RESOLVED (2026-09-13, #71 Pass 3)** | `Circuits/Basic.lean` | now referenced by `Circuits/MustRefute.lean`'s `empty_not_natural` — no longer flagged |
| binder | `a` weak witness (leaf-generalized depth ladder) | `Circuits/AC0.lean` (`depth1_shapes_input` / `depth_le_one_shapes`) | Issue #157: the shape statements use single-binder `∃ a, IsLeaf a ∧ (c = …)` ∨-disjuncts; the scanner over-splits the ∨-separated conjunct list and reports a `b`-conjunct as free of the `a` witness. False positive — same shape as the MonotoneApprox `a`/`b` items; no-action |
| binder | `and2` **RESOLVED (2026-09-13, #72 Pass 1)** | `Circuits/Basic.lean` | now referenced by `Circuits/AC0.lean`'s eval sanity examples — no longer flagged |
| hygiene | `by decide` (1) | `Circuits/Basic.lean` | `Nat.one_le_pow` discharge in `univ_largeness` — same proof-body finiteness category as the OracleSmoke smells; no-action |
| binder | `BoolFunc` / `CircuitFamily.sizeOf` **RESOLVED (2026-09-13, #71 Pass 2)** | `Circuits/Basic.lean` | now referenced by the Pass-2 defs (`Largeness`, `IsPPoly`) — no longer flagged |
| binder | `consoleOracleHead_computable` unreferenced | `Barriers/RelativizationProof.lean` | Clause-(a) A2 console-oracle leading-bit instance (issue #63 Pass 1, sibling): public proof-work API consumed by A3/A5 — not dead code; no-action |
| hygiene (`--prove-stage`) | `by decide` smell ×3 | `OracleV5Tests.lean:138,155,165` | Same proof-body finiteness discharges as the OracleSmoke items (v5 word-query smoke accept/reject theorems + 2-step bound); no-action |
| binder | `UpstreamPolyTime` unreferenced | `OracleComplexity.lean:40` | Consumed by `OracleUpstreamP.lean` (the P^∅ = P anchor, outside the clean scan set); no-action |
| binder | `atomEqOrNe` unreferenced | `MarkerFuneqAtom.lean:117` | Campaign rendering target — registered in `churn/marker-funeq/renderings/atom.json` (multi_render slot 1) and checked by `dual_render`/`multi_render check`; the scanner sees only Lean declarations, not the campaign workspace; no-action (issue #41) |
| binder | `pointwiseEqOrNe` unreferenced | `MarkerFuneqPointwise.lean:126` | Campaign rendering target — registered in `churn/marker-funeq/renderings/pw.json` (multi_render slot 2) and checked by `dual_render`/`multi_render check`; the scanner sees only Lean declarations, not the campaign workspace; no-action (issue #41) |

**Register changes (2026-09-13, #40):** `emptyOracle` is **no longer
flagged** — the word-query test module (`OracleV5Tests.lean`)
references it (`v5M (emptyOracle V5Query)`), so the binder scanner's
"unreferenced" REVIEW resolved itself. `OracleV5Tests.lean` contributes
3 new hygiene REVIEWs (registered above). The `y`/`P_A_subset_NP_A`
line numbers shifted (v5 substrate #35 rewired `OracleComplexity.lean`).

Expected scan result on the clean set: **0 violations, 8 binder REVIEW
items, 6 hygiene REVIEW items — all register entries above, all
demonstrated-intentional.** (The two challenge-module binder REVIEWs from
`PleaNP.Challenges.Relativization` for the DEC-022 comparator references
are registered in the row above; the challenge module is a statement
reference consumed by the JSON pin, not dead code.)
## 3. Rung-5 soundness + P^∅ anchor REVIEWs (issue #65 / #40)

**Sweep lineage:** run=20260913-1012-uJoS (issue #65), and #40 (v5-word-query tests).

### `OracleComplexity.lean` — `UpstreamPolyTime` "unreferenced"

`binder_usage_scan.py` flags `UpstreamPolyTime` (issue #40) as referenced by
no other scanned declaration. It IS the RHS of the P^∅ = P anchor theorem in
`OracleUpstreamP.lean` (`P_empty_eq_upstream_P_class = UpstreamPolyTime _`) —
which is outside the CI scan set (it is the upstream-P-blocked leaf module).
The oracle-free `TM2ComputableInPolyTime` recharacterization is the
model-consistency anchor (Trap 3); not dead code.

### `Soundness.lean` — the uniformity lemmas "unreferenced"

`binder_usage_scan.py` once flagged the library-level uniformity lemmas
(`relAtom_uniform`, `langAtom_uniform`, `pA_mem_uniform`, `uniform_and`, …
`uniform_exists`, `funeq_uniform`, `funne_uniform`, `transfer_under_ext`,
`sound_verdict_abstract_rev`) as referenced by no other scanned declaration.
They are the **intentional public API** of the Rung-5 `#barrier_check`
soundness module (`docs/STATEMENTS/Soundness.spec.md`, issue #65): each
`UniformInOracle` lemma is the semantic counterpart of one `Relativizing.*`
propagation instance, designed for downstream composition proofs (the class
transfer / BGS `False` once #18/#63 land). Same demonstrated-intentional
pattern as the `BarrierCalculus` propagation instances in §1 above. NOTE:
`pA_mem_uniform` is no longer flagged since #73 Pass 1's
`Classification.classification_uniform` references it.

**Disposition.** No-action. The register (`tooling/gates/gate_review_register_check.py`
EXPECTED) is updated to include these items so the machine-check agrees.

### `MarkerFuneqAtom.lean` / `MarkerFuneqPointwise.lean` — the campaign rendering targets (issue #41)

`binder_usage_scan.py` flags `atomEqOrNe` / `pointwiseEqOrNe` as referenced
by no other scanned declaration. They are the two-candidate **rendering
targets** of the marker-funeq campaign (issue #41): each is registered in
`churn/marker-funeq/renderings/*.json` (multi_render slots) and machine
checked by `dual_render`/`multi_render check` (the campaign reported the two
readings DISAGREE — the intended semantic divergence). The scanner sees only
Lean declarations, not the campaign workspace. Not dead code.

**Disposition.** No-action. The register EXPECTED set is updated to include
these items so the machine-check agrees.

**Register changes (2026-09-13):** the two marker-funeq campaign rendering
targets (`atomEqOrNe` / `pointwiseEqOrNe`) join the register (issue #41);
`UpstreamPolyTime` is registered above (issue #65/#40, as-swept). Binder
REVIEW count on the clean set is 8 (5 original + UpstreamPolyTime + the two
#41 rendering targets).
### `Closure.lean` — the Rung-7 Tier-1 benchmark membership theorems (issue #81)

`binder_usage_scan.py` flags `emptyLang_in_UpstreamPolyTime` /
`univLang_in_UpstreamPolyTime` as referenced by no other scanned declaration.
They are the **public API** of the Rung-7 Tier-1 baseline datapoint
(`lean/PleaNP/Benchmark/Closure.lean`, issue #81 Pass 2): the membership
facts recorded in `docs/BENCHMARK.md` (the baseline run table B1/B2) and
consumed by the benchmark/Rung-9 acceptance tracking. The scanner sees only
Lean declarations, not the benchmark docs.

**Disposition.** No-action. The register EXPECTED set is updated to include
these items so the machine-check agrees.

### `Resolution.lean` — the resolution substrate API (issue #75 Pass 1)

`binder_usage_scan.py` flags the substrate module's building blocks:
- `eval` — **referenced internally** (by `Clause.eval`) but the scanner
  resolves only top-level name references, so it still reports it as
  unreferenced; a genuine false positive. (`var` was in the same class but
  the rewritten `Clause.eval` exposes the reference, so it self-resolved.)
- `simp` — a `@[simp]`-attribute misread as an implicit binder on `not`.
- `Clause.empty`, `CNF.width`, `ResDerivation.width` — the public substrate
  measures. (`ResDerivation.size` self-resolved: the merged scan set now
  resolves it — no register entry needed.)
- `ResDerivation.sound` — the headline soundness theorem (resolution derives
  only entailed clauses).

All are demonstrated-intentional public API of the Rung-4 proof-complexity
substrate, consumed by #75 Pass 2 (the pigeonhole width lower bound) and
#73 (the barrier classification).

**Disposition.** No-action. The register EXPECTED set is updated to include
these items so the machine-check agrees.

## 3.5 AW09 AZ3 barrier-consequence lemmas (issue #69 Pass 2)

**Sweep lineage:** run=20260913-2040-6c3d (issue #69 Pass 2).

`binder_usage_scan.py` flags `no_algebrizing_uniform_resolution`
(`lean/PleaNP/Barriers/AlgebrizationProof.lean`) as referenced by no
other scanned declaration. It is the **intentional public API** of the
Algebrization proof-work module — the asymmetric-access counterpart of
`RelativizationProof.no_uniform_resolution_of_p_vs_np`: given the AW09
separating pair (NP^A ⊄ P^E) and equalizing pair (P^B = NP^E), neither
uniform direction of a P-vs-NP resolution survives the low-degree-
extension access model. Same demonstrated-intentional pattern as the
RelativizationProof barrier-consequence set.

**Disposition.** No-action. Registered in
`tooling/gates/gate_review_register_check.py` EXPECTED.

**Register-side effect.** Adding `AlgebrizationProof.lean` to the scan
set changed the cross-reference graph: the module genuinely references
the `Algebrization.lean` statement refs (`algebrizing_*_statement` — used
as hypothesis types) and the per-direction lemmas (`uniform_collapse_...`,
`uniform_separation_...` — the joint theorem's components), so the binder
scanner no longer flags them as unreferenced. Those EXPECTED entries were
removed accordingly; the remaining register matches the fired set.

### `AC0.lean` — the AC0 milestone public API (issue #72 Pass 1 + #73 Pass 2)

`binder_usage_scan.py` flags the AC0 milestone's public API:
- `parity_zero` / `parity_nontrivial` — the structural parity facts giving
  the statement content (parity is a genuine, non-constant family).
- `parity_notin_AC0_relativizing` — the #73 Pass 2 classification: the AC0
  lower-bound claim is oracle-uniform (relativizing) via the Rung-4 method.
- `depth_eq_zero_iff_input` — the #72 Pass 2 structural core: a depth-0
  circuit is exactly an input gate (the depth-ladder first rung); referenced
  by `not_computes_parity_depth1`, so it is no longer flagged.
- `not_computes_parity_depth1` — the #72 Pass 2 depth-1 exclusion: no
  length-2 depth-1 circuit computes parity (the depth-ladder second rung).
  NOT flagged: it uses `depth_eq_zero_iff_input` and closes each two-input
  shape by decide over the finite `Fin 2 -> Bool` space; and it is itself
  referenced by `not_computes_parity_depth_le_one`, so it no longer fires
  as an unreferenced decl either.
- `not_computes_parity_depth_le_one` — the #72 Pass 2 depth-≤1 extension
  (2026-09-22): the depth-1 exclusion extended down to depth 0, the form
  the switching-lemma induction consumes. Flagged as unreferenced public
  proof-work API (the pattern of the ladder rungs above); registered as
  demonstrated-intentional.
- `depth1_shapes_input` — the #72 Pass 1 structural core (2026-09-22): every
  depth-1 circuit is a single gate over input literals (the depth-ladder
  rung between `depth_eq_zero_iff_input` and the exclusion). NOT flagged: it
  is referenced by `depth_le_one_shapes`, so the scanner resolves it.
- `depth_le_one_shapes` — the #72 Pass 1 base case (2026-09-22): every
  depth-≤1 circuit is a gate over input literals, the depth-reduction base
  case. Flagged as unreferenced public proof-work API (the pattern of the
  ladder rungs above); registered as demonstrated-intentional.
- `parity_notin_AC0` itself is NOT flagged anymore — the classification
  theorem references it, so the scanner resolves it.

**Disposition.** No-action. The register EXPECTED set reflects the current
set (structural facts + the classification theorem).

### `MustRefute.lean` — the must-refute suite (issue #71 Pass 3)

`binder_usage_scan.py` flags the validation-suite public API:
- `univ_property_constructive` — the universal property is constructive
  (companion to `univ_largeness`; `Constructive` is inhabited).
- `empty_not_natural` — the empty property family is not a natural property.
- `boolfunc_card` — `|F_n| = 2^n`, the counting baseline.

All demonstrated-intentional, consumed by `docs/VALIDATION_SUITE.md` and the
Rung-4 lower-bound arguments. (`empty_not_largeness` is referenced by
`empty_not_natural`; the suite's unifying fact.)

**Disposition.** No-action. The register EXPECTED set is updated to include
these items so the machine-check agrees.

### WilliamsSat.lean — the CircuitSAT-decider milestone (issue #89 Pass 2)

`binder_usage_scan.py` flags the milestone's public API:
- `acc0SatBrute_correct` / `acc0SatSteps_eq` — the correctness and the
  verified `2^n` runtime baseline (the mechanism Pass 3 attaches).
- `acc0SatSubExpBound` — the tracked sub-exponential goal (a `def`, not a
  `sorry`; the ACC0-structure packing is the documented research gap).
- `sat_existing` — the satisfiable-`and2` smoke.
- hygiene `by decide` (1) — the `sat_existing` discharge, same proof-body
  finiteness category as the registered OracleSmoke smells.

All demonstrated-intentional, consumed by the Pass-3 transfer and the
Williams umbrella (#76/#90/#91).

**Disposition.** No-action. The register EXPECTED set is updated to include
these items so the machine-check agrees.

## 3.6 Monotone-circuit approximation reducer (issue #74 Pass 2)

**Sweep lineage:** run=20260913-2232-9297 (issue #74 Pass 2).

`binder_usage_scan.py` flags the structural API of
`lean/PleaNP/Circuits/MonotoneApprox.lean` (`sm_or_size_le`,
`sm_and_size_le`, `sm_or_mem`, `sm_and_mem`, `approximate_nonempty`,
`MonomialEval`, and the `m`/`a`/`b` weak-witness tokens) as referenced by
no other scanned declaration / weakly-constrained. They are the
**intentional public API** of the approximation-reducer milestone — the
sm-AND/sm-OR approximators (+ size bounds + membership identities) that
Pass 3's CLIQUE counting bound consumes. The `m`/`a`/`b` tokens are the
binder's notes on the honest `∀ i ∈ m, ...` and paired-`∃` statement
shapes (same register pattern as `y` in `OracleComplexity.lean`).

**Disposition.** No-action. Registered in
`tooling/gates/gate_review_register_check.py` EXPECTED. Adding the module
to the scan set resolved `Monotone.lean`'s `MonotoneFamily.sizeOf` (no
longer flagged), so that EXPECTED entry was removed.

**Update (2026-09-22, #74 Pass 3).** Pass 3 added `ApproxSet.truncate` /
`truncate_size_le` (the Razborov size-`r` closure) and the reducer-soundness
lemma `monomialEval_imp_eval` (with its `MonomialEval`-shaped restatement
`monomialEval_imp_eval'`). Two changes to this section's register:

- `truncate_size_le` and `monomialEval_imp_eval` are **new** unreferenced
  public API awaiting Pass-3's counting bound — added to EXPECTED.
- `sm_or_mem`, `sm_and_mem`, and `MonomialEval` are **no longer flagged** —
  `monomialEval_imp_eval` now references all three (it recurses through the
  membership identities and uses `of_decide_eq_true` on `MonomialEval`), so
  the scanner resolves them. Those three EXPECTED entries were removed, the
  same way #157's depth ladder resolved `depth_eq_zero_iff_input`.

**Update (2026-09-22, #74 Pass 3 item 1 — completeness).** The completeness
half of approximation-correctness landed:
`eval_imp_monomialEval` (`g = true` on an assignment forces a produced
monomial to be satisfied there) and its packaged exactness form
`eval_iff_exists_monomial` (the approximation's 1-set **is** the gate's
1-set, the property the counting bound consumes). One register change:

- `eval_iff_exists_monomial` is **new** unreferenced public API awaiting
  Pass-3's counting bound — added to EXPECTED.
- `eval_imp_monomialEval` is **not** flagged — it is referenced by
  `eval_iff_exists_monomial` (the exactness packaging), so the scanner
  resolves it. `monomialEval_imp_eval` stays registered because its
  `MonomialEval`-shaped restatement `monomialEval_imp_eval'` is not yet
  referenced by any scanned declaration.

**Update (2026-09-22, #74 Pass 3 item 2 — counting bound).** The Razborov
counting bound landed:

- `truncate_subset_powersetCard_biUnion` — the truncated carrier is a
  subfamily of the `≤ r`-subset layers of `Fin n`.
- `truncate_card_le_sum_choose` — `|truncate r A| ≤ ∑_{k ≤ r} C(n,k)`, the
  bound that depends on `n` and `r` alone, not on the circuit. The
  scanner's `unreferenced_decl` note is a false dead-code verdict: the
  lemma is the counting bound the CLIQUE pigeonhole instantiation consumes
  (Pass 3 item 3 / the Rung-4 assembly), the same disposition as its
  sibling `truncate_size_le`.

`truncate_subset_powersetCard_biUnion` is **not** flagged — it is
referenced by `truncate_card_le_sum_choose`'s proof. `truncate_card_le_sum_choose`
is added to EXPECTED in `gate_review_register_check.py`.

## 4. BGS clause-(a) A2/A3 console-oracle API (issue #63)

**Sweep lineage:** run=20260913-1020-GY2l (issue #63).

`binder_usage_scan.py` flags `consoleOracleHead_computable`,
`consoleLang_mem_P` (and the §3.3 barrier-consequence lemmas, already
registered) as referenced by no other scanned declaration.

> **#121 update (2026-09-17).** Issue #121 generalised the A3 membership from
> the two constant oracles to **every** oracle: `consoleLang_mem_P (A)` proves
> `consoleLang A ∈ P_A A`, with `consoleRun_halts (A)` generalising the two
> constant-oracle run lemmas. The `#check` reference lines that used to sit
> after `consoleLang_mem_P_false` now sit in the general theorem's block, so
> the register's flagged API name moves from `consoleLang_mem_P_false` to
> `consoleLang_mem_P` (same intentional-public-API disposition; the constant
> theorems remain as the `A := fun _ => true/false` instances). They are the
**intentional public API** of the BGS clause-(a) proof-work module
(`lean/PleaNP/Barriers/RelativizationProof.lean`, `docs/STATEMENTS/
Soundness.spec.md`): the total-computability console oracles (A2) and the
one-query machine's concrete `P^A` memberships (A3) that the full
`NP^A ⊆ P^A` simulation (A3 assembly) and the sandwich (A5) compose. Same
demonstrated-intentional pattern as `OracleSmoke`'s smokes and the
`BarrierCalculus` propagation instances.

**Disposition.** No-action. Registered in
`tooling/gates/gate_review_register_check.py` EXPECTED.
`P_subset_NP_console` (the A4 easy direction, `P_A A ⊆ NP_A A`
instantiated at the console oracle) joins the same register: it is the first
half of the collapse sandwich, consumed by the A5 assembly (issue #63 Pass 3).


## 6. Rung-4 barrier-classification method (issue #73 Pass 1)

`binder_usage_scan.py` flags `Classification.classification_uniform` and
`Classification.oneQuery_classification_uniform` (lean/PleaNP/Calculus/
Classification.lean) as unreferenced. They are the **intentional public
API** of the Rung-4 classification method: the spine theorem
`classification_uniform` (Relativizing-membership ⟹ UniformInOracle, via
the #65 soundness bridge) and the A3 method demo (the #63 one-query
machine's constant-oracle language memberships classified as
oracle-uniform). Each lower-bound family (#72 AC0, #74 monotone, #75
resolution, #76 Williams) instantiates this spine once its proof lands.
Same demonstrated-intentional pattern as the Soundness uniformity lemmas.

**Disposition.** No-action. Registered in
`tooling/gates/gate_review_register_check.py` EXPECTED.
