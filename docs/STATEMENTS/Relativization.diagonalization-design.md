# Diagonalization design - BGS clause (b), sub-task 2 (#22)

**Status:** working-design note for `lean/PleaNP/Barriers/BGSDiagonal.lean`
(the proof of `exists_separating_oracle`, clause (b)). Written 2026-09-07
(run=20260907-2107-59bc) during the #22 claim. **NOT a frozen proof
spec and NOT a proof** - a decomposition plan that seeds the proof work,
per the sizing rule (one task = one agent run; tasks that can't fit get
decomposed further).

**Companion docs:** `docs/STATEMENTS/Relativization.md` (frozen informal
statement); `Relativization.proof-strategy.md` (§2 clause (b) sketch; §5
open proof-strategy questions); `docs/STATEMENTS/Relativization.lean.spec.md`
(rendering spec); `lean/PleaNP/Barriers/BGSDiagonal.lean` (U_B +
witness-core, #21 done).

---

## 1. What is already in place

- `lean/PleaNP/Barriers/BGSDiagonal.lean` (#21): `U_B : Oracle Query -> Set Nat` with
  `Query = Sigma n : Nat, Bits n`, `Bits n = Fin n -> Bool`; `IsWitness`;
  `U_B_iff_witness` (witness-core, zero sorry). Builds green.

- `lean/PleaNP/Computability/Oracle.lean` (v4): `Oracle Q := Q -> Bool`, `Machine Q tm` with
  `queryLabel`/`yesLabel`/`noLabel`; `step` branches on the query label,
  consults the oracle, routes to yes/no labels; `evalsTo_unique_result`
  (deterministic halting endpoints agree). Builds green.



- `lean/PleaNP/Computability/OracleComplexity.lean` (v4): `P_A`, `NP_A`, `AcceptsInTime`,
  `P_A_subset_NP_A` (both directions). Builds green.


## 2. The substrate wall that #22 inherits from #26/#27

`#26/#27` record a hard type-level contradiction for constructingthe
*membership* machine (`U_B in NP_A (alpha := Nat) B`): `NP_A` requires
`tm'.Gamma tm'.k0` to equal `Query = Sigma n : Nat, Bits n`, but `FinTM2`
bundles `[Gammak0Fin : Fintype ( Gamma k0)]` and `Fintype Query` is provably
uninhabitable (`Nat` injects via all-false length-tagged strings). See
`blockers/closed_20260907-0953_bgs26-infinite-query-fintype.md`.

**#22 inherits the same wall.** The separating oracle `B` in the BGS stage
construction also lives over `Sigma n : Nat, Bits n` (a query about an n-bit
string tagged by length), and `P_A (alpha := Nat) B` quantifies a
machine with the same bundled-Fintype constraint - so any stage-machine
simulation/tournament against `B` hits the same `Fintype Query` wall. The
diagonalization cannot be completed against the *current* substrate as stated;
the resolution options ((a) finite reindexed query family, (b) substrate
generalization to infinite alphabets, (c) per-length reindexed class shape) in
#27 are the same options this task's shaft must await. This makes #22
**de facto blocked** on the same human decision - the "soft-blocked" note
in its body anticipated this.

**Recommendation to the queue:** #22 should be treated as
`status:blocked-needs-input` (or kept available only for the *design* work
below, which does not need the machine construction) until #27's human
decision lands. The design below is written so each option (a/b/c) can be
picked up without rework of the *combinatorial* core.


## 3. The proof shape (independent of the substrate choice)

The BGS clause-(b) strategy (per `Relativization.proof-strategy.md` §2):

> Build `B : Oracle Query` in stages `B_0 subseteq B_1 subseteq ...` so that for
> every deterministic poly-time oracle machine `M_i`, `M_i^B` fails to
> decide `U_B` on some input `1^n`: run `M_i` with "no" answers for
> fresh queries; if it accepts, leave B empty on length-n; if it
> rejects, add an unqueried n-bit string to B. Then `U_B in NP^B`
> (universal, #21) and `U_B notin P^B` (by the tournament), so `P^B != NP^B`.


### 3.1 Decomposition (each a one-run sub-task; gates per
`docs/MULTI_AGENT_WORKFLOW.md` §Gates:

| # | Sub-task | Lean obligation | Blocked by |
|---|---|---|---|
| D1 | **Counting lemma**: `exists n, p.eval n < 2^n` (per-stage `2^n >` queries) | new lemma in a `Combinatorics`/`lean/PleaNP/Barriers/Counting.lean (to be created)` - the unqueried-string existence crux; Mathlib hooks below | None (pure Nat/Polynomial) |
| D2 | **Finite query family reindex** (per #27 option (a/(c)): `Bits (Fin N)` or per-length `Bits n` with bounded `N` | private bounded `Query`/`Bits` rework in `lean/PleaNP/Barriers/BGSDiagonal.lean` | #27 decision |
| D3 | **Machine enumeration**: poly-time oracle machines as Nats (`M_i <-> code`) | encoding of `FinTM2`+`Machine`; or reuse `Partrec.Code` if the tournament weakens to partial-recursive machines | substrate + #27 decision |
| D4 | **Stage construction**: `B : Nat -> Oracle Query` (monotone stages `B_k subseteq B_{k+1}}`;diagonalization at stage k not undone later | inductive def + monotonicity invariant | D2, D3 |
| D5 | **Tournament lemma**: forall code i, stage i gives `M_i^B(1^n) != U_B(1^n)` via the unqueried-string choice | combines D1, D4 | D1-D4 |
| D6 | **Assembly**: `U_B notin P^B`, then `exists B, P_A B != NP_A B` in `lean/PleaNP/Barriers/Relativization.lean` | composition + #23's job (sub-task 3) | D3-D5, #21 |

> **Landed status (2026-09-19, run=20260919-0920-p8k2).**
> - **D1** ✅ `DiagonalCounting.poly_lt_two_pow` (+ the `2^n` growth lemmas).
> - **D2** — no longer needed under the DEC-024 word-query substrate (the full
>   infinite `Query` stays); row is historical.
> - **D3** ✅ `DiagonalEnum` (`M_of`, encode roundtrips, `evaln` bounded
>   simulation); the `Machine → Code` step is now precisely characterized — the
>   oracle is *pinned* by the `P_A`/`NP_A` witnesses (`DiagonalSyntax`/#118), so
>   only the finite program factor is enumerated; what remains is the routine
>   "fix a concrete machine family + canonical `decode`" modeling step.
> - **D4** ✅ `DiagonalStages` (abstract `MonotoneChain` + `mem_mono_of`) and,
>   as of `b9cf909`, the **concrete** chain invariant:
>   `DiagonalChain.stageChain_step_mono` / `stageChain_monotone` /
>   `stageChain_mem_persist` / `stageChain_added_persist` /
>   `stageChain_tail_agree` — the construction provably satisfies the
>   "diagonalization not undone" invariant.
> - **D5** ✅ the per-length decision (`DiagonalDecision`) and, as of
>   `1040e94`, the **chain-lifted** reject flip
>   (`DiagonalChainFlip.flip_persists_over_chain`): once stage `k` flips `U_B`
>   true at `n`, it stays true at every later stage. The remaining D5 gap is
>   the machine-behaviour half (that `M_i^B` cannot answer `U_B` at the flipped
>   length) — which needs the D3 machine-embedding, not more combinatorics.
> - **D6** — open; the single tracked `sorry` is
>   `DiagonalAssembly.exists_separating_oracle_assembly` (SORRY_TRACKER #12).
>   **Scoping (2026-09-22, run=20260922-1701-k9x2).** The composition does
>   NOT close from the landed D1–D5 substrate without one further modeling
>   decision, so it was recorded as a `NEEDS:` blocker on #156 rather than
>   left as a silent `sorry`. The precise gap is the machine-behaviour half
>   the D5 row above already names. As stated, the theorem quantifies over
>   *all* `P_A B` witnesses, and a `MachineCode.simulates` field is part of
>   the data of a witness, so a proof cannot choose it. Closing D6 requires
>   fixing, ONCE, a concrete machine family and a canonical `decode`, then
>   carrying a lemma that each `P_A` witness under that family is correctly
>   simulated by the `M_of` enumeration *and runs at all* (`∀ i, ∃ k n,
>   Simulate i k n ≠ none`). The `simulate_bound` fact (`evaln` decisions
>   require `n < k`) makes the window a function of the input, so the
>   "punt-into-accept" route alone does not give this. This is the same
>   modeling step #118 localized; it is a genuine choice, not more
>   combinatorics.

### 3.2 Mathlib hooks (verified present, u v4.31.0)

- **`2^n` growth:** `Nat.two_pow_*` family; `pow_lt_pow_right0`
  (`Algebra/Order/GroupWithZero/Basic.lean:568`)(`1 < a -> m < n -> a^m < a^n`);
  `Algebra/Order/Archimedean/Basic.lean:158`
`pow_unbounded_of_one_lt (x : R) (hy1 : 1 < y) : exists n, x < y^n` -
  the raw exists-n hook (works over any `ExistsAddOfLE` semiring;
  `Nat.choose_lt_two_pow` (`Data/Nat/Choose/Bounds.lean:91`) for
  binary-string counting.

- **Polynomial time bound:** `Polynomial ℕ` from
  `Mathlib.Algebra.Polynomial.Basic` (already imported by
  `lean/PleaNP/Computability/OracleComplexity.lean`);`p.eval n` is Nat-valued.




- **Computable enumeration substrate:** `Nat.Partrec.Code` + `Denumerable Code`
  (`Computability/PartrecCode.lean:176`),`evaln` (bounded-step eval,
  `:568`),`evaln_complete`(`:690`),`primrec_evaln` (`:922`),
  and Rogers/Kleene fixed points (`:1004`,`:1022`) - the cleanest
  "enumerate programs + simulate for bounded steps" machinery Mathlib
  has. Gap: it enumerates *partial-recursive* codes, not *poly-time
  Oracle machines* - D3 must bridge (a `Computable`/`P`-detector,
  or a diagonalization that tolerates non-poly machines by punting slow
  ones to a filler input).
- **Determinism:** `evalsTo_unique_result` (Oracle.lean) - needed to
  know `M_i^B` has one behavior per input (tournament soundness).
- **BGS sandwich/PSPACE (clause (a):** not needed for (b):

## 4. What is missing (gaps to file as sub-tasks when the design is
approved) besides D1-D6:

- **Fintype Query decision** (#27): **RESOLVED (DEC-024, 2026-09-11)** — Option Ω (word-query oracle substrate,:the query is read from a tape's content over the machine's own finite alphabet, per the spec's "oracle tape" model (`Oracle.lean.spec.md` §2.2);recorded options ((a) finite query family,(c) per-length reindexing) become unnecessary;`Query = Σ n, Bits n` and **all frozen statements stay unchanged**;the fix is substrate-wiring-only (#33 work order,#35 implementation). D2's "finite-query-family reindex" row below is **no longer needed**;D3–D6 proceed over the repaired substrate in dependency order.

- **Machine encoding of FinTM2-oracle machines** (D3): no upstream
  instance; `Partrec.Code` is the closest reusable substrateand needs a
  reduction/bridge argument.

- **`#barrier_check` interplay:** any proof closing this must report the
  elaborator verdict per the gates discipline (expected: `#barrier_check`
  on the final `exists B, P_A B != NP_A B` in `lean/PleaNP/Barriers/Relativization.lean`: the
  statement itself carries no `Relativizing` instance -> **Inconclusive** -
  which is correct: BGS is the *meta*-theorem showing relativizing proofs
  can't resolve P vs NP, not itself a relativizing proof.). (Documented
  for #23's done-comment when it lands)

---

## 5. Recommendation scope for the next session

1. **D1 (counting lemma** can start immediately, u naffected by #27:
   prove `forall p : Polynomial Nat, exists n, p.eval n < 2^n` (or the per-stage
   `exists n, p.eval n < 2^n` bound) in a new `Combinatorics` module -
   pure Nat/Polynomial, no oracle substrate. Gate-evidence: build + hygiene.


2. **File #22's substrate blocker** afresh when the claim is swept: #22 inherits
   #27's human decision; the design above is written to route every option.

3. **After #27 lands:** execute D2-D6 in dependency order, one sub-task per run.