# Barrier-check verdict test spec (issue #3; extended #170)

**Status:** 2026-09-30 (run=20260930-1341-u8sg, #170). Executable harness:
`tooling/gates/barrier_check_test.py`; unit tests: `tooling/gates/tests/test_barrier_check_test.py`;
CI wiring: `.github/workflows/ci.yml`; index note: `tooling/gates/README.md`.

## What is covered

The Rung-5 `#barrier_check` elaborator in
`lean/PleaNP/Calculus/BarrierCalculus.lean` logs verdict lines during
compile (via `logInfo`). A regression in the verdicts — a relic that stops
synthesizing, a verdict message rewrite, an instance that stops carrying the
`Relativizing`/`PVsNPShaped` markers — would otherwise pass CI silently (the
build succeeds either way; only the *info lines* change)). The harness asserts
the expected verdict segments appear in the captured build log.

| Declaration | Expected verdict segment |
|---|---|
| `PleaNP.Calculus.thhStatement` | `#barrier_check ...thhStatement: relativizes,` |
| `PleaNP.Calculus.abstractPVsNP` | `#barrier_check ...abstractPVsNP: DEAD` |
| `PleaNP.Calculus.plainRelHeuristic` | `#barrier_check ...plainRelHeuristic: relativizes,` |
| `PleaNP.Calculus.nonRelativizingControl` | `#barrier_check ...nonRelativizingControl: Inconclusive` |
| `PleaNP.Calculus.concreteClassMembership` | `#barrier_check ...concreteClassMembership: DEAD` |
| `PleaNP.Calculus.bgsMetaStatement` | `#barrier_check ...bgsMetaStatement: Inconclusive` |
| `PleaNP.Barriers.Williams.williams_transfer` | `#barrier_check ...williams_transfer: Inconclusive` |
| `PleaNP.Barriers.Williams.NEXP_not_subset_ACC0` | `#barrier_check ...NEXP_not_subset_ACC0: Inconclusive` |
| `PleaNP.Barriers.Williams.williams_lower_bound_compiled` | `#barrier_check ...williams_lower_bound_compiled: Inconclusive` |

Segments end at the verdict keyword (the `logInfo` templates at
BarrierCalculus.lean:276-280 are the source of truth; keep the segments in
sync with them). The log's `info: <file>:<line>:<col>:` prefix and any
dash-family variants are tolerated (folded before matching).

## How CI catches regressions

The "Build clean modules" step pipes its lake output through
`tee /tmp/barcheck.log`;a following step runs the harness on that log and
fails the job if any expected segment is missing. Thus a verdict regression
kills CI — mechanically, with no human eyeball required.

## Drift guard (#170)

The harness only asserts declarations it knows about, so before #170 a new
`#barrier_check <decl>` added to a Lean module compiled green with its verdict
unasserted — a regression in that declaration could never fail the build. Three
Williams-module invocations (`williams_transfer`, `NEXP_not_subset_ACC0`,
`williams_lower_bound_compiled`) were in exactly this state.

`--check-drift [LEAN_ROOT]` closes the hole: it scans every `.lean` file under
`LEAN_ROOT` (default `lean/`), strips comments, finds each `#barrier_check
<ident>` invocation, and fails if the bare identifier is absent from `EXPECTED`.
CI runs it as a separate step (stdlib-only, no Lean toolchain needed). Matching
is by short-name suffix; add the invocation to `EXPECTED` with its verdict
segment when a new check is authored.

 The unit tests
(`tests/test_barrier_check_test.py`,stdlib-only, no Lean, no secrets) cover
the harness logic (all-present pass; missing-verdict fail; dash tolerance;
no-prefix tolerance; file-exit-code mapping) and run in CI alongside the other
gate unit tests.



## Updating when the verdicts change

If a `#barrier_check` verdict message is intentionally rewritten (cosmetic
reword), the expected segment list in `barrier_check_test.py` MUST be updated in
the same commit — exactly the "sync the spec" discipline the repo applies to
`SORRY_TRACKER`/design docs. If a declaration is added/removed, update both
the elaborator's unit-test invocations and the expected list`. The fancy dash
`—` and the wordboundary around the verdict keyword are the only fragile parts; keep
segments short (ending at the keyword) and dash-tolerance makes them robust.

**Cache caveat.** `#barrier_check` info lines print only when the module is
actually compiled. Today CI has no `.lake/build` cache, so the fresh runner
compiles PleaNP modules fresh and the teed log contains the verdicts. If
`.lake/build` caching is ever added to CI,the Build step must force a
recompile of `PleaNP.Calculus.BarrierCalculculus` (e.g. `touch` before
teeing, or switch the harness step to `--run-lake`,which touches first) -
else the harness would see an up-to-date module, and the verdict lines would be
absent.