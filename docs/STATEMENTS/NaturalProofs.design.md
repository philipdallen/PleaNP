# Natural Proofs design — N1–N6 proof-path decomposition (#67)

**Status:** working-design note for the Natural Proofs barrier (Razborov–Rudich,
Rung 3b). Written 2026-09-13 (run=RUNID-67) during the #67 claim. **NOT a
frozen proof spec and NOT a proof** — a decomposition plan that seeds the
proof work, modeled on `Relativization.diagonalization-design.md` (#22) and
the #62 BGS clause-(a) design (A1–A5).

**Companion docs:** `docs/STATEMENTS/NaturalProofs.md` (frozen informal
statement — the Gate 1 anchor); `NaturalProofs.proof-strategy.md` (informal
strategy, §2/§3); `docs/GAP_AUDIT.md` §6 (Mathlib circuit coverage);
`docs/UPSTREAM_TRACKING.md` §6 (complexitylib's circuit model + Fourier
subtheory).

---

## 1. What is already in place / pinned

- **Statement frozen** (informal, `NaturalProofs.md` §1): the *conditional*
  theorem — under an OWF/PRFF hypothesis, no `P`-natural property
  (usefulness + constructivity + largeness) is useful against `P/poly` for
  superpolynomial circuit-size lower bounds.
- **Strategy written** (`NaturalProofs.proof-strategy.md` §3): the reduction —
  a natural property used as a **distinguisher** between a PRFF `f_s` and a
  random function `R`, contradicting the PRFF's pseudorandomness. All three
  property conditions are load-bearing (constructivity -> the test; largeness
  -> random functions pass; usefulness -> small-circuit `f_s` fails).
- **Scope/hard pins** (from the statement): v1 uses `P`-natural
  (`poly(2^n)`-time constructivity) and density `1/2^n` largeness; the
  hardness parameter must be explicit (`2^{n^e}`, `e > 0`); the OWF/PRFF
  enters as a **hypothesis** (never constructed); namespace
  `PleaNP.Barriers.NaturalProofs`.

## 2. The substrate gap (circuit side)

The single hard prerequisite is the **circuit substrate** (`P/poly`, circuit
size). Mathlib has no circuit model (per `docs/GAP_AUDIT.md` §6); the options:

- **(a) build `PleaNP.Circuits`** (Rung 4, issue #71) — own `P/poly` +
  circuit-size + a `BoolFunction`/truth-table substrate. Unblocked by nothing
  external (pure definitions), but a real sub-project.
- **(b) import complexitylib's circuit model** — after the v4.30-to-v4.31
  toolchain reconciliation (#70). This is the same decision Rung 4 owns (#71).

**This design does not choose (a)/(b) — it routes either.** Every N-sub-task
below is written against the *interface* ("circuit-size predicate",
"`P/poly` membership") and is substrate-agnostic, so the choice can land
without rework of the reduction core.

## 3. The proof shape (independent of the substrate choice)

Assume a `P`-natural property `C = {C_n}` useful against `P/poly`. Build a
distinguisher `D` with oracle access to a function `g` (either `f_s` or `R`):
query `g` on all `2^n` inputs for its truth table, run `C_n`'s membership
test (that is constructivity), and guess "random" if `g` is in `C_n`,
"pseudorandom" otherwise. Largeness makes `D(R) = random` non-negligible;
usefulness plus the small-circuitness of `f_s` makes `D(f_s) = random` always
false for large enough `n`. So `D` has non-negligible distinguishing
advantage — contradicting the PRFF's pseudorandomness. Hence no such `C`
exists.

### 3.1 Decomposition (each a one-run sub-task; gates per
`docs/MULTI_AGENT_WORKFLOW.md` §Gates; `#barrier_check` discipline per Rung 5)

| # | Sub-task | Lean obligation | Blocked by |
|---|---|---|---|
| **N1** | **Circuit substrate decision**: `P/poly` + circuit-size predicate; truth-table/`F_n` substrate | decide (a) `PleaNP.Circuits` (#71) vs (b) complexitylib (#70) — author the import/definitions: a `BoolFunction n` carrier (`Fin n -> Bool` indexed), a `CircuitSize le k` predicate, and `MemPpoly` | #70/#71 substrate choice (substrate-agnostic core still proceeds) |
| **N2** | **Natural property definition** (rendered faithfully to spec §1(2)(3)): `Natural C := Useful C ∧ Constructive C ∧ Large C`, with (i) usefulness: `f ∈ C_n i.o. -> f ∉ P/poly`; (ii) constructivity: membership decidable in `poly(2^n)` (`P`-natural); (iii) largeness: density at least `1/2^n` | a `Natural` structure over `F_n` with the three fields; Gate 2 (no `P/poly` redefinition) + Gate 4 read-back | N1 (carrier), OWF-hypothesis typing |
| **N3** | **OWF/PRFF hypothesis** (as a *hypothesis*, not constructed): a seeded PRFF `{f_s : Fin n -> Bool}` + a pseudorandomness/indistinguishability predicate (`DistAdvantage A f_s ≤ 2^{-n^e}`) as a `variable` / assumed type | a `PRFFHyp` type with the hardness parameter explicit (`NaturalProofs.md` §7); **never** a theorem/axiom (Gate 5 trap, spec §4) | none (assumed) — but needs the N1 truth-table substrate for "query all inputs" |
| **N4** | **Distinguisher construction** `D` (the crux): given oracle `g`, compute the truth table (all `2^n` queries), run `C_n`'s decider (constructivity), output random/pseudorandom | a `Distinguisher` def + correctness lemma `∀ g, (g ∈ C_n) ↔ D(g) = random`; the heart (proof-strategy §3 step 2) | N2 (property), N3 (PRFF typing) |
| **N5** | **Contradiction / assembly**: `D` distinguishes `f_s` from `R` with non-negligible advantage — contradiction with PRFF pseudorandomness — giving `¬ ∃ C, Natural C ∧ UsefulAgainstPpoly C` | the reduction + negation; then the conditional theorem `OWF_hyp -> ¬(∃ natural property useful against P/poly)` in `lean/PleaNP/Barriers/NaturalProofs.lean` (to be created) | N1–N4 |
| **N6** | **Gates + read-back + comparator + file layout** (per DEC-022): statement module (`NaturalProofs.lean`) stays proof-free; separate proof module; `#print axioms` standard-only; comparator / JSON as `formalization.yaml` row | alignment rows + CI + read-back vs `NaturalProofs.md` §5 | N5 (the proved theorem) |

### 3.2 Mathlib hooks / prior-art (verified present, v4.31.0)

- **Truth-table / Boolean functions:** `Bool`, `Fin n -> Bool`, `List` /
  permutation machinery — all present upstream.
- **Counting / largeness:** `Nat.choose` / `2`-power growth
  (`pow_lt_pow_right0`, `Archimedean`) — reused for the `1/2^n`-density and
  `2^n`-query-count obligations.
- **Polynomial time (constructivity):** `Polynomial ℕ` + `p.eval n`, already
  imported by `OracleComplexity.lean` — reused for the `poly(2^n)`-time
  constructivity reading.
- **complexitylib (when importable after #70):** Fourier/analytical
  subtheory (O'Donnell ch.1) is the closest circuit-side substrate (spec §6);
  the natural-property definition may reuse it, but the barrier core is
  substrate-agnostic.
- **No OWF/PRF exists upstream** (spec §6 / `docs/PRIOR_ART.md` crypto
  section): confirms the OWF-as-hypothesis route.

## 4. What is missing (gaps to file as sub-tasks when this design is approved)

- **The circuit substrate** itself (`PleaNP.Circuits`, #71) — the biggest
  missing piece; the N1 decision routes into it.
- **The hardness parameter `e`** — a Lean-author decision (spec §7(1)),
  deferred to the N3 hypothesis definition.
- **File the N1–N6 sub-tasks** as separate issues with `Blocked by` this
  design (after approval) — per the same filing pattern as #62/#22.

## 5. Recommendation / priority

1. **N1 (circuit substrate decision) is the fork in the road.** Everything
   else keys off it; it is the same decision Rung 4 (#70/#71) owns. Do it
   first, coordinated with #71.
2. **N3 (OWF hypothesis) can proceed immediately** — an assumed type with an
   explicit hardness parameter; no circuit substrate needed. Lowest-risk first
   step (proof-strategy §4: "Easy").
3. **N2 (natural-property def) is substrate-agnostic** and can be drafted in
   parallel once N1's carrier exists.
4. After N1–N3, execute N4 (distinguisher) -> N5 (contradiction/assembly) ->
   N6 (gates/comparator) in dependency order, one sub-task per run.

---

_Last updated: 2026-09-13 (issue #67, design doc). The N-sub-task issues are a
follow-up once this design is approved._