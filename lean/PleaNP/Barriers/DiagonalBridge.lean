import Mathlib
import PleaNP.Computability.Oracle
import PleaNP.Barriers.DiagonalEnumOracle

set_option warningAsError true

/-!
# BGS (b): the Machine-to-Code gap — the obstacle, localized (issue #118)

**Status after `#226`:** the `#224` "Machine → Code bridge" was **vacuous** and is
not a landed result. The module's proved content is (a) the enumeration fact
`M_of` is surjective on codes, and (b) the simulate-or-punt split (`#155`, D6/O2).
A genuine `Machine → Code` agreement — relating a code's `evaln` to the machine's
own `step`-based run — remains the open step-3 obligation (`#226`).

A faithful `Machine → Code` compiler is the tournament's last gap. This module
used to record the obstruction as "*the raw `Machine Q tm` type carries an
arbitrary oracle `Q → Bool`, uncountable for infinite `Q`, so a faithful
bijective `Machine → Code` is IMPOSSIBLE and 'detect P or punt' is REQUIRED*".

**That analysis is misplaced for the statement the tournament needs**, and
`DiagonalSyntax` (#118) records the correction with proofs:

- The witnesses of `P_A A` / `NP_A A` pin the oracle by an explicit conjunct
  (`M.oracle = A` in `OracleComplexity.lean`), so the oracle is **not** a
  degree of freedom when the diagonalization quantifies over "every poly-time
  machine with oracle `B`" (which is what `U_B ∉ P_A B` means). Its
  uncountability cannot be the obstruction to enumerating *those* witnesses.
- `DiagonalSyntax.machineEquiv` factors a machine as
  `Machine Q tm ≃ MachineSyntax tm × Oracle Q × (List (Γ k₀) → Q)`. This
  **localizes** the (possibly uncountable) content in the `oracle`/`decode`
  factors; the `MachineSyntax` factor is finite (`Fintype` proved).
- `DiagonalSyntax.mem_P_A_oracle_pinned` makes the pinning explicit.

What actually remains is a *routine modeling step*, not an impossibility: the
witnesses also carry `tm' : FinTM2` (whose fields include types `Λ`, `σ`, `K`,
`Γ`, so `FinTM2` is not itself a set to enumerate) plus `decode`, `ea`, `oa`.
Enumerating those means **fixing a concrete machine family and a canonical
`decode`** — a modeling choice with a routine resolution. "Punt slow codes" is
one option among several, not a requirement.

(Historical note: the Cantor fact below is still true about the *bundled*
`Machine` type; it is simply not the obstruction it was recorded as being.)
-/

namespace PleaNP

namespace Barriers

namespace DiagonalBridge

open PleaNP.Oracles
open PleaNP.Barriers.DiagonalEnumOracle
open Turing
open Cardinal

/-- **The Cantor fact, now proved** (#120). The oracle space over an infinite
  query type is uncountable: `#(A → Bool) = 2 ^ #A` and `ℵ₀ < 2 ^ #A` whenever
  `ℵ₀ ≤ #A`.

  This replaces an earlier *unproved* `def BridgeObstacle : Prop` "documentation
  marker" (whose bound `A` did not occur in its body, so it asserted nothing —
  `binder_usage_scan` flagged it `vacuous_forall`). It is a real theorem. -/
theorem oracle_uncountable {A : Type} (h : Infinite A) :
    ¬ Countable (Oracle A) := by
  intro hc
  have hc' : Countable (A → Bool) := hc
  rw [← mk_le_aleph0_iff] at hc'
  have hinf : ℵ₀ ≤ #A := aleph0_le_mk_iff.mpr h
  have harrow : #(A → Bool) = 2 ^ #A := by
    simp
  rw [harrow] at hc'
  have hlt : ℵ₀ < 2 ^ #A := by
    calc ℵ₀ < 2 ^ ℵ₀ := cantor ℵ₀
      _ ≤ 2 ^ #A := power_le_power_left (by norm_num : (2 : Cardinal) ≠ 0) hinf
  exact absurd hc' (not_le.mpr hlt)

/-- The `BridgeObstacle` statement — *proved*, not asserted (#120): if the
  oracle space over `A` is countable then `A` is not infinite. This is the fact
  the module originally carried as an unproved marker.

  **Scope (per #118).** It is about the *bundled* oracle/`Machine` type, and is
  **not** the obstruction to enumerating the `P_A`/`NP_A` witnesses the
  tournament diagonalizes over: those pin `oracle = A` (see `DiagonalSyntax`),
  so they do not range over the oracle factor at all. -/
theorem BridgeObstacle :
    ∀ (A : Type) (_ : Countable (Oracle A))
      (_ : Infinite A), False :=
  fun _ hc hinf => oracle_uncountable hinf hc

/-- The positive, provable half the tournament DOES have: the program
  universe `Nat.Partrec.Code` is countable (Denumerable), and its
  bounded-step simulation `evaln` is what the diagonalization iterates. -/
theorem Code_countable : Countable Nat.Partrec.Code :=
  inferInstance

/-!
## The code packaging and the simulate-or-punt split (issue #155, D6/O2)

### `toCode` — a packaging, not a bridge (defect `#226`)

`toCode mc` is `(prog := mc.code, oracle := M.oracle)`: a code together with the
pinned oracle. The `#224` module described this as a faithful bridge whose code's
bounded run reproduces the machine's run (`toCode_evaln`). **That claim was
vacuous** (`#226`): `toCode_evaln` was proved from the `MachineCode.simulates`
field, which did not mention the machine and, by `DiagonalEnum.code_encode_ofNat`,
equated an expression with itself. No machine behaviour was transferred. The field
and lemma are removed; what remains is the packaging `toCode`, the surjectivity of
the `M_of` enumeration, and the simulate-or-punt split below.

The *residual* freedom (which `code` to package) is a parameter of `toCode` rather
than a canonical choice. Naming a code that genuinely *simulates* `M` — relating
the code's `evaln` to the machine's `step`-based run — is the open `#226`
obligation, not a landed result.

### The simulate-or-punt split

Given a family `f : Nat → OracleCode Q` (the enumeration the tournament walks),
each index `i` and input `n` falls into exactly one case:

- **DECIDED** — `f i` returns a value within the window `k` (`Simulate f i k n =
  some r`), and by `simulate_mono` that value is *stable* under widening `k`.
- **PUNTED** — `f i` returns nothing within the window (`Simulate f i k n =
  none`); the diagonalization uses a filler input, and `punts_of_le_window` shows
  the punt is *forced* whenever the window does not exceed the input length.
-/

/-- A machine packaged with the program the `M_of` enumeration carries for it.

  **This is a packaging, not a simulation.** The `#224` version of this structure
  carried a field

  `simulates : ∀ k n, evaln k code n = evaln k (M_of (encode code)) n`

  intended to certify that the code reproduces the machine's own bounded run.
  That field was **vacuous** (`#226`): the machine `M` did not occur in it, and by
  `DiagonalEnum.code_encode_ofNat` both sides are the *same expression*, so it was
  `rfl`-true for **any** machine and **any** code. It certified nothing about `M`.
  The field is therefore removed rather than kept as a false certificate.

  A genuine `Machine → Code` agreement — one that *mentions* `M` and relates
  `evaln` on the code to the machine's own `step`-based run — is the open step-3
  obligation (`#226`; see the "open obligation" note below). -/
structure MachineCode (Q : Type) (tm : FinTM2) [DecidableEq tm.Λ] (M : Machine Q tm) where
  code : Nat.Partrec.Code

/-- **The code packaging.** Package a machine together with the program it is
  paired with as an `OracleCode` in the `#154` code-space. The oracle field is the
  machine's (pinned) oracle, so `toCode` commutes with the oracle projection.

  The name is the `#224` one; note that it packages the paired `code` and does
  **not** claim a `Machine → Code` simulation (see `MachineCode`). -/
def toCode {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) : OracleCode Q :=
  { prog := mc.code, oracle := M.oracle }

/-- The packaging preserves the machine's oracle: the packaged code queries
  exactly the oracle the machine was built with. -/
@[simp]
lemma toCode_oracle {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) :
    (toCode mc).oracle = M.oracle :=
  rfl

/-- The packaging carries the machine's paired program. -/
@[simp]
lemma toCode_prog {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) :
    (toCode mc).prog = mc.code :=
  rfl

/-- The "machine side" of the (removed) `#224` agreement: `machineEvaln` is the
  bounded run of the paired program, indexed on the `DiagonalEnum` enumeration.
  It depends on `M` only through the type index of `mc`; it is *not* the machine's
  `step`-based run, which is what a genuine bridge would have to relate to. -/
abbrev machineEvaln {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) (k n : Nat) : Option Nat :=
  Nat.Partrec.Code.evaln k (DiagonalEnum.M_of (Encodable.encode mc.code)) n

/- **The open obligation, stated precisely (`#226`).** The `#224` module claimed
  `toCode_evaln`: that simulating the paired code reproduces the machine's own
  bounded run. The claim it actually proved was `evaln k code n = evaln k
  (M_of (encode code)) n`, true by the `encode`/`ofNat` roundtrip and independent
  of `M`. The honest statement must relate the code's bounded run to the
  machine's `step`-based run, so it *mentions* `M`. That proof — a real
  `Machine → Code` compilation — is not landed, so no `toCode_evaln` is defined
  here. -/

/-- A bounded simulation of the family `f` at index `i` under window `k` on
  input `n` — the per-index decision the tournament reads before deciding to
  simulate or punt. (The name is the `#224` one; it simulates the *code* `(f i).prog`,
  which is not claimed to be a code for any machine.) -/
def Simulate {Q : Type} (f : Nat → OracleCode Q) (i k n : Nat) : Option Nat :=
  Nat.Partrec.Code.evaln k (f i).prog n

/-- **DECIDED case.** The family returns a value `r` within the window `k`. When
  this holds the diagonalization reads `M_i`'s answer: `Simulate f i k n = some r`
  is a genuine (in-window) decision. -/
def Decided {Q : Type} (f : Nat → OracleCode Q) (i k n : Nat) (r : Nat) : Prop :=
  Simulate f i k n = some r

/-- **PUNTED case.** The family returns nothing within the window `k`; the
  diagonalization takes the filler-input branch. -/
def Punted {Q : Type} (f : Nat → OracleCode Q) (i k n : Nat) : Prop :=
  Simulate f i k n = none

/-- **Window stability (`simulate_mono`).** A decision read inside the window is
  stable: widening the window cannot un-decide it. This is what makes the
  `Decided` branch well defined. -/
lemma simulate_mono {Q : Type} {f : Nat → OracleCode Q} {i k₁ k₂ n r}
    (h : Simulate f i k₁ n = some r) (hk : k₁ ≤ k₂) :
    Simulate f i k₂ n = some r := by
  unfold Simulate at h ⊢
  exact Option.mem_def.mp
    (Nat.Partrec.Code.evaln_mono (c := (f i).prog) (n := n) hk (Option.mem_def.mpr h))

/-- A decision returns an element of the program's genuine partial output: the
  in-window answer is not an artifact of the cutoff. -/
lemma simulate_returns {Q : Type} {f : Nat → OracleCode Q} {i k n r}
    (h : Simulate f i k n = some r) :
    r ∈ Nat.Partrec.Code.eval (f i).prog n :=
  (Nat.Partrec.Code.evaln_complete (c := (f i).prog) (n := n)).2 ⟨k, h⟩

/-- **The window must exceed the input length.** A program that returned within
  `k` steps was run on an input `n < k` (Mathlib's `evaln_bound`). Consequence:
  any input at or beyond the window is necessarily punted. -/
lemma simulate_bound {Q : Type} {f : Nat → OracleCode Q} {i k n r}
    (h : Simulate f i k n = some r) : n < k := by
  unfold Simulate at h
  exact Nat.Partrec.Code.evaln_bound (Option.mem_def.mpr h)

/-- Contrapositive: any input at or beyond the window length is necessarily
  punted — the tournament's filler-input branch is *forced*, not chosen. -/
lemma punts_of_le_window {Q : Type} {f : Nat → OracleCode Q} {i k n : Nat}
    (hn : k ≤ n) : Punted f i k n := by
  unfold Punted Simulate
  cases h : Nat.Partrec.Code.evaln k (f i).prog n with
  | none => rfl
  | some r => exact absurd (Nat.Partrec.Code.evaln_bound (Option.mem_def.mpr h)) (not_lt.mpr hn)

/-- **The case split.** Every index/input falls into exactly one branch: either
  the family is decided in-window (returning some `r`), or it is punted. -/
theorem simulate_or_punt {Q : Type} (f : Nat → OracleCode Q) (i k n : Nat) :
    (∃ r, Decided f i k n r) ∨ Punted f i k n := by
  unfold Decided Punted Simulate
  cases h : Nat.Partrec.Code.evaln k (f i).prog n with
  | none => exact Or.inr rfl
  | some r => exact Or.inl ⟨r, rfl⟩

/-- The two branches are mutually exclusive: a decided index is not punted. -/
theorem not_decided_and_punted {Q : Type} {f : Nat → OracleCode Q} {i k n : Nat}
    (h : Punted f i k n) : ¬ ∃ r, Decided f i k n r := by
  rintro ⟨r, hr⟩
  unfold Punted at h
  unfold Decided at hr
  rw [hr] at h
  exact Option.some_ne_none r h

/-!
## The bridge lemma (issue #224, step 3/4) — and its `#226` defect

`docs/STATEMENTS/Relativization.machine-family.md` §2 names step 3's obligation:
every `P_A`/`NP_A` witness of the DEC-028 family is "correctly simulated by the
`M_of` enumeration *and runs at all*" (`∀ i, ∃ k n, Simulate i k n ≠ none`).

**Defect (#226).** The `#224` module claimed to land the `Machine → Code` half
via `toCode_evaln`, resting on the `MachineCode.simulates` field. That field did
not mention the machine `M`, and by `DiagonalEnum.code_encode_ofNat` its two sides
are the *same expression* — so it was `rfl`-true for any machine and any code. The
"bridge" therefore transferred no machine behaviour. The field and the lemma are
removed; the module's honest content is what remains below, and the genuine
`Machine → Code` agreement is an open obligation, not a landed result.

**What *is* proved.** `exists_index_of_machineCode` is a real fact about the
`M_of` enumeration: it is surjective onto codes (`Encodable.encode`/`ofNat` is a
roundtrip on `Code`), so every code has an index. `simulate_at_index` is that same
roundtrip restated — it is **not** a `Machine → Code` bridge, because nothing in it
depends on `M`. `simulate_ne_none_iff` is a genuine statement about the
enumeration's partial semantics (the `#155` D6/O2 split), independent of the
removed field.
-/

/-- **The enumeration is surjective on codes.** Every code has an index in `M_of`
  at which the enumerated program *is* that code. This is a property of the
  `Encodable.encode`/`ofNat` roundtrip on `Nat.Partrec.Code`, **not** a
  `Machine → Code` bridge: the `MachineCode` wrapper contributes only its `code`
  field, and the machine `M` is unused. -/
theorem exists_index_of_machineCode {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) :
    ∃ i, DiagonalEnum.M_of i = mc.code :=
  ⟨Encodable.encode mc.code, DiagonalEnum.code_encode_ofNat mc.code⟩

/-- **The `#224` "half 1b", restated honestly.** At the enumeration index of the
  paired code, `Simulate` returns the same value as `machineEvaln` — but both sides
  are the *same expression* after the `encode`/`ofNat` roundtrip, so this holds for
  every machine and carries no information about `M`. It is kept because
  `exists_deciding_window_of_eval` and downstream callers use the index, not
  because it bridges machines to code. A genuine bridge is the open obligation. -/
theorem simulate_at_index {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) (k n : Nat) :
    Simulate (fun _ => toCode mc) (Encodable.encode mc.code) k n = machineEvaln mc k n := by
  unfold Simulate machineEvaln
  rw [toCode_prog, DiagonalEnum.code_encode_ofNat]

/-- **Half 2 — "runs at all" is exactly halting.** A deciding window exists for
  the family at index `i` on input `n` **iff** the program's partial semantics is
  nonempty there. So the obligation the design doc states as `∃ k n, Simulate i k
  n ≠ none` is a property of the enumerated program's `eval`, not a modelling
  assumption: the diagonalization decides exactly those inputs on which the code
  halts, and punts the rest (`punts_of_le_window`). -/
theorem simulate_ne_none_iff {Q : Type} {f : Nat → OracleCode Q} {i n : Nat} :
    (∃ k, Simulate f i k n ≠ none)
      ↔ ∃ r, r ∈ Nat.Partrec.Code.eval (f i).prog n := by
  constructor
  · rintro ⟨k, hk⟩
    cases h : Simulate f i k n with
    | none => exact absurd h hk
    | some r =>
      exact ⟨r, (Nat.Partrec.Code.evaln_complete (c := (f i).prog) (n := n)).2
        ⟨k, Option.mem_def.mpr h⟩⟩
  · rintro ⟨r, hr⟩
    obtain ⟨k, hk⟩ := (Nat.Partrec.Code.evaln_complete (c := (f i).prog) (n := n)).1 hr
    exact ⟨k, by
      unfold Simulate
      rw [Option.mem_def.mp hk]
      exact Option.some_ne_none r⟩

/-- The `∃ k` direction, stated for a bare code: a program that halts on `n`
  decides at some window of the enumeration. This is the "runs at all" half for a
  code — a property of the code's partial semantics, independent of any machine. -/
theorem exists_deciding_window_of_eval {Q : Type} (c : Nat.Partrec.Code) (A : Oracle Q)
    {n r : Nat} (h : r ∈ Nat.Partrec.Code.eval c n) :
    ∃ k, Simulate (fun _ => (⟨c, A⟩ : OracleCode Q)) 0 k n ≠ none :=
  simulate_ne_none_iff.mpr ⟨r, h⟩

end DiagonalBridge

end Barriers

end PleaNP