import PleaNP.Barriers.BGSDiagonal
import PleaNP.Computability.Oracle

set_option warningAsError true

/-!
# BGS (b): the concrete machine family + canonical decode (issue #223, step 2/4)

Implements DEC-028 (`docs/decisions/LOG.md`): the single concrete machine
family the BGS (b) diagonalization enumerates over, and the canonical
length-tagged identity `decode` the v5 word-query substrate uses
(`docs/STATEMENTS/Oracle.v5-repair.spec.md` §3.1).

The family is the two-symbol `Bool` machine with three tapes — input
(`k₀`), output (`k₁`), and a dedicated **query tape** (`queryTape`). The
alphabet is `Γ := fun _ => Bool`, matching the landed v5 substrate
(`OracleSmoke.lean`) and forcing no re-type of a DEC-024-frozen module.

The canonical decode is the identity-on-bits, length-tagged:

    decode w = ⟨w.length, fun i => w.get i⟩

Its load-bearing invariant is that `decode`, restricted to length-`n`
words, is a **bijection** onto the `n`-fiber of the query space
`Query = Σ n, Bits n` (frozen in `BGSDiagonal.lean`). That is what makes
the query-word space *be* the `2^n` space `DiagonalCounting.lean` counts
over, keeping BGS clause (b) faithful (DEC-028 rationale (3)).

Step 3 (`DiagonalBridge.lean`, #224) owns the `Machine → Code` bridge;
this module is substrate only and changes no frozen statement.
-/

namespace PleaNP

namespace Barriers

namespace BGSDiagonal

open Turing

/-- The query-tape index of the family: tape `2`, a peer of input `k₀ = 0`
  and output `k₁ = 1`. The word on this tape is what `decode` consumes. -/
abbrev queryTape : Fin 3 := 2

/-- The BGS (b) machine family: two-symbol (`Bool`) alphabet and three
  tapes (input, output, query). This is the one concrete `FinTM2` shape
  DEC-028 fixes the diagonalization to enumerate over. -/
def familyTM : FinTM2 where
  K := Fin 3
  k₀ := 0
  k₁ := 1
  Γ := fun _ => Bool
  Λ := PUnit
  main := PUnit.unit
  σ := PUnit
  initialState := PUnit.unit
  m := fun _ => TM2.Stmt.halt

/-- The family's query tape carries a word over the finite alphabet
  `Γ queryTape = Bool`; `decode` reads exactly that word. -/
abbrev QueryWord := List (familyTM.Γ queryTape)

/-- The canonical length-tagged identity decode (DEC-028): a word `w`
  decodes to the length-`w.length` bitstring whose `i`-th bit is `w.get i`. -/
def decode (w : QueryWord) : Query :=
  ⟨w.length, fun i => w.get i⟩

/-- The canonical encoding of a bitstring: its own `n` bits as a word.
  This is the query word a family machine writes to the query tape. -/
def encodeBits {n : Nat} (x : Bits n) : QueryWord :=
  List.ofFn x

/-- `encodeBits` produces a length-`n` word. -/
lemma length_encodeBits {n : Nat} (x : Bits n) :
    (encodeBits x).length = n := by
  simp [encodeBits]

/-- The roundtrip `decode ∘ encodeBits = id` on the length-tagged query
  space: decoding the encoded word returns exactly `⟨n, x⟩`. -/
lemma decode_encodeBits {n : Nat} (x : Bits n) :
    decode (encodeBits x) = ⟨n, x⟩ := by
  unfold decode encodeBits
  exact Fin.sigma_eq_of_eq_comp_cast List.length_ofFn (by
    funext i
    simp only [List.get_ofFn]
    congr 1)

/-- **Surjectivity** (the DoD's lemma): every `x : Bits n` is encodable —
  some query word decodes to `⟨n, x⟩`. With `length_encodeBits` and
  `decode_encodeBits` this is the fiber-surjectivity DEC-028 requires. -/
theorem decode_surjective (n : Nat) (x : Bits n) :
    ∃ w : QueryWord, w.length = n ∧ decode w = ⟨n, x⟩ :=
  ⟨encodeBits x, length_encodeBits x, decode_encodeBits x⟩

/-- The fiber bijection: length-`n` query words correspond bijectively to
  `n`-bit strings, so the query-word space per length has exactly `2^n`
  words — one per `x : Bits n`. This is the counting faithfulness the D1
  argument (`DiagonalCounting.lean`) relies on. -/
def fiberEquiv (n : Nat) : Bits n ≃ {w : QueryWord // w.length = n} where
  toFun x := ⟨encodeBits x, length_encodeBits x⟩
  invFun w := fun i => w.1.get ⟨i.1, by have h := w.2; omega⟩
  left_inv x := by
    funext i
    simp [encodeBits]
  right_inv w := by
    obtain ⟨w, hw⟩ := w
    apply Subtype.ext
    subst hw
    simp only [encodeBits]
    exact List.ofFn_get w

end BGSDiagonal

end Barriers

end PleaNP
