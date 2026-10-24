# Machine family + canonical `decode` for the BGS (b) diagonalization

**Rung:** 2 (local piece). **Status:** Decision record — the modelling choice
#18's owner-approved direction ("take the concrete branch", 2026-10-23) requires
before any proof work. **Recorded as:** `DEC-028` in `docs/decisions/LOG.md`.
**Supersedes:** the open modelling question in `docs/STATEMENTS/Oracle.v5-repair.spec.md`
§3.1 ("the local agent picks the cleanest concrete rendering"). **Read first:**
`docs/STATEMENTS/Oracle.v5-repair.spec.md` (§2, §3.1, §4.3), `DEC-024` (the
word-query direction), `lean/PleaNP/Computability/Oracle.lean` (the landed v5
substrate), `lean/PleaNP/Barriers/DiagonalAssembly.lean` (the D6 gap).

---

## 1. The decision

**Adopt the two-symbol Bool machine family with the length-tagged identity
`decode`.**

Concretely, the family the BGS diagonalization enumerates over is the family of
`FinTM2` machines whose **input/query alphabet is `Bool`** and whose `decode`
is the canonical **length-tagged bitstring decode**:

```lean
-- the query tape alphabet
Γ kq = Bool

-- the canonical decode: an n-symbol Bool word is an n-bit string,
-- tagged by its own length
decode : List Bool → Query          -- Query = Σ n : Nat, Bits n
decode w = ⟨w.length, fun i => w.get i⟩
```

This is the *one* family, not a disjunction: every `P_A`/`NP_A` witness machine
in the D6 assembly is a member of it, and the diagonalization's `M_of`
enumeration (D3, `DiagonalEnum.lean`) runs over exactly this family's syntax.

### Why this family and not another

- **It is already the landed substrate's alphabet.** `Oracle.lean`'s v5
  `Machine.decode : List (tm.Γ tm.k₀) → Q` and the smoke machine
  (`OracleSmoke.lean`) both use `Γ := fun _ => Bool`. Choosing any other
  alphabet would force a re-type of a module that DEC-024 already froze.
- **It is the alphabet `U_B`'s verifier actually needs.** §3.1 of the v5 spec
  requires `Γ kq` to have "at least a two-symbol alphabet" because the guessed
  witness `x : Bits n` is written bit-by-bit onto the query tape. `Bool` is the
  minimal such alphabet, so no unused symbols inflate the machine syntax.
- **`decode` is the identity-on-bits, tagged by length.** §3.1 pins this: "the
  decode maps that n-symbol word to `⟨n, x⟩ : Q` — length-tagged, exactly `U_B`'s
  query shape." Reading the word as its own bits is the only convention that makes
  the word space *be* the query space; any other encoding would make the counting
  argument (`2^n` query-words per length) an approximation rather than an equality.

### The faithfulness invariant (the reason the family choice is load-bearing)

`decode` restricted to length-`n` words must be a **bijection onto the `n`-fiber
of `Query`**:

```lean
-- surjective-enough, per Oracle.v5-repair.spec.md §4.3(5):
--   every x : Bits n is encodable by the word [x 0, x 1, …, x (n-1)]
-- injective on each fiber:
--   decode w₁ = decode w₂ → w₁ = w₂   (same length ⇒ same bits)
```

This is what keeps BGS clause (b) faithful. The diagonalization's "fewer than
`2^n` queries, so an unqueried string exists" argument (D1 counting,
`DiagonalCounting.lean`) counts over the **query-word space**, and the family
choice is what makes that space the `n`-fiber of `Query` — size exactly `2^n`.
A family whose `decode` collapsed words (e.g. one that ignored all but the first
symbol) would leave `U_B` and the diagonalization living over different spaces,
and the counting argument would not transfer.

---

## 2. What each build step carries

The #18 re-split chain (#222 → #223 → #224 → #225) implements this decision.
Each step's exact Lean obligation, with the file it lands in:

| Step | Issue | Lean obligation | File |
|---|---|---|---|
| 1 (this) | #222 | *(none — this document)* | `docs/STATEMENTS/Relativization.machine-family.md`, `docs/decisions/LOG.md` |
| 2 | #223 | The concrete `FinTM2` family instance (`Γ := fun _ => Bool`, a query-tape index) + the canonical `decode` + the fiber-bijection lemma | `lean/PleaNP/Barriers/DiagonalFamily.lean` (new) |
| 3 | #224 | `MachineCode.simulates`: every `P_A`/`NP_A` witness of the family is simulated by the `M_of` enumeration, and *runs at all* (`∀ i, ∃ k n, Simulate i k n ≠ none`) | `lean/PleaNP/Barriers/DiagonalBridge.lean` — **not met.** #224 landed a vacuous `simulates` field (it did not mention `M` and was `rfl`-true by `code_encode_ofNat`); #226 removed it. Step 3 remains open: a genuine `Machine → Code` agreement relating a code's `evaln` to the machine's own `step`-based run. |
| 4 | #225 | The D6 composition: `exists_separating_oracle_assembly` over the family + bridge, `sorry`-free | `lean/PleaNP/Barriers/DiagonalAssembly.lean` |

### The gap the family choice leaves open (carried to step 3)

The 2026-10-24 sizing comment on #18 records the substrate-level obstruction
precisely: "the theorem quantifies over every `P_A B` witness `Machine`, while
the diagonalization runs over `Nat.Partrec.Code` (via `M_of`) … there is no
code-level bridge from an arbitrary `P_A` witness to the enumerated indices."

The family decision *narrows* this gap without closing it: it fixes which
machines the quantifier ranges over (Bool-alphabet, canonical-`decode`), so step 3
no longer faces "an arbitrary `decode` factor" — it faces one concrete family.
That is the reduction the owner's direction buys. Closing the bridge itself is
step 3's obligation, not this step's.

### Evidence checked

- `lean/PleaNP/Computability/Oracle.lean:67` — `decode : List (tm.Γ tm.k₀) → Q`
  (the v5 field this decision instantiates).
- `lean/PleaNP/Computability/OracleSmoke.lean:57` — `Γ := fun _ => Bool`
  (the alphabet already in use).
- `lean/PleaNP/Barriers/BGSDiagonal.lean:45-49` — `Bits n = Fin n → Bool`,
  `Query = Σ n, Bits n` (the frozen statement `decode` must land in).
- `lean/PleaNP/Barriers/DiagonalEnum.lean:33-40` — `M_of i := Denumerable.ofNat Code i`
  (the enumeration step 3 bridges to).
- `lean/PleaNP/Barriers/DiagonalAssembly.lean:38-56` — `Simulate`,
  `simulate_mono`, `simulate_bound` (the window facts step 3 must respect).

---

## 3. What this does not do

- **No Lean change.** Step 1 is a written finding plus a decision record, per
  #222's Definition of Done. The family's implementation is step 2.
- **No `Machine → Code` bridge.** That is step 3, and the family choice above is
  what makes it tractable.
- **No change to the frozen statements.** `BGSDiagonal.lean` and
  `Relativization.lean` are untouched, per Gate-1/4 discipline.
