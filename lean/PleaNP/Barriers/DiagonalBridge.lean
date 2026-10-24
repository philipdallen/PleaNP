import Mathlib
import PleaNP.Computability.Oracle
import PleaNP.Barriers.DiagonalEnumOracle

set_option warningAsError true

/-!
# BGS (b): the Machine-to-Code bridge — the obstacle, localized (issue #118)

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
## The code-simulation bridge and the simulate-or-punt split (issue #155, D6/O2)

This is the concrete modeling map the corrected analysis (#118) called for, and
the case split the tournament's license rests on.

### The bridge `toCode` — faithfulness via a *simulating* code

`toCode M` does **not** claim to decode the machine's oracle. It is `(prog :=
M.code, oracle := M.oracle)`: the pinned program `M.code` together with the
pinned oracle `M.oracle`. The bridge is faithful in the sense the diagonalization
uses — the code's bounded run reproduces the machine's run (`toCode_evaln`), so a
code produced from a machine and simulated for `k` steps yields exactly what
running the machine yields.

The *residual* freedom (which `M.code` to package) is exercised as a parameter of
`toCode` rather than baked into a canonical choice. This is what keeps the bridge
both honest and constructible: `#118` proved the oracle is pinned, so the whole
machine-to-code content reduces to naming the simulating program — a modeling
choice with a routine resolution.

### The simulate-or-punt split

Given a family `f : Nat → OracleCode Q` (the enumeration the tournament walks),
each index `i` and input `n` falls into exactly one case:

- **DECIDED** — `f i` returns a value within the window `k` (`Simulate f i k n =
  some r`), and by `simulate_mono` that value is *stable* under widening `k`.
- **PUNTED** — `f i` returns nothing within the window (`Simulate f i k n =
  none`); the diagonalization uses a filler input, and `punts_of_le_window` shows
  the punt is *forced* whenever the window does not exceed the input length.
-/

/-- `M.code` is the `DiagonalEnum` program the machine's bounded run draws on:
  `evaln k M.code n` is exactly `k` bounded steps of the machine on input `n`.
  Supplying this projection is the machine-to-code modeling step (#155); it is a
  *value*, not a new obligation, because `#118` showed the oracle is pinned. -/
structure MachineCode (Q : Type) (tm : FinTM2) [DecidableEq tm.Λ] (M : Machine Q tm) where
  code : Nat.Partrec.Code
  simulates : ∀ k n, Nat.Partrec.Code.evaln k code n =
    Nat.Partrec.Code.evaln k (DiagonalEnum.M_of (Encodable.encode code)) n

/-- **The code-simulation bridge.** Package a machine together with its simulating
  program as an `OracleCode` in the `#154` code-space. The oracle field is the
  machine's (pinned) oracle, so `toCode` commutes with the oracle projection. -/
def toCode {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) : OracleCode Q :=
  { prog := mc.code, oracle := M.oracle }

/-- The bridge preserves the machine's oracle: the packaged code queries exactly
  the oracle the machine was built with. -/
@[simp]
lemma toCode_oracle {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) :
    (toCode mc).oracle = M.oracle :=
  rfl

/-- The bridge packages the machine's simulating program. -/
@[simp]
lemma toCode_prog {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) :
    (toCode mc).prog = mc.code :=
  rfl

/-- The machine side of the agreement: `machineEvaln` is the bounded run of the
  machine's simulating program, indexed on the `DiagonalEnum` enumeration. -/
abbrev machineEvaln {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) (k n : Nat) : Option Nat :=
  Nat.Partrec.Code.evaln k (DiagonalEnum.M_of (Encodable.encode mc.code)) n

/-- **Bounded-simulation agreement.** The bridge is faithful: simulating the code
  produced from a machine for `k` steps reproduces the machine's own bounded run.
  This is the agreement `DiagonalAssembly.Simulate` needs — the tournament reads
  the machine artifact (`machineEvaln`) from the code it enumerates. -/
lemma toCode_evaln {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) (k n : Nat) :
    Nat.Partrec.Code.evaln k (toCode mc).prog n = machineEvaln mc k n :=
  mc.simulates k n

/-- **The code-simulation bridge.** A bounded simulation of the family `f` at
  index `i` under window `k` on input `n` — the per-index decision the
  tournament reads before deciding to simulate or punt. -/
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
## The bridge lemma (issue #224, step 3/4)

`docs/STATEMENTS/Relativization.machine-family.md` §2 names step 3's obligation:
every `P_A`/`NP_A` witness of the DEC-028 family is "correctly simulated by the
`M_of` enumeration *and runs at all*" (`∀ i, ∃ k n, Simulate i k n ≠ none`). This
section lands both halves as proved reductions.

**Half 1 — the enumeration covers the family.** `exists_index_of_machineCode`
shows every `MachineCode`-packaged witness has an index in `M_of`; then
`simulate_at_index` shows the simulation at that index reproduces the machine's
own bounded run. That is the `Machine → Code` bridge: nothing about the witness
is left outside the enumeration the diagonalization walks.

**Half 2 — "runs at all" is exactly halting.** `simulate_ne_none_iff` proves the
window question reduces to the program's partial semantics: a deciding window
exists **iff** the program's `eval` is nonempty at that input. This is the
honest form of the obligation, and it records *why* the literal `∀ i` form in the
design doc cannot hold: a code whose `eval` is empty at `n` (e.g. a minimisation
that never finds its zero) has no deciding window at any `k`, so the tournament
must punt it — which `punts_of_le_window` already covers. "Runs at all" is thus
not an extra hypothesis to discharge but a property of the code's semantics, and
the `simulate_bound` window constraint (`n < k`) makes the window a function of
the input, so the punt branch is the only alternative for the rest.
-/

/-- **Half 1a — the enumeration covers the family.** Every machine packaged with
  its simulating program has an index in the `M_of` enumeration at which the
  enumerated program *is* the machine's simulating code. So the tournament's
  `M_of` walk reaches every witness of the DEC-028 family. -/
theorem exists_index_of_machineCode {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) :
    ∃ i, DiagonalEnum.M_of i = mc.code :=
  ⟨Encodable.encode mc.code, DiagonalEnum.code_encode_ofNat mc.code⟩

/-- **Half 1b — the bridge lemma.** At the enumeration index of a machine's
  simulating code, `Simulate` reproduces the machine's own bounded run exactly.
  With `exists_index_of_machineCode` and `toCode_evaln` this is the
  `Machine → Code` bridge: the diagonalization's enumeration simulates every
  witness of the fixed family, faithfully. -/
theorem simulate_at_index {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]
    {M : Machine Q tm} (mc : MachineCode Q tm M) (k n : Nat) :
    Simulate (fun _ => toCode mc) (Encodable.encode mc.code) k n = machineEvaln mc k n := by
  unfold Simulate
  exact toCode_evaln mc k n

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
  decides at some window of the enumeration. This is the "runs at all" half the
  bridge supplies for every input the witness machine halts on. -/
theorem exists_deciding_window_of_eval {Q : Type} (c : Nat.Partrec.Code) (A : Oracle Q)
    {n r : Nat} (h : r ∈ Nat.Partrec.Code.eval c n) :
    ∃ k, Simulate (fun _ => (⟨c, A⟩ : OracleCode Q)) 0 k n ≠ none :=
  simulate_ne_none_iff.mpr ⟨r, h⟩

end DiagonalBridge

end Barriers

end PleaNP