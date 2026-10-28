# Upstream tracking: Mathlib complexity efforts

The computational-model substrate (Rung 2) is *not* PleaNP's to build — it's being actively contested by multiple efforts upstreaming into Mathlib. This document tracks them so PleaNP imports the right thing rather than reinventing or picking sides.

Last reviewed: 2026-10-28 (added cslib as a numbered row — effort #9 — verified against its primary source, and updated the #2 stance line to point at it. The eight prior rows were last verified 2026-10-19; this run re-verified cslib only.) Material change since the 2026-10-19 review: cslib is now tracked as its own row (#9), carrying SingleTape and MultiTape Turing-machine models, a typed Boolean-circuit development, and a `PolyTimeComputable` predicate — but still no oracle machines, no P/NP classes, and no relativization content. See each row for its verification date. This is a living document — update when upstream lands.

---

## The active efforts

### 1. Mathlib #35366 — `Turing.TM1` with fuel-based step counting

- **Source:** https://github.com/leanprover-community/mathlib4/issues/35366 — verified 2026-10-19: **open**, last activity 2026-04-16 (a maintainer redirecting the author to the Lean Zulip `general` channel); effectively **stale** for ~6 months, no PRs opened from it.
- **Author:** KrystianYCSilva (opened Feb 2026)
- **Approach:** Extends Mathlib's existing `Turing.TM1` (from `Mathlib/Computability/PostTuringMachine.lean` (upstream), Carneiro 2018) with `runN` (fuel-based) step counting, then defines P, NP, and proves `p_sub_np`.
- **Status (2026-10-19):** Issue open, no linked PR, no maintainer endorsement beyond a redirect to Zulip. The original description's claims (working, zero `sorry`, compiles against Mathlib v4.28.0-rc1) are unchanged from the 2026-08-18 review — no new code has landed. Proposes a 3-PR sequence: `step_none_iff` lemma → `Mathlib/Computability/TM1Complexity.lean` (upstream) with `runN` → complexity classes + `p_sub_np`.
- **Builds on:** existing, merged Mathlib infrastructure (`Turing.TM1`).
- **PleaNP stance:** Strong candidate to import from *if* it revives. Uses existing infrastructure, lowest-risk path. Pending maintainer feedback on `runN` vs relational approach — unchanged by this review (stance changes are a human call).

### 2. PR #33132 — `FinTM0` bundled type

- **Source:** https://github.com/leanprover-community/mathlib4/pull/33132 — verified 2026-10-19: **closed, not merged** (closed 2026-09-17; created 2025-12-20). Closing comment (BoltonBailey, 2026-09-17): *"I am closing this PR since it seems like it will be faster to make progress on models of computation in cslib."*
- **Author:** BoltonBailey
- **Approach:** A *new* `FinTM0` bundled type with `EvalsTo`/`EvalsToInTime`, rather than extending existing `TM1`.
- **Status (2026-10-19):** **Dead as a Mathlib PR.** The author has redirected the work to `cslib` (Lean Computer Science Library, `leanprover/cslib`), whose `Cslib/Computability/Machines/Turing/` tree now carries `SingleTape` and `MultiTape` machine models (verified 2026-10-19).
- **PleaNP stance:** **Superseded — do not watch #33132.** The `FinTM0` PR is closed; the same author is now building machine models in `cslib`. Follow `cslib` instead — now tracked as **effort #9** (added 2026-10-28).

### 3. `descriptive-complexity` (separate repo)

- **Source:** https://github.com/PierreSenellart/descriptive-complexity (default branch `master`) — verified 2026-10-19: last push 2026-10-07; latest release **v1.3.0** (2026-09-22, "for Mathlib v4.34.0"); `lean-toolchain` = `leanprover/lean4:v4.34.0`.
- **Author:** PierreSenellart
- **Approach:** Machine-free — defines NP-completeness via logical definability on top of Mathlib's `ModelTheory` (Immerman-style descriptive complexity). No Turing machines. Covers all 21 Karp problems, Cook-Levin without a machine model.
- **Status (2026-10-19):** Actively maintained, released (v1.3.0 against Mathlib v4.34.0; was v1.2.0 / v4.33.0 at the 2026-08-18 review). Not part of Mathlib core.
- **PleaNP stance:** This is a *different strategic axis*. It avoids the computational-model pain entirely but defines complexity classes logically, which may not give us the oracle-machine substrate relativization needs. Track as a possible source for NP-completeness results, but the barriers likely need a machine model with oracles. (Unchanged.)

### 4. Simas (2026, arXiv:2601.15571)

- **Source:** https://arxiv.org/abs/2601.15571 — verified 2026-10-19: **the cited id does not match the described work.** `arXiv:2601.15571` resolves to *"Thermodynamic Limits of Proof"* (Tristan Simas, 2026-01-22), a physics-of-proof paper, not "polynomial-time reductions in Lean 4". The PleaNP docs that cite this id (`docs/GAP_AUDIT.md` §2/§5, `docs/PRIOR_ART.md`) describe a reductions-in-Lean paper; the id is **unverified / likely wrong** and is flagged for a human to correct at source.
- **Approach:** As described in PleaNP's docs: polynomial-time reductions in Lean 4, but deliberately does *not* use Mathlib's TMs and does *not* define P/NP. **Not confirmed against a primary source** — no arXiv entry by this author matches the description (searched by author and by title terms, 2026-10-19).
- **Status (2026-10-19):** Citation unverified. Treat as a **provisional reference only** until a correct identifier is supplied.
- **PleaNP stance:** Reference for reduction-formalization technique, but not importable (defines its own substrate). Stance unchanged; the citation itself needs fixing (a human call — this task is verification, not re-decision).

### 5. The Coq precedent (not Lean, but methodological)

- **Gäher & Kunze, ITP 2021.** Cook-Levin in Coq using the call-by-value λ-calculus L as model. Required Forster-Kunze-Wuttke-Smolka (L ↔ TMs, polynomial overhead) first.
- **Methodological lesson:** The λ-calculus route was chosen *because* TMs were too painful ("19K lines, inherently infeasible" — Forster). If Lean's `Turing.TM1` route proves equally painful, the λ-calculus or synthetic approach is the fallback.
- **Status (2026-10-19):** Unchanged — a fixed historical precedent, not a live effort. No re-verification needed.

### 6. complexitylib — Samuel Schlesinger

- **Repo:** https://github.com/SamuelSchlesinger/complexitylib — verified 2026-10-19: **default branch is now `dev`** (it was `master` at the 2026-08-18 review; `master` no longer exists — the API returns 422 for `commits/master`). Head `add0aca` (2026-10-07). No releases/tags.
- **Approach:** A standalone Lean 4 / Mathlib formalization of complexity theory using concrete Arora–Barak-style multi-tape Turing machines (deterministic, nondeterministic, probabilistic) over a fixed four-symbol alphabet, with explicit time and space predicates. Concrete over abstract: machines, circuits, reductions, and encoders are concrete definitions, not bare existence claims. An `AxiomGuard` script mechanically guards headline results against hidden axioms.
- **Toolchain (2026-10-19):** `leanprover/lean4:v4.35.0-rc3` (on the `dev` default branch; bumped from v4.34.0-rc2 at the 2026-08-18 review). Head `add0aca` (2026-10-07). **This does NOT match PleaNP's `v4.31.0`** — and the gap has widened since this entry was written (was v4.30, now v4.35.0-rc3 + the rc toolchain + cslib). Import is **rejected** per DEC-025 (issue #70 Pass 1, 2026-09-13); the Rung-4 circuit substrate is built locally under `PleaNP.Circuits` (#71).
- **License:** Apache 2.0 (compatible with PleaNP).
- **What it has:** `P`, `NP`, `BPP`, `PSPACE` (plus `DTIME`/`NTIME`/`DSPACE`/`NSPACE`, `PPoly`/`PAdvice`, `RP`/`ZPP`/`PP`/`EXP`/`NEXP`/`SC`/`FNP`/`TFNP`); multi-tape-to-single-tape simulation; universal machines; the deterministic time-hierarchy theorem; a full Cook-Levin reduction (`SAT` is NP-complete) via computation tableaux; a typed Boolean-circuit model with size/depth, CNF/DNF, Shannon bounds, gate-elimination lower bounds, Schnorr's XOR lower bound, Valiant depth reduction; a logarithmic-cost RAM model; and a Fourier-analysis-of-Boolean-functions subtheory (O'Donnell ch. 1) — the analytic foundation for small-depth lower bounds and natural proofs.
- **What it explicitly lacks:** Oracle machines (the roadmap lists "oracle access" as needing common interfaces before headline equivalences can be stated), and **all three barriers** (relativization, natural proofs, algebrization) — code search confirms zero hits for `oracle`/`relativization`/`barrier`/`algebrization`. These are exactly PleaNP's gap.
- **PleaNP stance:** **Closed — do not import.** The 2026-08-18 attempt failed (below), and the drift has since widened to v4.35.0-rc3 + cslib, well past the point where repair or toolchain-matching is worth it for the small slice Rung 4 needs. Per **DEC-025** (2026-09-13, issue #70 Pass 1): build the Rung-4 circuit substrate locally under `PleaNP.Circuits` (#71). Not added to `lean/lakefile.lean`, and no longer proposed. Revisit only if complexitylib reconciles onto a stable toolchain that PleaNP pins, or upstream circuit machinery lands in Mathlib proper.

  **Reconciliation check (2026-08-18, attempted):** Added complexitylib (`dev` branch) to PleaNP's lakefile and built under Lean v4.31.0 / Mathlib v4.31.0. **Result: does NOT reconcile cleanly.** The build fails on ~23 of ~4033 modules with Mathlib API-drift errors (e.g. `Complexitylib.Mathlib.NatBits` — `simp made no progress`; `Complexitylib.Models.TuringMachine.Trace.Internal` — type-mismatch after simplification; failures in `Asymptotics`, `Circuits.Internal.Spira`, `Models.TuringMachine.*`, `DescriptiveComplexity.Reduction`, etc.). These are caused by `simp`-lemma and term-structure changes between Mathlib v4.30.0 (what complexitylib pinned then) and v4.31.0 (what PleaNP pins). **Superseded by DEC-025 (2026-09-13):** the fork is closed toward local `PleaNP.Circuits` build-out (#71); the reconciliation path is abandoned rather than revisited-on-bump, because complexitylib moved further away (v4.35.0-rc3 + cslib) rather than toward PleaNP's stable pin.

### 7. Reitwiessner — multi-tape + space-bounded model (Lean Together 2026)

- **Source:** talk slides `https://leaning.in/2026/slides/reitwiessner.pdf` — verified 2026-10-19: **HTTP 200** (the talk exists). Author's GitHub is `chriseth` (Christian Reitwiessner) — note the GitHub login is `chriseth`, **not** `reitwiessner` (a `reitwiessner` login returns 404). `chriseth` maintains a Mathlib fork (`chriseth/mathlib4`, fork, `master`, last push 2026-10-13) and `chriseth/complexity` (a standalone Lean complexity repo, default `main`, head `e23072e` 2026-02-01, `lean-toolchain` = `v4.27.0-rc1`).
- **Approach:** A multi-tape + space-bounded Turing-machine model. Per `docs/ROADMAP.md` Rung 2, this is *the only effort targeting space bounds*; `docs/ROADMAP.md` Rung 10 notes it also targets Williams's *Simulating Time With Square-Root Space* (STOC 2025, `arXiv:2502.17779`, verified 2026-10-19: HTTP 200).
- **Status (2026-10-19):** **Untracked until now** (ROADMAP-named, not previously in this doc). Talk delivered; code lives in `chriseth/complexity` (last commit 2026-02-01) and the `chriseth/mathlib4` fork. No upstream Mathlib PR identified. Not a released library.
- **PleaNP stance:** Track as the space-bounds axis. Do not duplicate the √-space target (ROADMAP Rung 10 excludes it). No import path until it lands upstream; watch only.

### 8. Keßler's Mathlib fork (Maximilian Keßler)

- **Source:** `https://git.abstractnonsen.se/max/mathlib4` — verified 2026-10-19: **unreachable from this environment.** DNS resolves (`git.abstractnonsen.se` → `195.52.50.237`) but both ports 80 and 443 are closed/filtered and HTTPS returns no response (curl exit 28/000). The fork's current status therefore **could not be re-verified from a primary source this run** — flagged, not asserted.
- **Approach:** A Mathlib fork with work on computability theory — formalizing the P and NP classes and proving facts about them (per `docs/PRIOR_ART.md`, quoting the fork README Feb 2026; progress notes on a public Hedgedoc pad).
- **Status (2026-10-19):** **Untracked until now** (ROADMAP-named, not previously in this doc). Last confirmed description is from 2026-08-18-era `PRIOR_ART.md`; the host is not reachable from the sandbox, so **no status change can be recorded** — this row is marked stale-unknown rather than silently carried forward.
- **PleaNP stance:** Track as a standalone formalization. No import path (it is a fork, not a released library); watch only. Re-verify when the host is reachable, or if the work surfaces as an upstream Mathlib PR.

### 9. `cslib` — Lean Computer Science Library (leanprover/cslib)

- **Source:** https://github.com/leanprover/cslib — verified 2026-10-28: **reachable**, default branch `main`, head `f4a4725` (2026-10-27, *"chore: support precompilation in bench suite (#1167)"*); `lean-toolchain` = `leanprover/lean4:v4.36.0-rc1` (an rc prerelease); latest release `v4.35.0` (2026-10-13). Apache-2.0. 209 `.lean` files under `Cslib/`. This is the successor effort #2 redirected to (closing comment on mathlib4 #33132, 2026-09-17).
- **Approach:** A general Lean CS library spanning `Algorithms`, `Computability`, `Crypto`, `Foundations`, `Languages`, `Logics`, `MachineLearning`, `Probability`, `Tactic`. Relevant here is `Cslib/Computability/`, whose README states its scope includes "automata, complexity classes, formal languages … and other machine models", with "multiple computational models" as an explicit design principle.
- **What it has (verified 2026-10-28):**
  - **Turing-machine models** under `Cslib/Computability/Machines/Turing/`: `Cslib/Computability/Machines/Turing/SingleTape/` (3 files — `Cslib/Computability/Machines/Turing/SingleTape/Defs.lean`, `Cslib/Computability/Machines/Turing/SingleTape/Deterministic.lean`, `Cslib/Computability/Machines/Turing/SingleTape/NonDeterministic.lean`; authors Fabrizio Montesi, Bolton Bailey, Pim Spelier, Daan van Gent) and `Cslib/Computability/Machines/Turing/MultiTape/` (20 files — `Cslib/Computability/Machines/Turing/MultiTape/Configuration.lean`, `Cslib/Computability/Machines/Turing/MultiTape/Deterministic.lean`, `Cslib/Computability/Machines/Turing/MultiTape/Nondeterministic.lean`, `Cslib/Computability/Machines/Turing/MultiTape/Space.lean`, plus a `Plumbing/` subtree; authors Christian Reitwiessner, Samuel Schlesinger, Aviv Bar Natan). The two trees are different author groups; the MultiTape group includes Christian Reitwiessner (`chriseth`), the same author as effort #7, so that effort's multi-tape + space-bounded model now also appears here.
  - **Polynomial-time computability:** `PolyTimeComputable` in `Cslib/Computability/Machines/Turing/SingleTape/Deterministic.lean`: "A Turing machine + a polynomial time function + a proof it outputs `f` in at most `time(input.length)` steps", with `id`, `comp`, and `withMonotoneBound`.
  - **Typed Boolean circuits** under `Cslib/Computability/Circuit/` (23 files): signatures/interpretations independent of gate basis, topological programs with designated output wires, plus `Cslib/Computability/Circuit/Complexity.lean` (`complexity`/`ecomplexity`, least gate count on a support), `Cslib/Computability/Circuit/RelativeComplexity.lean` (`C(f | g)`), `Cslib/Computability/Circuit/Boolean/Complexity.lean`, `Cslib/Computability/Circuit/Boolean/Shannon.lean`, `Cslib/Computability/Circuit/Boolean/Lupanov.lean`, `Cslib/Computability/Circuit/Depth.lean`, `Cslib/Computability/Circuit/Synthesis.lean`.
  - Also: automata (DA/NA/TwoWayNA/Büchi), `URM` register machines, `QueryComplexity/`, distributed `FLP`, and circuit `RelativeComplexity`.
- **What it explicitly lacks (verified 2026-10-28, code search + tree):** **no oracle machines and no relativization** — the only occurrence of "oracle" in `Cslib/` is an unrelated doc phrase in `Cslib/Foundations/Data/PFunctor/Free.lean`; grep for `relativiz` returns zero hits. **No P/NP complexity classes** — grep for `NP`, `PClass`, `ComplexityClass` returns no class definitions (only `PolyTimeComputable` and circuit complexity, which are machine/complexity-*measure* layers, not the classes). No Cook-Levin, no barrier theorems.
- **Toolchain:** `v4.36.0-rc1` — an rc prerelease, and five minor versions past PleaNP's stable `v4.31.0` pin (and one past complexitylib's `v4.35.0-rc3`, effort #6, whose `dev` branch now `require`s cslib). Re-verified 2026-10-28; the gap has widened since effort #2 was written.
- **PleaNP stance:** **Watch only — do not import.** cslib is the most active and most credible upstream machine-model effort (the #33132 redirect lands here, and the multi-tape model absorbs effort #7), so it is the right thing to *follow*. But it provides none of the layer PleaNP exists to build: no oracle machines, no relativization, no P/NP classes. Its toolchain is an rc five minors ahead of PleaNP's stable pin, so importing would repeat the complexitylib trade (DEC-025) — and cslib is itself now a dependency of complexitylib, so the two efforts are converging rather than giving PleaNP a cleaner option. No import decision is made here — per the issue, a stance-changing fact is reported rather than decided. Revisit if cslib pins a stable toolchain that PleaNP tracks **and** lands oracle-machine or P/NP content.

---

## What none of the upstream efforts provide

This is PleaNP's gap to fill, regardless of which model lands:

- **Time-bounded oracle computation.** Mathlib already has *oracle computability* — `Mathlib/Computability/RecursiveIn.lean` (Duve/Roth, 2025) defines `Nat.RecursiveIn O f` (a function partial-recursive given an oracle set `O`), the recursion-theoretic substrate. But this is *unbounded-time*. What relativization (Baker-Gill-Solovay) needs is a machine with an oracle tape answering a fixed function in one step **under a polynomial time bound** — i.e. `P^A` / `NP^A`. None of #35366, #33132 (now closed), descriptive-complexity, Simas, `RecursiveIn`, complexitylib, Reitwiessner's model, Keßler's fork, or `cslib`'s machine models provide this time-bounded oracle-machine layer (complexitylib's own roadmap flags oracle access as unfinished).
- **Oracle complexity classes** (P^A, NP^A) and oracle-separation results (Baker-Gill-Solovay).
- **The barrier theorems themselves** (natural proofs, algebrization) — none of these efforts touch them.
- **Circuit complexity** (AC⁰, TC⁰, NC) and **proof complexity** (resolution, Frege).
- **Cryptographic primitives for natural proofs** (one-way functions, pseudorandom function families) — code search of Mathlib master confirms none exist (see `docs/GAP_AUDIT.md` §6, open question 1).

---

## Decision rules for PleaNP

1. **Do not define P, NP, or reductions locally.** Import from whichever upstream effort lands first in Mathlib core.
2. **Do define oracle machines locally** (under `PleaNP.Barriers.Relativization` or a dedicated `PleaNP.Oracles` namespace), since no upstream effort provides them.
3. **Track the computational-model choice.** When P/NP lands in Mathlib, record the chosen model in `docs/decisions/LOG.md` and update this document.
4. **If the chosen model makes oracle-machine definition painful**, evaluate the synthetic approach (Church's Thesis as axiom) as a fallback — per the Coq precedent, it dramatically lowers overhead.

---

## Naming

PleaNP uses the `PleaNP.*` namespace for all project-specific declarations, *not* `Complexity.*`. The `Complexity` namespace is being actively designed by the Mathlib community; claiming it would conflict with upstream and misrepresent PleaNP's role (we formalize barriers, not complexity classes).
