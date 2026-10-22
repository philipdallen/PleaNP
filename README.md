# PleaNP

A Lean 4 / Mathlib project building machine-checked infrastructure for the **barrier landscape** of computational complexity theory — the meta-theorems showing which classes of proof techniques *provably cannot* resolve the P vs NP problem — together with the surrounding circuit complexity and proof-complexity infrastructure those barriers require.

> "Plea" — because this is the road we're building toward P vs NP, not the claim we've reached it.

> **Status — oracle + BGS substrate zero-`sorry`; no barrier theorem proven.**
> A statement catalogue with a working substrate, not a proof library. The oracle substrate
> (`P^A ⊆ NP^A`, both directions) and the BGS diagonalization substrate are machine-checked and
> zero-`sorry`. Relativization is a frozen statement carrying 2 tracked `sorry`s; algebrization
> is rendered as statement definitions with no theorem yet; natural proofs is scoped in design
> docs with no Lean artifact yet.
>
> This block is a **rolling summary, not a dated snapshot**, so it cannot go stale: the live
> figures are machine-derived. Read [`docs/SORRY_TRACKER.md`](docs/SORRY_TRACKER.md) for the
> `sorry` ledger (every `sorry` in `lean/PleaNP/` must appear in its table, so it is checked
> against the code) and [`docs/GRANT_READINESS.md`](docs/GRANT_READINESS.md) for the frank gap
> analysis of what exists versus what a reviewer will ask for.

## At a glance

- **Building the missing infrastructure for proofs no one has machine-checked yet**: the P vs NP barrier theorems (relativization, natural proofs, algebrization) have no formal proof in any proof assistant. The machine-grounded oracle/class foundation is complete and zero-`sorry`; the barrier statements are frozen as specs, with the proofs as tracked open work.
- **A "barrier calculus"**: a `Relativizing` typeclass + `#barrier_check` elaborator that turns "does this proof relativize?" from human judgment into a typechecking question — unit-tested against the time hierarchy theorem.
- **A lower-bound compiler**: Williams' transfer theorem as a Lean elaborator (verify an algorithm + runtime bound → get a circuit lower bound), plus the supporting circuit- and proof-complexity library.

> Full background below, or jump to [scope & non-scope](#scope-and-non-scope).
>> **Built with agentic AI tooling.** The author specified the architecture, the scope, and the integrity gates that audit AI-produced claims; agent-based coding workflows produced and iterated on the Lean formalizations. The author is not a Lean specialist — the repo's own gates (hygiene, vacuity, model-consistency, lethality, `#barrier_check`) are what make the artifact auditable rather than trusted. See commit history and [`docs/CONTRIBUTIONS.md`](docs/CONTRIBUTIONS.md).


## Why this project exists

The P vs NP problem has three decades of known **barriers**:

| Barrier | Year | Core message |
|---|---|---|
| Relativization | Baker–Gill–Solovay, 1975 | Any relativizing proof cannot separate P from NP (oracles exist on both sides). |
| Natural proofs | Razborov–Rudich, 1994 | Natural lower-bound techniques would break pseudorandom functions / one-way functions. |
| Algebrization | Aaronson–Wigderson, 2008 | A third barrier refining the first two, covering modern lower-bound techniques. |

These barriers are the map of where P vs NP proof attempts fail. Encoding them formally turns "don't try these techniques" from folklore into machine-checkable facts — which is the prerequisite for any honest, AI-assisted proof search over the formalized landscape.

**None of these barriers has a machine-checked proof in any proof assistant, in any computational model.** (They've been stated as axioms and sketched as abstract schemes — see `docs/PRIOR_ART.md` — but never proved over real machine-grounded classes.) This project is building the missing infrastructure: machine-grounded oracle classes — done — with the barrier theorems on top still open. The statements are now *statable* over real machine-grounded classes, which is the prerequisite for proving them and was itself absent before.

## Scope and non-scope

### In scope

- A **barrier library** — currently a frozen statement catalogue (relativization, natural proofs, algebrization); the proofs are tracked open work, per the status note above.
- A **barrier calculus** (Rung 5, the crown jewel): a `Relativizing` typeclass that propagates through the dependency graph of any lemma built from relativizing pieces, plus a `#barrier_check` elaborator that walks a theorem's dependency closure and reports **"DEAD: this proof relativizes"** or **"Inconclusive."** — turning "does this proof relativize?" from per-paper human judgment into a typechecking question. Unit-tested against the time hierarchy theorem (which relativizes).
- An **anchor object** (Rung 6): machine-checked P/NP model-equivalence across whichever upstream formalizations land, plus Levin universal search as an explicit `#eval`-able term behind `P_eq_NP_iff`. The search⟶decision gap (needs self-reducibility + a Hutter-style wrapper) is logged as a scoped open lemma, not a blocker (see DEC-012).
- A **lower-bound compiler** (Rung 8): Williams' transfer theorem (nontrivial CircuitSAT algorithm for class C ⟹ NEXP ⊄ C) as a Lean elaborator — feed it a verified algorithm + runtime bound, it emits a verified circuit lower bound. Under `PleaNP.Barriers`, with the elaborator command `#lower_bound_compile`.
- Supporting **circuit complexity** (AC⁰, switching lemma, monotone bounds; TC⁰ and NC specified but not yet implemented) and **proof complexity** (resolution; Frege specified but not yet implemented) needed to state and apply the barriers.
- An **integrity pipeline** (the "gates") that separates statement formalization from proof search, to structurally prevent the most common failure mode of claimed P vs NP formalizations.

### Out of scope (deliberately)

- Defining P, NP, and polynomial-time reductions from scratch. These are being actively upstreamed to Mathlib by multiple efforts (see `docs/UPSTREAM_TRACKING.md`). PleaNP imports and builds on whichever lands, rather than contesting the computational-model design.
- Claiming to resolve P vs NP. The realistic outcome is a world-class formalized barrier library plus honest tooling — a serious contribution regardless of whether the top rung is ever reached.

## Project structure

```
PleaNP/
├── lean/                # Self-contained Lean 4 / lake project (the library)
│   ├── PleaNP/
│   │   ├── Computability/  # Rung 2: oracle machines, P^A / NP^A, smoke tests
│   │   ├── Barriers/    # Relativization, algebrization (Lean); natural proofs specified, no module yet
│   │   ├── Calculus/    # Rung 5: Relativizing typeclass + #barrier_check
│   │   ├── Circuits/    # AC0, switching lemma, monotone bounds
│   │   ├── ProofComplexity/  # Resolution
│   │   ├── Challenges/  # Comparator-challenge modules (not imported by the root)
│   │   └── Benchmark/   # Graded benchmark scaffolding
│   └── tests/
├── tooling/             # AI + integrity layer (Python)
│   ├── gates/           # The integrity pipeline (scanners + specs + fixtures)
│   ├── galaxy/          # formalization.yaml -> galaxy.html renderer
│   └── reviews/         # Review-inbox sync (src/reviews/)
└── docs/                # The spec, roadmap, audit, and decision log
```

The `lean/` tree is a clean lake project with no Python dependencies — it can be extracted and contributed upstream independently.

## Current status

See `docs/ROADMAP.md` for the full rung ladder and `docs/SORRY_TRACKER.md`
for the live `sorry` ledger.

- **Rung 1 — Gap audit: done.** `docs/GAP_AUDIT.md` is the domain-by-domain
  analysis of Mathlib's current complexity coverage versus what the barrier
  theorems require, plus the upstream efforts PleaNP tracks.
- **Rung 2 — Oracle substrate (partly landed).** The oracle-machine and
  complexity-class layer lives in `lean/PleaNP/Computability/`: `Oracle.lean`,
  `OracleComplexity.lean`, and `OracleSmoke.lean` build green with zero
  sorries (the v5 word-query repair, DEC-024). `OracleUpstreamP.lean` carries
  one tracked, honest `sorry` — the upstream-P-blocked bridge, isolated in its
  own module so nothing else depends on it. The `P^A ⊆ NP^A` self-check is
  proved in both directions.
- **Rung 3 — Barrier theorems: in progress.** The BGS diagonalization chain
  (`lean/PleaNP/Barriers/Diagonal*.lean`, ~20 modules) is built and
  `DiagonalUB.lean` is zero-sorry. `Relativization.lean` renders the frozen
  BGS statement with two tracked `sorry`s for the proofs;
  `Algebrization.lean` renders the AW09 statement with its consequence proofs
  in `AlgebrizationProof.lean` (zero-sorry). Natural proofs currently exists as
  statement/design specs only (`docs/STATEMENTS/NaturalProofs*.md`) — no Lean
  module yet. See the `sorry` ledger.
- **Rung 5 — Barrier Calculus: prototype landed.** The `Relativizing`
  typeclass and `#barrier_check` elaborator live in
  `lean/PleaNP/Calculus/`, unit-tested against the time-hierarchy theorem. It
  is meta-level — it does not wait on upstream P/NP.
- **Rung 6 — Anchor object: blocked on upstream.** Needs two landed P/NP
  formalizations before the equivalence anchor can be stated.
- **Rung 8 — Lower-Bound Compiler: skeleton landed.** Williams' transfer
  theorem is frozen as a statement in `Barriers/WilliamsTransfer.lean`, and the
  `#lower_bound_compile` elaborator skeleton (Pass 2) lives in
  `Barriers/LowerBoundCompiler.lean`; see its
  [`README`](lean/PleaNP/Barriers/LowerBoundCompiler.README.md). The genuine
  ACC⁰-structure packing (Shah–Shetty Good-SAT) remains a decomposed follow-up,
  not a `sorry`.

Rungs 4, 7, 9, 10, and 11 are not started.

**Packaging (DEC-027):** a root `lakefile.lean` repoints the package at `lean/`
so sibling repos can `require PleaNP from git`. `lean/` remains the
authoritative build tree (CI, the devcontainer, and `tooling/elantool.sh` all
run from it); the root file is additive and guarded by
`tooling/gates/lakefile_sync_check.py`.

**Community status (2026-09-06, DEC-015):** contributions are welcome via
GitHub issues/PRs (`docs/CONTRIBUTIONS.md`); the multi-agent issue workflow is
`docs/MULTI_AGENT_WORKFLOW.md`. The project is maintained by one human + AI
agents with machine-verified integrity gates. Participation in external chat
channels (e.g. Zulip) is deliberately deferred until the artifact is
stranger-pickupable and a human accountability anchor exists — the repo is
fully GitHub-native in the meantime.

## For newcomers

Want the plain-words version — no math background needed?
Read [`docs/EXPLAINER_P_VS_NP.md`](docs/EXPLAINER_P_VS_NP.md),
a beginner-friendly telling of P vs NP and how PleaNP approaches it.

Then read the project in this order:

1. [`docs/ROADMAP.md`](docs/ROADMAP.md) — the rung ladder: what is built, what is next, and what "done" means at each rung.
2. [`docs/GRANT_READINESS.md`](docs/GRANT_READINESS.md) — the frank gap analysis: what exists versus what a skeptical reviewer will ask for.
3. [`docs/SORRY_TRACKER.md`](docs/SORRY_TRACKER.md) — the live `sorry` ledger, checked against the Lean code.

## Conventions

This project follows Mathlib's naming and style conventions for all Lean code, with project-specific declarations under the `PleaNP` namespace. See `AGENTS.md` for the condensed project reference.

## Cite this work

Citation metadata lives in [`CITATION.cff`](CITATION.cff) (GitHub's "Cite this repository" uses it) and `.zenodo.json` (used if the owner enables the Zenodo GitHub integration).

## Acknowledgments

This project takes inspiration from the **Maith** project (a Lean 4 IR extraction experiment) in its documentation discipline (decision log, audit resolution markers, AGENTS.md memory) — but PleaNP is an independent formalization project, not a representation-research project.
