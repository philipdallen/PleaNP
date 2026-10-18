# Lower-Bound Compiler — accept-path test spec (issue #109)

**Status:** 2026-09-19 (run=20260919-0920-p8k2). Frozen spec for the
**accept path** of `#lower_bound_compile`. Written per #109's DoD: "A test
spec describing the accept-path coverage the compiler needs ... The test
itself lands once #98 supplies a contract proof; until then the spec is the
deliverable."

**Companion docs:** `docs/STATEMENTS/LowerBoundCompiler.design.md` §2 (the
input contract), `lean/PleaNP/Barriers/LowerBoundCompiler.README.md`
(usage + honest status), `lean/tests/LowerBoundCompilerGuards.lean` (the
four *rejection* guards, already pinned), `docs/STATEMENTS/BarrierCheckVerdicts.spec.md`
(the sibling spec whose sync discipline this one copies), #80 (parent),
#98 (the blocking contract proof).

---

## 1. What the accept path is, and why it is currently unreachable

`#lower_bound_compile <contract> as <name>` performs three steps
(`lean/PleaNP/Barriers/LowerBoundCompiler.lean`):

1. `assertContractShape` — the contract's type, after `whnf`, must be
   `SubExpCircuitSATT`;
2. `assertNoSorry` — the contract's axiom closure must not contain `sorryAx`
   (anti-requirement "no asserted runtime");
3. `emitClaim` — emit `def <name> : Prop := NEXP_not_subset_ACC0` and log
   the emitted name, the `PleaNP`-local dependency closure, and the axiom
   closure.

Steps 1-2 are *tested today* for the rejection direction
(`lean/tests/LowerBoundCompilerGuards.lean`: wrong shape, `sorryAx`,
missing, shadowing — each a `#guard_msgs` build-time assertion). Step 3 —
the **accept** direction — has **no test coverage**, because it needs a
`<contract>` that *passes* both guards, i.e. a `sorry`-free proof of
`SubExpCircuitSATT`.

**No such proof exists.** `SubExpCircuitSATT`
(`PleaNP.Barriers.Williams`) is an existential
`∃ (D) (c), (∀ n C, D C = true ↔ CircuitSAT C) ∧ (∀ n C, acc0SatSteps C ≤ 2 ^ (n ^ c))`.
Its correctness half is discharged by `acc0SatBrute_correct` (#89 Pass 2);
its **sub-exponential half** is the tracked `acc0SatSubExpBound` gap — the
ACC⁰-structure packing argument (Shah–Shetty-style Good-SAT) tracked by
**#98**. While that half is open, the accept path is *unreachable*: any
declaration of type `SubExpCircuitSATT` available today either carries
`sorryAx` (rejected by guard 2) or does not exist. Asserting the accept
emission today would therefore require exactly the dishonest input the
compiler refuses. **The spec is the deliverable, not the runnable test.**

## 2. The expected emission (frozen log shape)

Three `logInfo` calls produce the emission report (see `emitClaim`,
`reportClosure`, `reportAxioms` in the elaborator — **those templates are
the source of truth; keep the segments below in sync with them**). For the
full path the `label` is `full`:

| # | Log line (template) | Stability |
|---|---|---|
| 1 | `#lower_bound_compile [full] emitted '<name>'.` | **assert** — short, byte-stable |
| 2 | `#lower_bound_compile [full] dependency closure: [<PleaNP-local closure>, … (+N more)]` | **tolerant** — multi-line, order-dependent, cap-dependent; assert *containment* of key names only |
| 3 | `#lower_bound_compile [full] axioms: [<sorted axiom names>]` | **assert** — short, sorted, stable |

**Why line 2 is asserted tolerantly.** `reportClosure` renders an `Array Name`
via its `ToString` (one name per line, comma-separated, capped at 24 with an
`… (+N more)` suffix). Its contents follow the *definitional* dependency
graph, which legitimately shifts when any referenced `PleaNP` definition is
refactored — a strict full-string `#guard_msgs` would then fail for reasons
unrelated to the accept path. The spec therefore pins:

- **exact**: the emitted-name line and the axioms line;
- **contained**: the closure must mention at least
  `PleaNP.Barriers.Williams.NEXP_not_subset_ACC0` (the claim it emits) and
  the `PleaNP.Circuits` anchors it rests on (`BoolGate`, `CircuitFamily`,
  `IsACC0`).

The **axioms line is the load-bearing assertion**: it is the machine-checked
"no asserted runtime" guarantee made visible at the emission site — the
accept path must emit a claim whose closure is inside the standard Mathlib
set (`propext`, `Classical.choice`, `Quot.sound`) and **never** `sorryAx`.

### Calibration against today's reachable path

The **conditional** path (`#lower_bound_compile_cond`, the honest shape
while #98 is open) exercises the same three `logInfo` calls with
`label = conditional`. Its observed output on the current tree is the
calibration baseline for the templates above:

```
info: PleaNP/Barriers/LowerBoundCompiler.lean:236:0: #lower_bound_compile [conditional] emitted 'PleaNP.Barriers.Williams.williams_lower_bound_compiled'.
info: PleaNP/Barriers/LowerBoundCompiler.lean:236:0: #lower_bound_compile [conditional] dependency closure: [PleaNP.Barriers.Williams.williams_lower_bound_compiled,
 PleaNP.Barriers.Williams.NEXP_not_subset_ACC0,
 … , … (+19 more)]
info: PleaNP/Barriers/LowerBoundCompiler.lean:236:0: #lower_bound_compile [conditional] axioms: [Classical.choice, Quot.sound, propext]
```

So the accept-path test asserts the *same three line shapes* with
`[full]` in place of `[conditional]` and the emitted name being the
`as <name>` argument. The conditional emission is verified today in the
clean-module build (`#lower_bound_compile_cond williams_lower_bound_compiled`
in `LowerBoundCompiler.lean`), which is why only the accept-specific
difference — the `[full]` label plus `<name>` — needs a new test.

## 3. The test to land when #98 supplies the contract

The runnable test lives in the `tests` lib (not the clean build set) so a
future `sorry`-based fixture cannot leak into the prove-stage hygiene scan.
When #98 lands a zero-`sorry` proof of `SubExpCircuitSATT` under (say)
`PleaNP.Barriers.Williams.acc0SatSubExpBound_proved`, land
`lean/tests/LowerBoundCompilerAcceptPath.lean (planned)` as:

```lean
import PleaNP.Barriers.LowerBoundCompiler

set_option warningAsError true

/-!
# Lower-Bound Compiler — accept-path test (issue #109)

Pins the accept emission of `#lower_bound_compile <contract> as <name>`
once a `sorry`-free `SubExpCircuitSATT` proof exists (#98). Mirrors
`lean/tests/LowerBoundCompilerGuards.lean`, which pins the rejections.
-/

namespace PleaNP
namespace Barriers
namespace Williams

/--
info: #lower_bound_compile [full] emitted 'PleaNP.Barriers.Williams.acceptPathClaim'.
-/
#guard_msgs (info) in
#lower_bound_compile acc0SatSubExpBound_proved as acceptPathClaim

-- The emitted claim is the frozen lower bound (definitional shape check).
example : acceptPathClaim = NEXP_not_subset_ACC0 := rfl

-- The emitted claim carries no `Relativizing` instance: Inconclusive
-- (the expected non-relativizing classification).
#barrier_check acceptPathClaim

end Williams
end Barriers
end PleaNP
```

**Wiring on landing** (all three are required, in the same commit):

1. add `tests.LowerBoundCompilerAcceptPath` to the `roots` list in **both**
   `lean/lakefile.lean` and the root `lakefile.lean`
   (`tooling/gates/lakefile_sync_check.py` fails CI if they drift);
2. the axioms assertion (§2 line 3) is added as a second `#guard_msgs`
   block matching `[full] axioms: [Classical.choice, Quot.sound, propext]`
   (or the exact closure #98's proof yields — pin *what the machine
   reports*, never a wish);
3. the closure containment check (§2 line 2) is a plain `guard_msgs`
   assertion or a small `tooling/gates/` harness if the multi-line
   rendering makes `#guard_msgs` brittle.

## 4. What this spec deliberately does *not* do

- **No `sorry`-carried fixture.** A fixture with `sorry` would be rejected
  by guard 2 by design; using it to "exercise" the accept path would assert
  the opposite of the anti-requirement. The guards test already covers that
  input (`rejectedSorry`).
- **No synthesis of a fake contract.** Any locally-constructed term of type
  `SubExpCircuitSATT` would have to discharge the sub-exponential half —
  precisely the open mathematics. A "test contract" declared as an `axiom`
  or a `sorry` is the dishonesty the compiler exists to reject.
- **No weakening of the emission to `Prop`-valued placeholder.** The
  emission is already a named `Prop` (the honest shape while the transfer
  proof is open); the accept test must assert *that* emission, not a
  different one.

## 5. Sync discipline

If `emitClaim` / `reportClosure` / `reportAxioms` log templates are
intentionally reworded, the segments in §2 (and the `#guard_msgs` blocks in
§3, once landed) MUST be updated in the same commit — the same rule
`docs/STATEMENTS/BarrierCheckVerdicts.spec.md` applies to the Rung-5
verdict harness. If the emission is ever upgraded from `def` to `theorem`
(when the transfer proof lands), the emitted-name line changes to the
declaration keyword's report and this spec's §2 table must be updated with
it.

---

_Last updated: 2026-09-19 (issue #109, deliverable = this spec). The
runnable `lean/tests/LowerBoundCompilerAcceptPath.lean (planned)` lands with #98's
`SubExpCircuitSATT` proof; the accept path is otherwise unreachable by
design, and asserting it today would require a dishonest contract._
