import Mathlib
import PleaNP.Computability.Oracle

set_option warningAsError true

/-!
# BGS (b) step 3a: the corrected `Machine → Code` bridge — statement only

**Status.** Statement-only probe (`#229`, step 3a of 4). No proof is attempted
here; the bridge obligation is *rendered* as a `Prop`-valued `def` (the repo's
honest convention for an unproven statement — see `BoundaryProbe.lean` N4–N6),
not carried by a `sorry`. The proof is step 3b.

## Why the `#224` statement was vacuous (`#226`, DEC-029)

The retracted `#224` module carried, on its `MachineCode` structure, the field

```
simulates : ∀ k n, Nat.Partrec.Code.evaln k code n
                 = Nat.Partrec.Code.evaln k (DiagonalEnum.M_of (Encodable.encode code)) n
```

Two independent defects made this assert nothing about the machine `M`:

1. **`M` did not occur.** The field is typed by `code : Nat.Partrec.Code` alone;
   the machine that `MachineCode` was indexed by appears nowhere in the field's
   type. A proof of it therefore transfers no machine behaviour.
2. **Both sides are the same expression.** By `DiagonalEnum.code_encode_ofNat`
   (`M_of (Encodable.encode c) = c`), the right-hand side reduces to the
   left-hand side, so the field is `rfl`-true for **any** machine and **any**
   code. `toCode_evaln` was consequently a proof of `x = x`.

`binder_usage_scan` flags exactly this shape (`vacuous_forall`): a bound name
that does not occur in the body. (Here the offending bound name is absent
entirely — `M` is not even a binder of the field.)

## The honest statement

A genuine `Machine → Code` agreement must relate the code's bounded
`Nat.Partrec.Code.evaln` run to the machine's **own `step`-based run**
(`PleaNP.Oracles.step`), so that `M` occurs load-bearingly. The corrected
statement below does this: the hypothesis `HaltsWithin M w k cfg'` is driven by
`step M` from `initCfg M w`, and the code's bounded run must return exactly the
value `oa cfg'` that decodes the halted configuration's output. Neither side can
be discharged by `code_encode_ofNat`, because `M.decode` and `M.oracle` (fields
of `M`) determine which `cfg'` is reached, and the conclusion is constrained by
that `cfg'`.

## Which landed lemmas the proof (step 3b) will need

- `PleaNP.Oracles.step` / `initCfg` — the machine's real step function and its
  initial configuration (`Computability/Oracle.lean:85`). The bridge must be
  proved against these, not against a re-abstracted `evaln`.
- `StateTransition.EvalsToInTime` and `PleaNP.Oracles.evalsTo_unique_result` —
  bounded reachability, and the determinism lemma that makes the halted endpoint
  unique (so "the" decoded output is well-defined).
- `DiagonalEnum.M_of` / `code_ofNat_encode` / `code_encode_ofNat` — the
  `Nat.Partrec.Code` enumeration the diagonalization walks. Note that
  `code_encode_ofNat` is what *exposed* the `#224` vacuity; the honest proof must
  use it only as an enumeration round-trip, never as the whole content.
- `Nat.Partrec.Code.evaln_complete` (`DiagonalEnum.evaln_mem_eval`) — to pass
  between the bounded `evaln` and the unbounded `eval`, the form the tournament
  reads.
- `DiagonalSyntax.machineEquiv` — the factorisation that localises the oracle and
  `decode` factors, which is where the "detect `P` or punt" modelling choice is
  discharged.

## What is deliberately NOT here

The proof (step 3b), the D6 assembly (step 3c), and any claim that the bridge is
*provable* in this generality. A `Nat.Partrec.Code` is a plain partial-recursive
program with no oracle; simulating an oracle machine whose `oracle`/`decode` are
arbitrary is the actual open obligation, which is why the statement is a target,
not a theorem.
-/

namespace PleaNP

namespace Barriers

namespace BridgeSpec

open PleaNP.Oracles
open Turing

variable {Q : Type} {tm : FinTM2} [DecidableEq tm.Λ]

/-- The machine `M` started on the tape word `w` halts at configuration `cfg'`
  within `k` steps. Defined from `step M` and `initCfg M w`, so `M` occurs
  load-bearingly (contrast the retracted `#224` field, which did not mention its
  machine at all). -/
def HaltsWithin (M : Machine Q tm) (w : List (tm.Γ tm.k₀)) (k : Nat)
    (cfg' : Cfg Q tm) : Prop :=
  Nonempty (StateTransition.EvalsToInTime (step M) (initCfg M w) (some cfg') k) ∧
    cfg'.cfg.l = Option.none

/-- The compiled program paired with the machine it is meant to simulate.

  `ia` maps the machine's input tape word into the code's numeric input (the two
  substrates differ: a `Nat.Partrec.Code` runs on `ℕ`, the machine on a word);
  `oa` decodes a halted configuration's output into the `ℕ` that `evaln`
  returns. Naming both is the bridge's whole content — the `#224` attempt hid
  them by comparing `evaln` to itself. -/
structure MachineCodeBridge (M : Machine Q tm)
    (ia : List (tm.Γ tm.k₀) → Nat) (oa : Cfg Q tm → Nat) where
  /-- The compiled program: a partial-recursive code, the enumeration the
    tournament walks via `DiagonalEnum.M_of`. -/
  code : Nat.Partrec.Code
  /-- The honest simulation field. `M` occurs in the hypothesis through
    `step M` / `initCfg M w`; the conclusion is constrained by the `cfg'` that
    only `M`'s run can produce. -/
  simulates : ∀ (w : List (tm.Γ tm.k₀)) (k : Nat) (cfg' : Cfg Q tm),
    HaltsWithin M w k cfg' →
      Nat.Partrec.Code.evaln k code (ia w) = some (oa cfg')

/-- The bridge obligation, stated as a proposition: *some* code simulates the
  machine `M` under the input encoding `ia` and output decoding `oa`. This is
  the target step 3b must prove (or refute, and re-scope); it is rendered here as
  a `Prop` so the shape is fixed before proof search, without a `sorry`. -/
def BridgeStatement (M : Machine Q tm)
    (ia : List (tm.Γ tm.k₀) → Nat) (oa : Cfg Q tm → Nat) : Prop :=
  Nonempty (MachineCodeBridge M ia oa)

/-- **Statement-only (step 3a), rendered.** The bridge statement holds for a
  machine `M` under the encodings `ia`/`oa`. It is a `def`-valued `Prop`, not a
  proved `theorem`: the real `Machine → Code` compilation against `step M` is the
  open step-3b obligation and is **not** attempted here. -/
def bridge_statement (M : Machine Q tm)
    (ia : List (tm.Γ tm.k₀) → Nat) (oa : Cfg Q tm → Nat) : Prop :=
  BridgeStatement M ia oa

end BridgeSpec

end Barriers

end PleaNP
