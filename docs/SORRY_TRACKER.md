# Sorry tracker: open proof/composition debts

**Purpose.** Track every `sorry` in the PleaNP Lean codebase.

**Rule:** every `sorry` in `lean/PleaNP/` must appear in this table.

**Last updated:** 2026-09-22 (sorry-tracker scan, issue #127).

---

## Summary

| File | `sorry` count | Level |
|---|---|---|
| `lean/PleaNP/Computability/Oracle.lean` | 0 (was 1 — vacuous marker removed, see #2) | Substrate (Rung 2) |
| `lean/PleaNP/Computability/OracleComplexity.lean` | 0 (was 3) | Complexity classes (Rung 2) |
| `lean/PleaNP/Computability/OracleUpstreamP.lean` | 1 (was 2 — statement-level sorry #6 resolved, see below) | Upstream-P anchor (Rung 2) |
| `lean/PleaNP/Barriers/Relativization.lean` | 2 | Barrier statement (Rung 3a) |
| `lean/PleaNP/Barriers/DiagonalAssembly.lean` | 1 | BGS clause-(b) assembly scaffold (Rung 3a) |
| **Total** | **4 open** (6 resolved, 1 removed) | |

All remaining sorries are honest pending proofs/compositions. The structural
self-check `P_A ⊆ NP^A` (#5a/#5b) is now proved in BOTH directions — the v4
repair is behaviorally verified by the oracle-sensitivity smoke test
(`lean/PleaNP/Computability/OracleSmoke.lean`). The four remaining sorries are: upstream-P-blocked
(#7 — in the isolated anchor module; #6's statement-level sorry was resolved
by `UpstreamPolyTime`) and the BGS proofs (#8, #9, #12). The #36 U_B-machine
bridge + assembly (#10/#10b/#11) were RESOLVED 2026-09-13 —
`DiagonalUB.lean` is zero-sorry.

The counts here are machine-checked against the code by
`tooling/gates/sorry_tracker_scan.py` (Tier 1; wired into CI): the set of open
rows (file:line) must equal the set of `sorry` sites in `lean/PleaNP/`, and the
per-file/Total counts must agree. Edit this file and the scan together.

`lake build` status: `lean/PleaNP/Computability/Oracle.lean`, `lean/PleaNP/Computability/OracleComplexity.lean`,
`lean/PleaNP/Computability/OracleSmoke.lean` build green. `lean/PleaNP/Computability/OracleUpstreamP.lean` (1 tracked sorry,
the honest proof #7 — its statement-level sorry #6 was resolved by `UpstreamPolyTime`)
and `lean/PleaNP/Barriers/Relativization.lean` (2 tracked sorries) fail exactly on their tracked
sorries — the expected Gate-6-visible state.

Tier-2 axiom check (`#print axioms`) on the new proofs:
`evalsTo_unique_result` → {propext, Quot.sound};
`P_A_subset_NP_A`, `smoke_accepts_true`, `smoke_rejects_false` →
{propext, Classical.choice, Quot.sound}. All within the trusted
Mathlib-standard set; no `sorryAx`.

---

## Detailed inventory

### Substrate level (Oracle.lean)

| # | File:Line | What it is | Pending on | Priority |
|---|---|---|---|---|
| 2 | ~~`Oracle.lean:115`~~ **Removed** — `P_empty_eq_upstream_P` was a `True`-conclusion marker theorem whose only content was its sorry (vacuous by construction, and it blocked every `lake build` under `warningAsError`). The real tracking anchor is the class-level theorem (#6/#7), so the marker was deleted rather than left half-alive. | Upstream P (DEC-003) — now tracked only via #6/#7. | Medium |

### Complexity-class level (OracleComplexity.lean)

| # | File:Line | What it is | Pending on | Priority |
|---|---|---|---|---|
| 5a | ~~`lean/PleaNP/Computability/OracleComplexity.lean`~~ **Resolved** — forward direction proved in the v4-completion pass. | — | — |
| 5b | ~~`lean/PleaNP/Computability/OracleComplexity.lean`~~ **Resolved** — backward direction proved in the v4-completion pass via the new determinism lemma `Oracles.evalsTo_unique_result` (+ `step_none`) in `lean/PleaNP/Computability/Oracle.lean`: the accept-run and the decide-run start from the same initial config and both halt, so they share the halted endpoint; the output bit carries over. | — | — |

### U_B-machine level (DiagonalUB.lean, new isolated module — #36 Pass 1-2)

Isolated module `lean/PleaNP/Barriers/DiagonalUB.lean` (not imported by
BGSDiagonal) so `warningAsError` does not cascade. Proved zero-sorry:
certificate encoding roundtrip (`encWord`/`decodeWord_encWord`), the
guess-query-verify machine (`ubTM`/`ubM`), and its concrete-oracle
behavior (`accepts_const_true`, `rejects_const_false`). **All three gaps resolved 2026-09-13 — the module is zero-sorry** (see rows #10/#10b/#11 below).

| # | File:Line | What it is | Pending on | Priority |
|---|---|---|---|---|
| 10 | ~~`lean/PleaNP/Barriers/DiagonalUB.lean`~~ **Resolved 2026-09-13 (run=20260911-0944-qmzn)** — reject-run identity inside `accepts_true_oracle` proved (the `evals_in_steps` closes via `simp [ubRun, flip, ...]` + `congr 1`). | — | — |
| 10b | ~~`lean/PleaNP/Barriers/DiagonalUB.lean`~~ **Resolved 2026-09-13** — `accepts_depends_on_answer` proved (query-step routes to yes-branch via `ubRun_halts_yes`; output head true). | — | — |
| 11 | ~~`lean/PleaNP/Barriers/DiagonalUB.lean`~~ **Resolved 2026-09-13** — `U_B_in_NP` proved zero-sorry: `erw [encWord_length]` closed the polynomial-X bound; assembly via `decodeWord_encWord` + `certBits_encodeList` + `accepts_time_shift`. | — | — |

### Upstream-P anchor level (OracleUpstreamP.lean, new module)

Isolated into its own leaf module so `warningAsError` does not cascade from
these two sorries into OracleComplexity and everything downstream. The
module is expected to fail the build until upstream P lands.

| # | File:Line | What it is | Pending on | Priority |
|---|---|---|---|---|
| 6 | ~~`OracleUpstreamP.lean`~~ **Resolved** (run=20260913-1007-fUj8, issue #40) — the statement-level sorry was filled: the RHS is now the oracle-free `UpstreamPolyTime` recharacterization (`TM2ComputableInPolyTime` membership; `lean/PleaNP/Computability/OracleComplexity.lean`), per Trap 3. The theorem now fully renders P^∅ = P; no Gate-5 concern remains. | — | — |
| 7 | `OracleUpstreamP.lean:32` | `P_empty_eq_upstream_P_class` — proof of P^∅ = P equality (now between fully-rendered sides). | Upstream P (DEC-003), or an oracle-free recharacterization of the class + the no-query-machine equivalence. | Medium |

### Barrier-statement level (Relativization.lean)

> **File layout (2026-09-13, issue #66):** `Relativization.lean` is the
> claim root (the two theorem sorries #8/#9 live here as honest
> placeholders). Proof work proceeds in `RelativizationProof.lean`
> (barrier-consequence lemmas; A1–A5/D1–D6 land there), which the claim
> root does not import. When #18/#63 close, these rows flip to "Resolved"
> and the claim root's sorries are replaced by the assembled proofs.

| # | File:Line | What it is | Pending on | Priority |
|---|---|---|---|---|
| 8 | `Relativization.lean:89` | BGS clause (a) proof — equalizing oracle existence. | #5 (done) + PSPACE/QBF + upstream P. | Low (Rung 3 Step 6) |
| 9 | `Relativization.lean:110` | BGS clause (b) proof — separating oracle existence (diagonalization). | #5 (done) + machine enumeration + diagonalization. | Low (Rung 3 Step 6) |


### DiagonalAssembly level (DiagonalAssembly.lean, new isolated module - #37 assembly scaffold)

Isolated leaf module (not imported by clean modules) so `warningAsError`
does not cascade. Proved zero-sorry: `Simulate`, `simulate_returns`
(bounded enumeration simulation connects to unbounded eval), `PuntsSlow`
(the punting strategy), `stage_step_exists` (the tournament flip handle).
One tracked sorry:

| # | File:Line | What it is | Pending on | Priority |
|---|---|---|---|---|
| 12 | `lean/PleaNP/Barriers/DiagonalAssembly.lean:105` | `exists_separating_oracle_assembly` - the assembled "exists B, P_A B != NP_A B" (the BGS clause-(b) target #9). Needs the Machine-to-Code bridge (#23/#97 gap: poly-time oracle machines into Partrec.Code) plus the stage/tournament composition of the Diagonal* modules. **Re-scoped by #118**: the `DiagonalBridge` note that the bridge was blocked by the uncountability of the oracle space is misplaced — `P_A`/`NP_A` witnesses **pin** `M.oracle = A` (proved: `DiagonalSyntax.mem_P_A_oracle_pinned`), and `DiagonalSyntax.machineEquiv` localizes the uncountable content in the `oracle`/`decode` factors while the program factor is finite (`Fintype` proved). What remains is the routine modeling step: fix a concrete machine family + canonical `decode`, then enumerate. **#120**: the module's `BridgeObstacle` — previously an *unproved* `def : Prop` "documentation marker" (whose bound did not occur in its body, so it asserted nothing) — is now a **proved theorem** (`DiagonalBridge.oracle_uncountable`, `BridgeObstacle`), via `Cardinal.mk_arrow` + `cantor`. | Concrete machine family + canonical `decode` (modeling step, #118) + compose stage_step_exists over the enumeration. **#226**: the step-3 `MachineCode.simulates` bridge landed by #224 was vacuous (its field never mentioned `M`; `rfl`-true by `code_encode_ofNat`) and was removed. The genuine `Machine → Code` agreement remains open, so this obligation is not closer than before #224. | High |

### Machine-syntax factorization (DiagonalSyntax.lean, new — #118)

`lean/PleaNP/Barriers/DiagonalSyntax.lean` is **zero-sorry** and records the
corrected BGS-bridge analysis: `MachineSyntax tm` (the machine's label triple)
is `Fintype` (proved), `machineEquiv` factors
`Machine Q tm ≃ MachineSyntax tm × Oracle Q × (List (Γ k₀) → Q)` — localizing
the uncountable content in the `oracle`/`decode` factors — and
`mem_P_A_oracle_pinned` / `mem_NP_A_oracle_pinned` prove that a `P_A`/`NP_A`
witness carries `M.oracle = A` (so the oracle is not a degree of freedom in the
diagonalization's enumeration). No `sorry`; no proof debt.

### Monotone / Rung-4 model level (issue #74 Pass 1, 2026-09-13)

`lean/PleaNP/Circuits/Monotone.lean` lands the **monotone-circuit model**
zero-sorry: the no-NOT gate basis (`MonotoneGate`), its size/depth measures,
and the **monotonicity theorem** (`monotone_eval_preserves_order`) — the
defining structural property the Razborov CLIQUE bound exploits. Pass 2
(approximation-reducer lemma) and Pass 3 (CLIQUE bound) are open proof work.

### Williams transfer theorem level (issue #90 Pass 3, 2026-09-13)

`lean/PleaNP/Barriers/WilliamsTransfer.lean` freezes the **transfer
theorem statement** zero-sorry: `SubExpCircuitSATT → NEXP_not_subset_ACC0`
(`williams_transfer`), plus the asserted classification record
(`williams_classification_asserted`, non-relativizing/non-natural/
non-algebrizing marker classes for #73/#91). The PROOF needs the tracked
sub-exponential ACC⁰-CircuitSAT bound (#89 gap: `acc0SatSubExpBound`,
Shah–Shetty Good-SAT) + the NTIME-to-CircuitSAT encoding — a decomposed
sub-lemma follow-up (no sorry).

### Williams transfer assembly level (issue #91 Pass 4, 2026-09-13)

`lean/PleaNP/Barriers/WilliamsAssembly.lean` assembles the four passes
into the final `NEXP ⊄ ACC⁰` statement (`final_NEXP_not_subset_ACC0`)
+ the transfer closure + the classification record; the classification
note is `docs/STATEMENTS/WilliamsTransfer.classification.md`. The full
zero-sorry PROOF is blocked on the tracked sub-exponential bound
(#89 gap / #98 follow-up) — never a sorry, per #76 DoD fallback.

### Williams / Rung-4 statement level (issues #72/#88, 2026-09-13)

`lean/PleaNP/Circuits/AC0.lean` (#72 Pass 1) renders the **parity ∉ AC⁰**
lower-bound statement zero-sorry as a `def` target (`parity_notin_AC0`); the
switching-lemma proof is #72 Pass 2. `lean/PleaNP/Barriers/Williams.lean`
(#88 Pass 1) freezes the **Williams-transfer statement anchors** —
`CircuitSAT`, `IsACC0`, `NEXP_membership` — zero-sorry (`statement-rendered`);
the CircuitSAT algorithm and the transfer theorem are #89/#90/#91.

### Williams Pass 2 tracked gap (issue #89, 2026-09-13)

`lean/PleaNP/Barriers/WilliamsSat.lean` delivers the **verified CircuitSAT
decider** + runtime baseline zero-sorry (`acc0SatBrute_correct`,
`acc0SatSteps_eq` = `2^n`). The **sub-exponential** bound the transfer needs
(`acc0SatSubExpBound`, `∃ c, steps ≤ 2^(n^c)`) is rendered as a tracked goal
(a `def`, NOT a `sorry`): it needs the ACC⁰-structure packing argument
(Shah–Shetty-style Good-SAT) — the actual research content, tracked so the
Pass-3 transfer contract is pinned without pretending the improvement landed.

### Lower-Bound Compiler level (issue #80 Pass 2, 2026-09-16)

`lean/PleaNP/Barriers/LowerBoundCompiler.lean` is **zero-sorry**: the
`#lower_bound_compile` elaborator skeleton emits a named claim and reports
its dependency/axiom closures, and its contract guards reject a wrong-shape,
`sorryAx`-carried, missing, or shadowing contract (pinned by `#guard_msgs` in
`lean/tests/LowerBoundCompilerGuards.lean`). The compiler depends on the
tracked `acc0SatSubExpBound` gap above: the **full** contract emission needs a
proved `SubExpCircuitSATT` (#98), so the module's example uses the conditional
form. **No new `sorry`** — the `tests` module's decoy contract carries the
only placeholder, and it is a test fixture, not a proof debt.

### Algebrization statement level (issue #69 Pass 1, 2026-09-13)

`lean/PleaNP/Barriers/Algebrization.lean` renders the **AW09 v1 statement**
zero-sorry (Gate 1 anchor; builds green in the clean module set). The two
clause *statements* are `def`s (`algebrizing_separation_statement`,
`algebrizing_equalization_statement`). The clause *proofs* (AZ5:
diagonalization for (a), PSPACE sandwich for (b)) are not yet claimed; when
proof work starts, the theorem claims land with honest placeholders here.

---

## Resolved

| # | What | Commit | Notes |
|---|---|---|---|
| 1 | `outputEncodesChi` — the per-machine output-encoding bridge | `5243a06` | Now a real predicate: `oa head = true iff x in L`. |
| 3 | `P_A` membership condition | `bc344ab` then v4 `a223b12` | Now composes `@DecidesInTime` with EvalsToInTime reachability. ea/M/t load-bearing. (hΓ added in v4 completion — see below.) |
| 4 | `NP_A` verifier condition | `bc344ab` then v4 `a223b12` | Now composes `@AcceptsInTime` on pair (x, y) with reachability. |
| 5a, 5b | `P_A_subset_NP_A` — both directions | v4-completion pass (on dev) | Forward: same machine/endpoint, empty certificate, output bit from outputEncodesChi. Backward: determinism via `evalsTo_unique_result`. |
| 10 | Certificate bound equivalence (Gate 4) | `4584d90` | Bound changed to direct `p.eval(ea(x,[])).length` (polynomial in input size). |
| 6 | P^∅ = P statement-level sorry (RHS was `{ L | sorry }`) | issue #40 (v5-word-query tests) | RHS filled by the oracle-free `UpstreamPolyTime` recharacterization (`TM2ComputableInPolyTime` membership) in `OracleComplexity.lean`; the theorem now fully renders P^∅ = P (Trap 3). Proof (#7) still tracks upstream P. |

## Removed (not resolved)

| # | What | Commit | Notes |
|---|---|---|---|
| 2 | `P_empty_eq_upstream_P` marker theorem (Oracle.lean) | v4-completion pass (on dev) | `True`-conclusion placeholder; single sorry blocked every build. Tracking roles merged into #6/#7. |

---

## Also fixed in the v4-completion pass (not sorry items)

- **P_A / NP_A ill-typed oracle constraint.** The v4 headers claimed
  `M.oracle = A` but that equation did not typecheck — `M : Machine
  (tm'.Γ tm'.k₀) tm'` has `oracle : Oracle (tm'.Γ tm'.k₀)`, not
  `Oracle Q`. Fixed per the query-type trap: machines now quantify with
  `hΓ : tm'.Γ tm'.k₀ = Q` and the constraint is `M.oracle = hΓ.symm ▸ A`.
  (Unobservable on dev because the build never got past the substrate
  sorry.)
- **NP_A typo.** `oa : tm'.Γ tm.k₁ → Bool` referenced unbound `tm`
  (never compiled).
- **Relativization.lean arg names.** `P_A (α := …)` → `P_A (alpha := …)`
  (never compiled against the class signature).
- **Smoke test (v4 acceptance item).** `lean/PleaNP/Computability/OracleSmoke.lean`: one machine
  program, two oracle instantiations — `smoke_accepts_true` (accept, by
  evaluation) and `smoke_rejects_false` (reject, by determinism +
  evaluation). The executable check that Flaw B stays fixed.
- **Determinism lemma.** `evalsTo_unique_result` + `step_none` in
  `lean/PleaNP/Computability/Oracle.lean` — the lemma #5b needed and the reject-side of the smoke
  test uses.

---

## Remaining tasks

1. **#6 (resolved):** the statement-level sorry in `P_empty_eq_upstream_P_class`
   was filled by the `UpstreamPolyTime` recharacterization (issue #40); no
   Gate-5 concern remains.
2. **#7: prove the equality** — between fully-rendered sides now; still
   pending upstream P / an oracle-free no-query-machine equivalence.
3. **#8, #9: BGS proofs** — blocked on PSPACE/QBF + machine enumeration +
   upstream P (Rung 3 Step 6).

The BGS statement (`∃ A, Computable A ∧ P^A = NP^A` / `∃ B, Computable B ∧ P^B ≠ NP^B`) is a barrier theorem *statement* rendered over machine-grounded, non-vacuous oracle classes (P^A/NP^A built on a real TM model with `EvalsToInTime` step counting). Prior renderings exist only as axioms over vacuous classes or as abstract schemes (see `docs/PRIOR_ART.md`, "Closer prior art"); ours is intended to be *provable*, not assumed. It type-checks and satisfies the rendering spec's three traps (computability hypothesis, set equality, query type). We do not claim priority — the point is that the statement is provable-in-principle, which the axiom/scheme renderings are not.

---

## Dependency chain


```
#6 (DONE, statement rendered via UpstreamPolyTime) → #7 (proof)  [upstream P, DEC-003]
#8/#9 (BGS)    ← needs {PSPACE/QBF, machine enumeration}  + upstream P
```

