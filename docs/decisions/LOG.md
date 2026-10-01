# Decision log

Chronological record of design decisions. Append-only. Format: `### DEC-0XX` with Date, Status, Scope, Decision, Rationale.

---

### DEC-001

**Date:** 2026-08-18
**Status:** Active
**Scope:** Project structure
**Decision:** PleaNP is a monorepo with a clean, extractable `lean/` lake project, a `tooling/` Python layer, and a `docs/` spec layer.
**Rationale:** The three layers need version alignment (retrieval reads Lean state, gates run against Lean definitions). Monorepo avoids cross-repo coordination overhead at this stage. The `lean/` tree is self-contained so it can be extracted for a Mathlib PR without carrying Python dependencies. The split-pain-later principle: start monorepo, split only when pain demands.

---

### DEC-002

**Date:** 2026-08-18
**Status:** Active
**Scope:** Naming
**Decision:** Project-specific declarations live under the `PleaNP.*` namespace, not `Complexity.*`.
**Rationale:** `Complexity` is being actively designed by the Mathlib community (see `docs/UPSTREAM_TRACKING.md`). Claiming it would conflict with upstream and misrepresent PleaNP's role — we formalize barriers, not complexity classes. The `PleaNP` namespace is honest about scope and avoids collisions.

---

### DEC-003

**Date:** 2026-08-18
**Status:** Active
**Scope:** Computational model
**Decision:** PleaNP imports P, NP, and polynomial-time reductions from upstream Mathlib rather than defining them locally. Oracle machines are defined locally.
**Rationale:** 3–4 active Mathlib efforts are contesting the computational-model design (tracked in `docs/UPSTREAM_TRACKING.md`). Building our own would mean picking a side in an open debate and duplicating substrate work. None of the upstream efforts provide oracle machines, which relativization requires — so that is ours regardless of which model lands.

---

### DEC-004

**Date:** 2026-08-18
**Status:** Active
**Scope:** Integrity architecture
**Decision:** Statement formalization and proof search are isolated in separate pipelines. The integrity gates (statement-freeze, model-consistency, statement-fidelity, read-back, non-triviality, hygiene) run before any proof search.
**Rationale:** The failure audit (`docs/FAILURE_AUDIT.md`) shows the #1 failure mode of claimed P vs NP formalizations is formalizing the wrong statement and trusting the green checkmark (Pattern A). The structural fix is to make it impossible for the same pipeline to both define the statement and search for its proof. This is the project's most important design contribution.

---

### DEC-005

**Date:** 2026-08-18
**Status:** Active
**Scope:** Relationship to Maith
**Decision:** PleaNP is a sibling project to Maith, not a submodule or dependency. PleaNP may reference Maith's findings (notably H6, the retrieval hypothesis) as they firm up, but does not depend on Maith.
**Rationale:** Maith is a representation-research project with open hypotheses; PleaNP is a formalization + integrity project. Entangling them now would couple an open experiment to a build pipeline. The dependency direction is one-way: PleaNP may cite Maith conclusions; Maith does not depend on PleaNP.

---

### DEC-006

**Date:** 2026-08-18
**Status:** Active
**Scope:** Machine-specific configuration
**Decision:** Machine-specific configuration (local Lean toolchain paths, build-server connection details, SSH/access mechanics) is kept out of the public repo, in a gitignored `AGENTS_LOCAL.md` that is referenced but never committed.
**Rationale:** The public repo must be a clean, portable, analyzable artifact. Local setup details are environment-specific and not of public interest. This follows the Maith precedent (`AGENTS_LOCAL.md` pattern).

---

### DEC-007

**Date:** 2026-08-18
**Status:** Active
**Scope:** Build workflow
**Decision:** The Lean build runs on a local machine (not in this authoring environment). The authoring environment maintains the source of truth (the repo); build feedback comes via the local toolchain.
**Rationale:** The authoring environment lacks a Lean toolchain and is ephemeral (reinstalls would be painful, especially Mathlib). A hybrid model — source-of-truth here, build-server local — keeps the repo portable while maintaining a fast edit→compile→goal-state feedback loop. Machine specifics are per DEC-006.


---

### DEC-008

**Date:** 2026-08-18
**Status:** Active
**Scope:** Computational model choice (Rung 2 local piece)
**Decision:** Oracle.lean is built against Mathlib core `Turing.TM1` (PostTuringMachine.lean) as a partial prototype, with a `StepCount` typeclass interface isolating the step-counting dependency. The complexity classes P^A and NP^A are NOT defined yet — they require the step-counting layer that core TM1 lacks (GAP_AUDIT section 1). The `StepCount` interface means when upstream step counting lands (#35366 runN, #33132 EvalsToInTime, or complexitylib reconciliation), only the counting glue changes — not the Oracle type, Cfg, Machine, or step definitions.
**Rationale:** complexitylib was tested and does NOT reconcile under v4.31.0 (23/4033 modules fail with Mathlib API drift; see UPSTREAM_TRACKING section 6). No upstream P/NP model has landed in Mathlib core. Core Turing.TM1 is present in Mathlib v4.31.0 and provides the machine model (Stmt, Cfg, step) needed to define the oracle-machine substrate, but lacks step counting — so the prototype is labeled "Substrate confirmed (partial — oracle machine only; P^A/NP^A blocked on step counting)." This follows decision rule 4 (UPSTREAM_TRACKING): record the chosen model so the next agent knows why TM1 was chosen and that the interface exists to swap it.


---

### DEC-009

**Date:** 2026-08-18
**Status:** Active
**Scope:** Build/CI hygiene enforcement
**Decision:** Hygiene is enforced via (1) per-file `set_option warningAsError true` pragmas in all PleaNP .lean files (making `sorry` a hard build error), and (2) a CI workflow (`.github/workflows/ci.yml`) that runs `lake build` + the hygiene scanner on every push/PR to main. The per-file pragma was chosen over a package-level `moreLeanArgs` flag because the latter caused "unknown configuration option" errors in lake v4.31.0 (the `warningAsError` option needs to be registered by Lean's stdlib, which loads after `-D` parsing). The per-file approach scopes unambiguously to PleaNP files only (not Mathlib), per the spec's section 3 caveat. `lake exe lint` is not available in Mathlib v4.31.0; a `#lint` test file is the fallback path (not yet wired).
**Rationale:** Makes Gate 6 Tier 1 structural (CI-gated) rather than aspirational. A `sorry`-laden PR now fails CI. This catches mechanical failures (sorry, axioms) but not semantic ones (wrong statement, vacuity) — those remain Gates 1-5. See `docs/STATEMENTS/HygieneEnforcement.spec.md`.


---

### DEC-010

**Date:** 2026-08-18
**Status:** Active - Option B chosen (core TM2ComputableInTime, no dependency change)
**Scope:** Step-counting substrate for oracle complexity (P^A / NP^A)

**Decision:** This DEC records the architectural fork in how PleaNP obtains the step-counting layer needed to define P^A and NP^A (the complexity classes the relativization barrier requires). Three options are laid out; the user picks one, and the local agent records the choice and executes.

**Context:** Oracle.lean (DEC-008) is built against core Turing.TM1, which has no step counting. The StepCount typeclass interface isolates this dependency. The question is what instantiates StepCount:

**Option A — Pin v4.30.0, import complexitylib**
- complexitylib (Schlesinger) provides P, NP, BPP, PSPACE, Cook-Levin, a circuit model, Fourier analysis, and multi-tape TMs with step counting. All available today.
- complexitylib is pinned to Lean v4.30.0 / Mathlib v4.30.0. It does NOT compile under v4.31.0 (23 of 4033 modules fail with Mathlib API drift — verified empirically). Under v4.30.0 (its native toolchain), it builds cleanly — no re-verification needed; the failures were v4.31.0-only.
- Pro: unblocks the critical path immediately — P/NP/reductions/Cook-Levin/circuits/step-counting all available. P^A/NP^A, the relativization statement, and a chunk of Rung 4 become runnable now.
- Con: PleaNP (and the sibling maith project) must downgrade to v4.30.0, behind Mathlib core. Accepts a non-Mathlib-core dependency (Apache 2.0, importable as a git dependency — allowed by UPSTREAM_TRACKING rule 3). When a v4.31.0+ complexitylib release lands or #35366 lands, bump back up — the StepCount interface makes this surgical.
- Verdict: highest unblock, highest cost (toolchain downgrade + non-core dependency).

**Option B — Use core TM2ComputableInTime (no dependency change)**
- Mathlib core (v4.31.0) already has a time-bounded computation framework: TM2ComputableInTime (in Mathlib/Computability/TuringMachine/Computable.lean) bundles a TM2 with a time: Nat -> Nat function and a proof it outputs f in at most time(input.length) steps. TM2ComputableInPolyTime is the polynomial-time variant (time: Polynomial Nat). The underlying step-counted relation is TM2OutputsInTime, built on EvalsToInTime (in StateTransition.lean), which tracks a steps count with a steps_le_m proof and has refl/trans (additive step counting).
- A StepCount instance can be written against TM2ComputableInTime's time field, without waiting for #35366's runN or importing complexitylib.
- Pro: stays on core Mathlib, no toolchain change, no external dependency. Consistent with DEC-003 (import, dont define) spirit.
- Con: this is a TM2 (multi-tape) function-computability framing (computing f: alpha -> beta in time), not a language-decision framing with a clean runN counter. Requires recomposing Oracle.lean against TM2 instead of TM1, and bridging from function-computability to language-decision (deciding L: Set alpha). More instance-writing work than Option A, but unblocked now.
- Verdict: conservative, no dependency change, more local work.

**Option C — Local throwaway step counter (stopgap)**
- The local agent writes a minimal fuel-based counter to instantiate StepCount, marked temporary. Unblocks statement-freeze (Gate 1 anchor) for the relativization statement without unblocking the proof.
- Pro: cheapest, fastest, no dependency or toolchain change.
- Con: unblocks only statement-freeze, not proof. The counter is throwaway and will be replaced when a real step-counting substrate lands.
- Verdict: cheapest stopgap, least ambitious.

**Rationale for recording this as a DEC:** The choice changes the project's dependency posture (A: non-core dependency + toolchain downgrade; B: stay on core, more local work; C: stopgap only). This is a genuine architectural fork — the kind the decision log exists for. The user picks; the local agent records the choice and executes.


# DEC-011 entry (to append to docs/decisions/LOG.md)

### DEC-011

**Date:** 2026-08-18
**Status:** Active
**Scope:** Validation discipline and the meta-lesson on honest scaffolding

**Decision:** Adopt a validation-suite requirement for all definitional modules. No definition reaches "frozen" status without compiling a quorum of must-prove lemmas, must-refute lemmas, and smoke tests. Introduce a status ladder (typed → validated → frozen) and forbid the word "anchor" for anything below frozen. Add `binder_usage_scan.py` (Gate 7) as a Tier-1 lethality check. Add a red-team pass on definitions before proving theorems from them. Fix CI staging so `warningAsError` doesn't self-defeat (render-stage vs prove-stage).

**Rationale (the meta-lesson):** The project's `FAILURE_AUDIT.md` Pattern A is usually told as a story about dishonest formalizers editing statements until they compile. The project's own first deliverable showed the more common, harder case: honest scaffolding that compiles, is documented as partial, and is still semantically empty. The v2 Oracle.lean and OracleComplexity.lean had three flaws (DecidesInTime vacuously satisfiable, oracle inert, NP_A certificate vacuous) that passed all Tier-1 scanners (Gate 5 vacuity, Gate 6 hygiene, Gate 2 model-consistency) because the flaws were structural, not syntactic. The defense isn't more honesty checks; it's behavioral evidence, demanded per definition, before anything is allowed to be called an anchor.

The three flaws were:
- **Flaw A:** `DecidesInTime` had no `EvalsToInTime` reachability — the time bound, input encoding, and machine were unused. `P_A` degenerated to "all languages."
- **Flaw B:** `step` delegated to `FinTM2.step` without branching on `queryLabel`. The oracle was inert — `P^A = P^B` for all A, B.
- **Flaw C:** `NP_A` wrapped the whole-language `DecidesInTime` inside `∃ y` — the certificate was vacuous. `NP^A ≈ P^A` by construction.

All three would have been caught by:
1. A must-refute lemma: "P_A A ≠ univ" (countability argument)
2. A smoke test: a machine that queries the oracle and produces different outputs for different oracles
3. A binder-usage scan: flagging unused parameters (`t`, `ea`, `M` in DecidesInTime) and dead binders (`y` absent from its conjunct in NP_A)

The v3 fix (commit `5fd85c6`) addresses the three flaws: step branches on the oracle answer, DecidesInTime references the real step function, NP_A uses a per-input AcceptsInTime predicate. But the process lesson — that behavioral evidence must be demanded per definition — is the lasting fix, recorded here.

**See also:** `docs/VALIDATION_SUITE.md` (the full validation requirements), `tooling/gates/binder_usage_scan.py` (Gate 7), the harsh review (2026-08-18).

### DEC-014 (was DEC-012 on dev — renumbered to resolve a DEC-number collision with the roadmap-expansion DEC-012 on main, merged 2026-09-06)

**Date:** 2026-08-21
**Status:** Active (deferred - post-v4 hardening)
**Scope:** Oracle-machine step semantics (Oracle.lean)

**Decision:** Record a known design gap in Oracles.step: the label
distinctness of queryLabel / yesLabel / noLabel is unenforced.

**The gap:** step checks `if l = M.queryLabel` BEFORE dispatching to the
machine program. If a machine sets `queryLabel = yesLabel` (or
`noLabel`), the oracle answer routes execution to that label, and the
NEXT step consults the oracle again at the same label rather than
running the program there. The query stack was already popped, so the
re-query hits an empty k0 stack and the machine halts (none) at the
post-query label instead of executing the intended branch. Verified
behaviorally: a degenerate Machine with `queryLabel = yesLabel` stops
after 2 steps with `= none`.

**Why deferred:** The fix adds `yesLabel != queryLabel` and
`noLabel != queryLabel` as Machine hypotheses (or fields), which threads
two inequalities through every Machine construction site (including the
smoke test). That is a real refactor, out of scope for the v4-completion
pass and worth its own review. The P_A/NP_A theorems do not rely on the
gap (the smoke machine uses three distinct labels), so this is
hardening, not a correctness fix for anything already proved.

**See also:** lean/PleaNP/Computability/OracleSmoke.lean (the degenerate
machine is the witness that the gap is real).

---

---

### DEC-012

**Date:** 2026-09-06
**Status:** Active
**Scope:** Roadmap expansion — three new target components(priority order: Barrier Calculus, Anchor Object, Lower-Bound Compiler).

**Decision:** Adopt the three components as new rungs of the ladder, with rung numbers in `docs/ROADMAP.md`: **Rung 5 — Barrier Calculus** (`Relativizing` typeclass + `#barrier_check` elaborator + THH unit test —the crown jewel — negative-space specification turned into a typechecking question); **Rung 6 — Anchor Object** (machine-checked P/NP model-equivalence across ≥2 upstream formalizations + Levin universal search rendering `P_eq_NP_iff` as an explicit `#eval`-able term); **Rung 8 — Lower-Bound Compiler** (Williams' transfer theorem as a Lean elaborator emitting verified `NEXP ⊄ C` from a verified CircuitSAT algorithm + runtime bound — lower priority than #1, not blocking — under `PleaNP.Circuits`). Former rungs are renumbered(7 Graded benchmark, 9 AI proof-search loop;, 10 Open problems below P vs NP;, 11 Novel barrier-evasion arguments). Existing out-of-scope boundaries unchanged: still not claiming to resolve P vs NP, still deferring P/NP's base definition to upstream Mathlib. The `lean/` tree stays the sole first-class code artifact.

**Levin-search / decision-gap item(logged as a scoped open lemma, NOT a blocker):** Extending the Anchor Object from the *search* version(Levin universal search,`#eval`-able term) to the *decision* version(`P_eq_NP_iff`)as a decision problem needs **(1) self-reducibility** of the search problem, and **(2) a Hutter-style proof-search wrapper** that turns a bounded search into a decision. Neither is in scope of the current rung's "done" definition; both are formulable as a single scoped, publishable lemma as soon as one base computational model lands upstream. Cite this entry when the search⟶decision gap is discussed, so it isn't glossed over nor silently treated as done.



**Rationale:** The project's core bet is negative-space specification: formalize the constraints a proof must satisfy, not the proof itself. Confirmed as a genuine gap — no proof assistant has formalized these barriers; Coq/Isabelle Cook–Levin formalizations(2021/2023) stalled with no barrier follow-through precisely because they had no demand-pull artifact. `#barrier_check` *is* that artifact — every future claimed-proof triage run creates the pull. The three components are independently valuable and prioritized by leverage(5:the demand-pull device itself; 6: robust statement; 8:the widest eventual force-multiplier, but non-blocking).


---

### DEC-013

**Date:** 2026-09-06
**Status:** Active — Plan B verified green 2026-09-06 (CI run on `459d38c`: success ~2 min). **Plan A (Codespace) is optional/dormant**: the owner works from the chat interface with OpenHands agents; the devcontainer files are kept for future human-interactive days but nothing is blocked on them (agent bootstrap recipe in AGENTS.md "Build and test"). — Plan B (CI build oracle) and Plan A (devcontainer) landed 2026-09-06 (`55329e6`, `68f3ba1`; verified green in-sandbox). CI now gates on the clean modules (PleaNP.Basic + PleaNP.Calculus.BarrierCalculus) with a Mathlib olean cache-restore step, because the full-tree `lake build` fails on the pre-existing v3 Oracle.lean debt (see docs/SORRY_TRACKER.md); widen back to `lake build` when the v4 repair lands. The devcontainer (`.devcontainer/`) provides the warm browser environment; the only human action remaining is the one-time "create a Codespace" click (and any later quota decisions). **Remaining blocker:** the GitHub account has a billing lock — Actions jobs report "The job was not started because your account is locked due to a billing issue" and Codespace creation returns HTTP 500; not automatable with the available tokens (no billing/admin scope). Owner: resolve billing in GitHub Settings → Billing, then re-run last CI and create the Codespace once (checklist: docs/ACTIVATION_CHECKLIST.md).
**Scope:** Persistent toolchain strategy (Lean 4 + Mathlib) without the local M4 box or from-scratch sandbox builds.

**Decision (proposal):** Adopt the community cache as the persistence layer and a warm devcontainer as the environment entry point. Concretely: (1) add a .devcontainer (elan + lean-toolchain pin + lake exe cache get + prebuild of the PleaNP import closure) so any cloud editor (GitHub Codespaces free 60 h/mo, Gitpod free 50 h/mo) or any fresh sandbox converges to a warm state in minutes; (2) keep .github/workflows/ci.yml as the always-free headless build oracle (public repo = unlimited Actions minutes), adding a Mathlib olean cache-restore step; (3) use the lean4web playgrounds (live.lean-lang.org, lean.math.hhu.de) for single-file experiments; (4) compartmentalize by keeping new modules import-light and the calculus layer physically separable as its own mini lake project if needed. Do NOT vendor Mathlib or self-host the olean cache — the community Azure cache is the decentralization already in place, and DEC-003 (import upstream) stays intact.

**Rationale:** Verified in-session (2026-09-06): elan installs in seconds and lake exe cache get restores ~8.5k Mathlib oleans in minutes; with cache warm, a single PleaNP module builds in ~4 s. The expensive, non-persistent step (full Mathlib build) never needs to happen in any environment — the community cache is persistent, free, and public. The M4 box is a convenience, not a prerequisite. Options researched live (Codespaces/Gitpod requirements, mathlib cache mechanics, lean4web, globally-shared-install pattern) — see docs/TOOLCHAIN_SOLUTIONS.md.


---

### DEC-015

**Date:** 2026-09-06
**Status:** Active
**Scope:** Multi-agent task coordination + community intake

**Decision:** Adopt the **muse** multi-agent workflow (muse/TASK_WORKFLOW.md, 2026-09-06) for PleaNP, adapted to PleaNP's integrity-gate reality: one task = one GitHub issue; run-ids under shared identity; atomic label claims (status:available / status:claimed / status:done / status:blocked-needs-input, plus priority:high, community-ready, needs-gate); direct-to-dev commits with no force-push; blockers dir + sweeps + end-of-session report. Formal claims additionally pass the PleaNP gates ( hygiene, vacuity, model-consistency, lethality, #barrier_check) before closing as done — the gates section of docs/MULTI_AGENT_WORKFLOW.md is the PleaNP-specific overlay on muse's protocol.

**Community surface (Zulip) — DEFERRED (2026-09-06):** external contributors do NOT commit to dev; they file issues/PRs, which agents triage into the queue, gate, and merge (docs/CONTRIBUTIONS.md). The community-ready label marks first-contributor-friendly work. **The Zulip connection itself is deliberately deferred**: the maintainer is not Lean-literate and not on Zulip, and prefers the artifact to speak first. The repo stays GitHub-native (issues + PRs + CI) — fully functional without any external chat channel. Revisit Zulip only when (a) the repo has a working, gated, stranger-pickupable state, and (b) the maintainer has a human accountability anchor (a Lean-literate reviewer/co-maintainer) so community trust does not rest on "AI agents did this" alone.

**Rationale:** PleaNP's work is inherently multi-agent (gated rung ladder); the shared GitHub identity needs the muse discipline to prevent double-claims and stranded dependents. The community surface multiplies capacity without crossing the statement-fidelity trust line: external PRs still pass Gates 1-6 before merge.


---

### DEC-016

**Date:** 2026-09-06
**Status:** Active
**Scope:** Human semantic review layer for a non-proof-writing owner

**Decision:** Add a third layer (the probe checklist) to the human semantic
review stack, on top of the mechanical gates and the two-translator read-back.
Rationale: the read-back (Layer 2) still asks the owner to compare two English
sentences and spot subtle differences (quantifier order, direction, bounds) — a
high bar for someone with intro math/CS who does not write proofs. The probe
checklist turns each claim into 3–5 tiny, independent, single-choice probes
(quantifier/direction/bound/existence) at intro-level (plain-language) level; one
wrong answer BLOCKS the claim and names the specific probe. Tool:
tooling/gates/probe_check.py (specs in tooling/gates/specs/, unit-tested). The
owner is NEVER the tiebreaker on ambiguity — machines/agents absorb it; the
human only confirms single concrete facts. Bias-guard: expected probe values
are derived from the Lean (what the proof says), never from the informal
wish-list. Doc: docs/STATEMENTS/HUMAN_REVIEW_LAYERS.md.


---

### DEC-017

**Date:** 2026-09-06
**Status:** Active
**Scope:** Human review interface — non-blocking, async, multistream-safe

**Decision:** Surface the irreducible human semantic confirmation through a
review inbox (reviews/ + tooling/reviews/review_inbox.py + docs/REVIEW_INBOX.md):
one claim = one review point = ONE plain-language yes/no question. Agents
FILE points and CONTINUE — never blocking on the human (inbox, not gate). The
human reads a single generated reviews/INBOX.md (batched, oldest-first, merged
across all parallel agents) and answers with confirm/flag. A flag reopens the
claim retrospectively (matching the existing retrospective-on-dev model);
nothing stalls. Rationale: the semantic hop is inherently human-async; making
it a synchronous gate would serialize the multi-agent stream and concentrate
review burden. The inbox keeps the human's effort to one page + one command
per answer, scales across streams, and keeps the machine-derived evidence
(statement_lint summary + informal claim) attached to every point. Rules:
expected answers come from the Lean (bias-guard); one point = one question;
missing evidence is a process failure, not a flag; never block.


---

### DEC-018

**Date:** 2026-09-06
**Status:** Active
**Scope:** Proof stance — acknowledged classical (non-constructive)

**Decision:** PleaNP's Lean proofs are and remain **classical (non-constructive by choice)**: the clean-proof axiom fingerprint is {propext, Classical.choice, Quot.sound}, verified and enforced by tooling/gates/axiom_check.py in CI. This is deliberate, not accidental. A **strategic rationale is added (owner, 2026-09-06):** if P = NP turns out to be true (cryptography collapses), a *constructive* proof would also have *constructed the hard object* that breaks crypto — furnishing the weapon. A non-constructive proof proves existence via classical choice without manufacturing the dangerous instance, which is the safest posture for the project if the crypto-hostile outcome occurs. This complements the natural-proofs barrier, which already says natural lower-bound techniques would imply the collapse; non-constructiveness lands on the safe side of that too.

**Scope note / honest trade-off:** classical choice is a genuine axiom; constructivist reviewers discount existence-on-choice claims. The trade (don't build the weapon vs. existence is classical-conditional) is accepted and documented. Constructive proofs remain welcome where the mathematics is constructive (the gates do not forbid them); they would be highlighted. Reversing to a constructive-only stance would be a major pivot and requires a new DEC.

**Rationale:** matches the mathematics (P vs NP barrier statements are inherently existence-shaped), matches Mathlib's classical posture (DEC-003), is CI-monitored (axiom_check fails on any drift), and — per the owner's strategic point — is the safest stance if the hostile cryptographic outcome occurs.


---

### DEC-019

**Date:** 2026-09-06
**Status:** Active
**Scope:** Creative-strategy protocol for hard sub-tasks

**Decision:** Adopt a structured creative-protocol (semantic excavation,
constraint cartography, cross-domain transplantation, synthesis +
persuasion scaffold, comprehension bridge) as the **idea-generation layer**
for hard, open-ended sub-tasks (e.g. BGS diagonalization, future novel
lower bounds, search-loop design). The protocol is documented in
docs/CREATIVE_PROTOCOL.md. **Governing rule:** novelty without verification
is crank-adjacent; a protocol output becomes real work only when rendered
as a Lean statement/proof and passed through the gates (multi-rendering
churn -> dual_render -> statement_lint -> review loop -> hygiene/axiom).
The creative phase is upstream of the pipeline, never a bypass.

**Worked example:** running the protocol on "P vs NP has no obvious next
step in Lean" produced a candidate: formalize the **provability boundary**
of the near-P-vs-NP lattice (which weaker statements are provable; where
provability stops). That idea is recorded as a candidate for a future rung,
not adopted as a task.

**Rationale:** the obvious approach to the hard steps is known to plateau
(the barriers classify it dead); the project needs a structured way to
generate genuinely novel candidate strategies without descending into
unverified brainstorms. The protocol gives the creative step a shape, and
the gates keep it honest.


---

### DEC-020

**Date:** 2026-09-06
**Status:** Active
**Scope:** Mathlib submission strategy + rejection handling

**Decision:** Prepare for the real Mathlib submission process with an honest
playbook (docs/MATHLIB_SUBMISSION.md): Zulip-first community alignment, small
PRs, bors/CI, and the five realistic rejection paths (too-early, too-big,
design-objection, duplicate, substantive-criticism) each with a concrete
handling plan. Reputation non-negotiables: never submit a sorry; submit the
oracle-machine substrate (the upstreamable module) not the barrier theorems
(those are research/papers); cite prior art; follow the community process;
require one human accountability anchor.

**Rationale:** PleaNP will eventually want to contribute its oracle-machine
layer to Mathlib (the gap audit confirms no upstream effort provides it), and
rejection is the default expectation for any Mathlib submission. Preparing
the process and the rejection responses now prevents reputational damage and
turns feedback into a concrete fix list rather than a dead end. No submission
is planned until the upstream P/NP substrate lands and a human anchor exists.


---

### DEC-021

**Date:** 2026-09-06
**Status:** Active
**Scope:** LLM architecture — no external LLM; OpenHands is the model

**Decision:** PleaNP does **not** use an LLM external to OpenHands. The "two
independent translators" guarantee (Gates 3/4) is satisfied by **two
independent OpenHands agent passes** — never by API calls from inside the repo
tooling. The external-LLM hook in `readback.py` (OpenAI/Anthropic) is demoted
to an **optional capability** (harmless, documented, off by default); CI uses
the deterministic-skeleton fallback (no secrets). Issue #5 ("wire an LLM
provider into CI as a secret") is closed as **resolved-by-architecture** — its
premise (needs a secret) was wrong for this project.

**Why:** the project's "AI" is the agent itself. Adding a separate
LLM-provider + CI secret would duplicate the model OpenHands already provides,
add secret-handling risk, and misrepresent where the intelligence lives. The
multi-rendering protocol (#24) formalizes the agent-pair path as the real
mechanism.

**Scope note:** the readback.py LLM hook stays in the code as an OPTIONAL path
(useful if a future contributor wants a non-agent LLM for a specific check),
but it is NOT part of PleaNP's architecture and must never be assumed in CI.

**Rationale:** aligns the tooling with how the project actually runs (agents
do the work), removes the secret-maintenance burden and the implied external
dependency, and keeps the two-independence guarantee where it belongs: in the
agent-pair protocol.
### DEC-022

**Date:** 2026-09-10
**Status:** Active
**Scope:** Lessons from the 2026-09-08 AI-assisted Navier-Stokes/Euler Lean releases (adoption of three statement-fidelity affordances).

**Decision:** Adopt, from OpenAI's `NavierStokesAndEuler` release (and the concurrent `tristanbuckmaster/fluid_lean`), three affordances: **1. Comparator-style machine-checkable statement-equivalence for every frozen PleaNP statement.** An independent, externally-sourced challenge module (`lean/PleaNP/Challenges/`, per the template `docs/STATEMENTS/ComparatorChallenge.template.md`) plus a JSON pin (`lean/ComparatorChallenges/<Name>.json`: theorem names + `permitted_axioms`), machine-checked by `lake exe comparator` when the Comparator lake dependency is available. **2. `formalization.yaml`(v0.4) machine-readable statement manifest** at repo root (declaration ↔ file ↔ sorry_count ↔ axioms ↔ comparator_config ↔ review status; initial manifest committed covers the current green CI surface; add/update rows in the same commit as every proof freeze, same rule as `docs/SORRY_TRACKER.md`). **3. Standalone-paper-theorem-file layout** ("PaperResults pattern"): a frozen claim lives inits own standalone Lean file, imported bya root module, and covered by CI builds + `#print axioms` before any proof search attaches; Gate 1 as file layout, not discipline. Full background: `docs/LEAN_FORMALIZATION_LESSONS_2026-09-10.md`.

**Why:** The OpenAI release is the first large-scale AI+Lean execution of thee exact statement-fidelity architecture PleaNP mandates: proof root does **not** import the reference problem statement; an independent challenge (Copied from DeepMind's Formal Conjectures) declares it; `lake exe comparator` machine-checks the adaptation; and `#print axioms` + `sorry_count: 0` vouch for hygiene (~2,655 files / ~640K lines, 0 sorries). Moreover its 2026-09-10 push added standalone paper-theorem statement files, proving the "freeze-the-claim-as-a-file" layout scales. PleaNP had two genuine gaps the release spotlighted: a machine-checkable *formal* equivalence layer (dual-render/read-back compare human/agent renderings, not a machine-checked formal reference) and a unified machine-readable statement manifest. Hence these three adoptions. The meta-conclusion(recorded inthe lessons doc): the NS releases validate PleaNP's core negative-space/barrier-scope design at scale; their result is a disproof-of-global-smoothness(a "there is no global smooth solution";the shape of `P ≠ NP`), andthe formalization cost(166 pages → 640K lines) argues for the barrier-library scope. Non-adoptions(also recorded): no "10,000-agent" model (claim-sized agents suffice);precision over parallelism); no "publish raw agent output" pattern (per-claim, human-reviewable commits); no direct P-vs-NP formalization target; no single-Comparator-reference-as-sufficient(keep dual-render), and no vendored inline deps(import upstream, DEC-003). OpenHands remains the model(DEC-021); OpenAI's `formalization.yaml` automation section(`GPT-6 Astra/Codex`)isa *reference format*,not data for PleaNP.





**Phasing:**(i) this commit: lessons doc + template + manifest + docs updates(no code, no Lean, no CI change);(ii) next practical step when a barrier statement is next touched: create `lean/PleaNP/Challenges/Relativization.lean` + `lean/ComparatorChallenges/Relativization.json` per the template, and add the `Comparator` lake dependency aspirational, as tracked in `docs/LEAN_FORMALIZATION_LESSONS_2026-09-10.md` §3.1;(iii) whenthe Comparator dependency lands, the CI job assertthe comparator configs(as aspirational follow-up). **Sandbox note:** no `lake`/`python-yaml` in every write sandbox, so the repo ships its own stdlib mini-YAML parser (`tooling/galaxy/miniyaml.py`) and `formalization.yaml` is a **checked artifact — parse-valid at commit time** (the Galaxy data layer and CI consume it; any malformation is tracked as a defect, see #43). (See the note in the manifest header and the lessons doc §3.2.)


### DEC-023

**Date:** 2026-09-10
**Status:** Active
**Scope:** Creativity/authority gates for AI-discovered formal claims — lessons from the 2026-09-08 Navier–Stokes releases (beyond sorry/vacuity).

**Decision:** Beyond DEC-022's three statement-fidelity adoptions, adopt three creativity/authority components from the NS releases (details in `docs/LEAN_FORMALIZATION_LESSONS_2026-09-10.md` §3–§5):

1. **Constraint-Net Cartography** — add as `docs/CREATIVE_PROTOCOL.md` Phase 2.5 (the executable-filter step): before creative search on a hard rung, enumerate the full independent-constraint net the construction must satisfy, and specify an automated cheap rejector per constraint, so the search concentrates on residual freedom, not cherry-picking. Stack the existing proto-rejectors (`#barrier_check`, validation must-refute lemmas, Comparator refs (DEC-022), load-bearing-choice audit (below). This turns "creative search" from "generate-then-pick" into "constraint-guided search"; rejection traces are kept as evidence.



2. **Proof-intuition record** — new template `docs/STATEMENTS/ProofIntuition.template.md`: each AI-discovered formal claim ships a human-legibility record(5-layer plain-words construction, load-bearing audit, perturbation tests, cheap-outs confession, steelman, reviewer checklist -- the "explanation" slot OpenAI filled with its 166-page paper. A claim is not authoritative-ready until humans can testify "I understand this construction and why it is right." "Formally checked but not yet human-legible" is a finding, not a blocker; if no human can fill the record, record that honestly.



3. **Load-bearing-choice audit** — extend `docs/VALIDATION_SUITE.md` (§"Load-bearing-choice audit")izin binder-lethality from *definitions* to *proofs*: audit which *choices* do the work(oracle, encoding, enumeration-ordering, force-like datum.)— internal mechanism or choice-bought? Meet the "internal mechanism, externally-perturbable" standard (the NS calibration);flag constructions whose conclusion is bought by an exact choice. This is the "chosen-to-work" detector the no-sorry/no-vacuity gates cannot see.



**Why:** The NS releases' deepest creativity lesson: their scale jump (~100 agents/50h Euler disproof vs ~10,000/88h NS) was **constraint density**,not raw compute -- each dense constraint (smooth force, bounded energy, exact residual cancellation) is a cheap rejector, so the parallel search concentrated on the residual freedom. And authority came from the 166-page paper, not the green build: Buckmaster called the LLM-generated Lean-verified proof "AI slop" and rewrote itfor clarity; OpenAI's own `formalization.yaml` says "self-assessed". A proof can compile, pass vacuity, and still be *creatively dishonest* if a *choice* carries the conclusion rather than an *internal mechanism*(the "define a force after the fact.arrange terms to cancel" move). These gates check *how the construction was found* and *whether humans can own it*,orthogonal to hygiene(Gate 6)and vacuity(Gate 5) -- the authority mechanism at the frontier, the mechanical gates cannot see.



**Phasing:**(i ) this commit: DEC-023 record + ProofIntuition template + VALIDATION_SUITE audit section + CREATIVE_PROTOCOL Phase 2.5 + docs pointers(no code, no Lean, no CI change).(ii ) apply when a barrier proof is next claimed (#18 BGS or Rung 9/11 output): file the intuition record per template, and run the load-bearing audit alongside Gate 4.(iii ) when creative search on Rung 9/11 begins, run Phase 2.5 first, keeping the rejection traces as evidence. **Sandbox note:** no `lake`/`python-yaml` inthe write sandbox -- docs-only edits, validated by structure/sweep only.



**Rationale:** CREATIVE_PROTOCOL's Phase 2(constraint cartography) listed constraints as *intellectual context*;Phase 2.5 upgrades them to *executable filters* -- which is what separates compile-time-constrained search from post-hoc-selected construction(turning "synthesize" into auditable work, completing DEC-019's protocol).The proof-intuition record is the missing authority mechanism: Gate 4 reads back the *statement*, nothing yet reads back the *proof's explanation* -- the NS releases show explanation is load-bearing for authority, not cosmetic;`sorry`-freeness and non-vacuity are necessary, not sufficient, for a construction to be authoritative.

### DEC-024

**Date:** 2026-09-11
**Status:** Active
**Scope:** Oracle-query substrate direction — word-query repair (Option Ω from the creative protocol solves the #26/#22 Fintype-Query wall).

**Decision:** Adopt **Option Ω — word-query oracle substrate** as the direction for resolving the #26/#22/#27 blockers: rewire the oracle substrate (`lean/PleaNP/Computability/Oracle.lean`) so the query is read from a **tape's content** (a finite word over the machine's own finite alphabet, per the spec's own "oracle tape" model `docs/STATEMENTS/Oracle.lean.spec.md` §2.2), instead of fusing the query type into the input-alphabet slot (`tm'.Γ tm'.k₀ = Q` in `lean/PleaNP/Computability/OracleComplexity.lean`). Recorded options ((a) bounded query family; (c) per-length reindexing) become **unnecessary** — they solved a self-inflicted interface bug by bendingthe theorem;Ω removes the artifact and keeps **every frozen statement unchanged** (`U_B`, `lean/PleaNP/Barriers/BGSDiagonal.lean`, `lean/PleaNP/Barriers/Relativization.lean`: `Query = Σ n, Bits n` stays; cost model (query = exactly 1 step],totality,`P^∅ = P`,andthe BGS counting(2^n vs p(n)) all survive).The cross-domain black-box audit (`docs/STATEMENTS/oracle-word-query-blackbox-audit.md` (pending #39), #39) records the deep invariant every mature black-box model separates infinite query *values* from finite machine *syntax*.

**Why:** The wall existed becausethe v4 encoding made each query a single alphabet symbol — an infinite alphabet on an infinite query type, violatingthe `Fintype (Γ k₀)` requirement. But a machine's alphabet is finite while its *tape contents* are unrestricted — queries written as words over the finite alphabet are the standard oracle-TM model ((the BGS paper's own model, andthe repo's own spec's model). No theorem shape changes; andremove-the-artifact beats bend-the-theorem for the barrier program's credibility (**Workflow output:** #33 (v5 work-order spec),#35 (implementation),#36 (U_B-in-NP machine},#37 (diagonalization D1-D6,#38 (campaign re-scope},#39 (audit},#40 (tests; #27 still awaits human confirmof the re-scoped lenseson #38.

**Phasing:**(i) this commit: decision record + blocker files updated + design-doc note + issue queue wiring (no code, no Lean, no CI change);(ii) #33 spec written by an agent, then #35 implementation (the substrate re-type/rewire, build green + gates; (iii) #36/#37/#38 consumethe repaired substratein dependency order; (iv) #39 docs deliverable can land anytime (no block. **Sandbox note:** no `lake`/`python-yaml` inthe write sandbox — docs-only edits, validated by structure/sweep only.

### DEC-026

**Date:** 2026-09-13
**Status:** Active
**Scope:** Multi-agent duplicate-work prevention — claim races + parallel-pass collisions + shared-file conflicts.

**Context:** During the 2026-09-13 Rung-4/BGS burst, the parallel-agent protocol produced three avoidable duplicates and repeated shared-file conflicts: (1) **claim races** — two agents claimed #65 within ~80s, and the "latest comment wins" reading let both believe they owned it; (2) **stale-claim-then-return** — a sweep-reclaimed #63 Pass 1 (claim comment >1h old) while the original sibling returned mid-session and landed superior work, forcing the reclaiming agent to drop redundant parallel A2; (3) **shared-file collisions** — every new module lands on the same `ci.yml` + register-check + gate-docs files, causing repeated 4-way rebase conflicts.

**Decision:** Amend `docs/MULTI_AGENT_WORKFLOW.md` with three rules:
- **Recent-activity guard (§Claiming step 1):** before claiming an `available` item whose subject overlaps a recently-active `claimed` item (same file/rung/adjacent pass), check `git log origin/dev` for sibling commits in the last ~1h *even when the claim comment is stale* — an agent can be mid-session with an aged comment. Default to a DIFFERENT task when fresh evidence exists.
- **Claim-race rule (§Concurrent-work):** the **earlier** claim comment (by timestamp) wins; the later claimant backs off, restores `status:available`, posts a one-line back-off recording run-ids, and picks different work. Replaces the "latest comment wins" ambiguity.
- **Duplicate-work rule (§Concurrent-work):** after a rebase reveals a sibling landed the same pass/statement, never push a second copy — drop or merge-and-reconcile in ONE commit, and prefer preventing the duplicate via the recent-activity guard.

**Why:** Parallel agents under a shared identity cannot tell coincident claims apart without run-ids and timestamps; the cost of a duplicate formalization run (elaborate Lean proofs on the same substrate) is the single highest-waste failure in this burst. The recent-activity guard makes the sweep defer to fresh evidence instead of the stale-claim clock; the claim-race rule gives an unambiguous, auditable winner; the duplicate-work rule makes "drop the redundant copy" the default, never-push-twice.

**Workflow output:** the three rules above landed in `docs/MULTI_AGENT_WORKFLOW.md` §Claiming (step 1, step 4) and §Do-the-work (concurrent-work rules). **Phasing:** (i) this commit: DEC + workflow-doc amendments (docs-only); (ii) agents adopt the guard/rules at their next start-of-session sweep (no code/Lean/CI change required).

### DEC-025

**Date:** 2026-09-13
**Status:** Active
**Scope:** Rung 4 circuit substrate — dependency direction for `PleaNP.Circuits`.

**Decision:** Reject the complexitylib import for the Rung-4 circuit substrate. Build `PleaNP.Circuits` locally (option (b) of issue #70) instead of vendor-repairing or toolchain-matching complexitylib (option (a)). This closes #70 Pass 1; the local build proceeds under #71.

**Rationale:** The #70 issue was filed when complexitylib pinned Mathlib `v4.30.0` vs PleaNP's `v4.31.0` — a one-minor drift across ~23 modules. That premise has since decayed. At the current head (`6c248df`, 2026-09-08) complexitylib pins **`leanprover/lean4:v4.34.0-rc2`** (an rc prerelease toolchain), pins **Mathlib rev `e06eff5f9537`** (2026-08-31, v4.34-rc2 era), and additionally requires the **`cslib`** dependency (`leanprover/cslib@d9be641`, its own Mathlib rev). PleaNP pins the stable **`v4.31.0`** toolchain/Mathlib — a two-minor + rc gap, not a one-minor drift. Reconciling either direction is a losing trade: pinning PleaNP to v4.34.0-rc2 sacrifices the stable-pin discipline for an rc prerelease; upstreaming complexitylib's ~23 (now likely more) drifting modules fights an upstream that has already moved two versions forward and keeps moving. Importing would also drag in a 1685-file dependency surface (its `Circuits/` tree alone is ~350 files) for the small slice PleaNP needs, and DEC-003 already established the PleaNP-local substrate precedent (oracle machines are local because no upstream effort provides them). Rung 4's need is modest — typed Boolean circuits with size/depth, P/poly shape, natural-property vocabulary — which #71 sizes at 3 runs. The Mathlib-in-namespace discipline that made local sense for oracles extends cleanly to circuits under `PleaNP.Circuits`.

**What happens instead:** #70 stays open only through this Pass-1 record; the DEC-025 decision closes the import-vs-local fork, #71 (Rung 4 substrate build-out) becomes the active path, unblocked (#70 Pass 1 was the posture-setting gate). If a future upstream effort lands circuit machinery in Mathlib proper (or complexitylib reconciles to a stable PleaNP mathlib), revisit via the playbook's import row at that time.

### DEC-027

**Date:** 2026-09-16
**Status:** Active
**Scope:** Packaging — how downstream repos consume PleaNP. Closes issue #102.

**Decision:** Adopt **option (A)** from #102: add a root `lakefile.lean` that repoints the package at the existing `lean/` source tree via `srcDir := "lean"`, and restate the library declarations there. Option (B) (move the package to the repo root) and option (C) (publish an extractable sub-package) are **not** taken now — (B) has a large blast radius across CI, the devcontainer, `tooling/elantool.sh`, and `AGENTS.md`, all of which run from `lean/`; (C) remains the better long-term boundary and is deferred, not rejected.

**Why a root lakefile is needed at all:** Lake resolves a *dependency's* package root at the repo root, so a sibling repo cannot `require PleaNP from git ...` while the only lakefile is at `lean/`. The failure is pre-Lean and unambiguous:

    error: PleaNP: no configuration file with a supported extension:
      .lake/packages/PleaNP/lakefile.lean
      .lake/packages/PleaNP/lakefile.toml

Requester is the sibling project **Maith**, which needs `PleaNP.Circuits` for its axiom-discovery benchmark corpus (Maith #26 / `docs/experiments/BENCHMARK_CORPUS_PLAN.md`). Both repos pin Lean `v4.31.0` and Mathlib `v4.31.0`, so no toolchain reconciliation is required — the contrast with DEC-025, where the version gap is exactly what killed the `complexitylib` import.

**Why `lean/` stays authoritative:** every build command in the repo operates from `lean/` — CI (`working-directory: lean` on every Lean step), `.devcontainer` `postCreateCommand`/`postStartCommand`, `tooling/elantool.sh`, and the `AGENTS.md` bootstrap. Lake picks the *nearest* lakefile, so `cd lean && lake build ...` continues to read `lean/lakefile.lean`. The root file is additive; it changes no existing command. Verified: with the root file present, `cd lean && lake exe cache get && lake build PleaNP.Circuits.Basic` succeeded (8558 jobs) and `lake build tests` succeeded (8564 jobs).

**The duplication is unavoidable — tested, not assumed.** A minimal root file (`package` + `srcDir` + `require mathlib`, no `lean_lib`) resolves the dependency path but **does not work**: the consumer fails with

    error: Demo/Probe.lean:1:0: unknown module prefix 'PleaNP'

because no library is declared, so the dependency builds nothing and there are no oleans to import. So the root file must restate the `lean_lib`/`lean_exe` declarations. `srcDir` handles the *layout*; it does not handle *target declaration*.

**Mitigation for the duplication:** `tooling/gates/lakefile_sync_check.py` fails (exit 1) if the root shim and `lean/lakefile.lean` disagree on the package name, any `lean_lib` name and its `globs`/`roots`, any `lean_exe` name and its `root`, or the `require mathlib` pin. It normalises whitespace and ignores comments, so a formatting-only reformat is not reported as drift — otherwise people would learn to ignore the guard. Its tests (`tooling/gates/tests/test_lakefile_sync.py`, 5 tests) assert **seven** drift classes are each detected and a matching pair is accepted. Wired into CI after the build steps; it needs no Lean toolchain.

**Verified end-to-end against this commit.** A scratch consumer package:

```lean
require PleaNP from "../PleaNP"
```

and importing the circuit substrate:

```
✔ Built PleaNP.Circuits.Basic (33s)
✔ Built PleaNP.Circuits.AC0 (4.8s)
✔ Built Demo.Probe (4.1s)
info: Demo/Probe.lean: PleaNP.Circuits.BoolGate : ℕ → Type
info: Demo/Probe.lean: PleaNP.Circuits.parity_notin_AC0 : Prop
```

Real definitions resolving across the repo boundary, including the AC0 module
that Maith's first transfer target (parity ∉ AC⁰) depends on.

**Also repaired in the same commit — a pre-existing breakage that #102 would otherwise have inherited.** The `ci.yml` copy on `dev` was **invalid YAML**, so GitHub would have rejected the entire workflow: three step boundaries had been swallowed into the previous scalar or mis-indented —

- line 38: `working-directory: lean      - name: Barrier-check verdict harness (...)` — step boundary inside the previous scalar
- line 44: a step indented 12 spaces where siblings use 6
- line 55: `...OracleV5Tests.lean- name: Gate-REVIEW register machine-check (...)` — boundary joined with no separator

This is the **third instance of the same corruption signature** recorded in #101 (content joined across a line boundary; see also `BarrierCalculus.lean`'s doc comments). `main`'s copy is valid YAML but an **older generation** (21 steps, no `Circuits` build), so this is a dev-branch regression that would have broken CI the moment `dev` merged. Repair was surgical: 5 insertions / 3 deletions, and an assertion that content is byte-identical modulo the intended line splits. Consequence: adding a CI step to this file was not possible without fixing it first.

**Consequences recorded for the maintainer:**

- **CI coupling:** once Maith depends on PleaNP, Maith's CI has a hard dependency on PleaNP's `Circuits` closure building green. The warm image at `ghcr.io/allenpd728/pleanp:main` (Plan E) may be the better consumption path than a source build.
- **Build a target, not the full tree:** PleaNP's full-tree `lake build` still fails on the two documented pending-sorry modules (`OracleUpstreamP`, `Relativization`). Consumers must build the `Circuits` closure specifically.
- **Import weight:** `PleaNP.Circuits.Basic` begins with `import Mathlib`, so consumers inherit the full Mathlib closure.
- **CI trigger gap:** `.github/workflows/ci.yml` triggers only on pushes to `main` and PRs to `main`, so **`dev` pushes are not automatically verified**. This change was verified locally (builds + gates + the end-to-end consumer) rather than by CI on `dev`. Worth deciding separately whether `dev` should be in the trigger list — flagged, not changed here, since it is a policy call.

### DEC-028

**Date:** 2026-10-01
**Status:** Active
**Tier:** 1
**Scope:** Task protocol
**Origin:** human
**Decision:** Triage decisions for the RLM Analyzer pass over PleaNP. D1: an RLM Analyzer report is unverified LLM triage, and a finding becomes a task only after it is confirmed against raw files in this repo. D2: a refuted or stale finding gets no task; it is recorded in the triage summary with the evidence that refutes it. D3: generic web-application security advice (authentication, authorization, API validation, security headers, WAF, pen testing, SAST/DAST, log anomaly detection) does not apply to a Lean 4 / Python library and gate repo that runs no web service, so no task is filed for it. D4: one task per verified finding, no bundling and no extra scope. D5: anything that needs a human choice is filed as a blocker for the owner, not decided by the agent.
**Rationale:** The reports are a triage aid, not a source of truth. Verification against raw artifacts is the only step that separates a real defect from a plausible-sounding one, which is the rule the integrity gates already apply to results. D4 keeps each task claimable in one run with an unambiguous acceptance check.
**References:**
  - `rlm-triage-summary.md` in `philipdallen/portfolio-ops` (branch `tasks/rlm-triage-2026-10-01`)
  - `docs/MULTI_AGENT_WORKFLOW.md` (task definition, blocker mechanics)
