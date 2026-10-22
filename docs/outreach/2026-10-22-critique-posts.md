# Critique post drafts: Lean Zulip (formalization) and theory venue (barrier statements)

**Task:** #211 (traces to #210, critique outreach).
**Status:** Drafts only. **No external contact has been made.** Posting is an
owner step and is fenced below.
**Purpose:** invite hostile review of PleaNP's barrier infrastructure from the
two audiences equipped to give it — the Lean Zulip on the formalization, and the
theoretical CS community on the barrier statements.

**Provenance of the content:** the questions and the framing come from #210. The
figures come from the repo records, each traced in the table at the end. Nothing
here is asserted beyond what the repo can be checked against.

---

## Owner-only steps (NOT agent work)

- Post Part A under the owner's Lean Zulip account and answer responses.
- Post Part B under the owner's account on the chosen theory venue and answer
  responses.
- Log substantive critique into the decision record, with any statement-level
  mismatch treated as a specification defect, not a disagreement.

The drafts below are copy-paste ready. Suggested subject lines are given; the
rest is the body.

---

# Part A — Lean Zulip (formalization audience)

**Suggested subject:** `Machine-grounded barrier infrastructure (BGS, Razborov–Rudich, algebrization): statements frozen, no barrier theorem proved — critique wanted`

---

Hi all — I'd like hostile review of a formalization project before I spend more
time on it. It is a Lean 4 / Mathlib repo, `PleaNP`, that tries to build
machine-checked *infrastructure* for the P vs NP barriers. I want to be clear up
front about what is and is not done, because the honest status is the credibility
asset here, not a footnote.

**The claim under critique.** The P vs NP barrier theorems — relativization
(Baker–Gill–Solovay 1975), natural proofs (Razborov–Rudich 1994), algebrization
(Aaronson–Wigderson 2009) — have no machine-checked proof in any proof assistant.
PleaNP is building the machine-grounded infrastructure that would make such proofs
*statable and checkable*: oracle-relative complexity classes over a real Turing
machine step function, with the barrier statements frozen as exact specs and every
admitted gap listed. **No resolution of P vs NP is claimed, and no barrier theorem
is proved yet.**

**What is machine-checked (zero `sorry`).**

- The oracle/class substrate: `P_A ⊆ NP_A` relative to an arbitrary oracle, proved
  in both directions, with oracle determinism (`evalsTo_unique_result`). The
  BGS diagonalization substrate (`DiagonalUB.lean`) is zero-`sorry`.
- Tier-2 axiom check (`#print axioms`) on these proofs returns only
  `{propext, Classical.choice, Quot.sound}` — the trusted Mathlib-standard set,
  no `sorryAx`.

**What is not done — stated plainly.**

- **No barrier theorem is proved.** Relativization is the statement root with two
  tracked `sorry` placeholders; the diagonal assembly scaffold carries one; the
  upstream-`P` anchor carries one. Four open `sorry` sites in total, each listed
  in `docs/SORRY_TRACKER.md` with what it is pending on, and machine-checked
  against the code by `sorry_tracker_scan.py`.
- **`P^∅ = P` compatibility is open.** `P_A`/`NP_A` are PleaNP-local classes; the
  connection to any upstream P/NP has not landed, so "whose P and NP?" currently
  answers "a local oracle-machine class, not yet connected upstream."
- **`#barrier_check` soundness is unproven.** The `Relativizing` typeclass and
  `#barrier_check` elaborator classify a claim as `DEAD` ("this proof
  relativizes") — but the theorem that a `Relativizing` construction truly
  relativizes in the BGS sense is itself an open target. There is a partial
  semantic model (`UniformInOracle`) with soundness lemmas for the seeded atoms
  and the propagation grammar; the concrete `NP_A`/class-equality hook is a
  documented plan, not a proof.
- **The repo's own hostile gap analysis is `docs/GRANT_READINESS.md`.** It lists
  the holes by exposure, and it goes in this post rather than behind it.

**Questions for critics.**

1. `#barrier_check` classifies a claim by asking Lean's instance search for a
   `Relativizing` marker on the statement body, which propagates through the
   dependency closure. Is that propagation sound as stated, or are there proof
   patterns it misclassifies in either direction? The function-level
   equality/inequality atoms (`funeq`/`funne`) are deliberately unconditional —
   is that the right call, or does it make the DEAD verdict fire where it should
   not?
2. The barrier statements are frozen over machine-grounded classes. Do they match
   the published theorems closely enough that a proof of the frozen statement
   would count as a proof of the barrier — or is the rendering shape (existential
   vs universal oracle, set extensional equality vs witness, the concrete
   `List Bool` query type) already a different theorem?
3. Read as a hostile reviewer: which gap in `docs/GRANT_READINESS.md` is fatal,
   and which are cosmetic?

Repo: `github.com/philipdallen/PleaNP` (branch `main`). The status line in
`README.md` and `docs/SORRY_TRACKER.md` are the ones to check me against. Thanks
in advance for the unkind parts.

---

# Part B — theory venue (CS Theory Stack Exchange or MathOverflow)

**Audience:** the barrier statements themselves, not the Lean mechanics.
**Suggested title:** `Are these frozen statements of the relativization, natural-proofs, and algebrization barriers faithful enough that a machine-checked proof would count?`

---

**Context.** The P vs NP barrier theorems — relativization, natural proofs,
algebrization — are, as far as I can tell, not machine-checked in any proof
assistant. What exists is weaker: statements of the BGS shape carried as `axiom`
over classes that constrain nothing, or abstract schemes with no machine model.
I've been building the machine-grounded version in Lean: oracle-relative classes
over a real step-counted Turing machine, with the barrier statements written out
exactly and the gaps tracked.

**The state of the art, honestly.** The oracle/class foundation is done and
zero-`sorry` (`P^A ⊆ NP^A` both directions, oracle determinism). **Zero barrier
theorems are proved.** The three barrier statements are frozen as specs; the
proofs are the roadmap. So what I have is a claim about *statability*, and I want
that claim attacked before I build further on it.

**The three frozen statements, and where I think they can be wrong.**

- **Relativization (BGS 1975).** Two clauses: (a) there exists a computable oracle
  `A` with `P^A = NP^A`; (b) there exists a computable oracle `B` with
  `P^B ≠ NP^B`. The Lean renders the oracle as existential and total (a
  `List Bool → Bool` function answering in one step), with an explicit
  `Computable` hypothesis on each witness — without it, clause (a) is trivially
  true and the statement is vacuous. `P^A = NP^A` is *set extensional* equality
  of two language classes, not a witness relation.
- **Natural proofs (Razborov–Rudich 1994).** A conditional theorem: under the
  existence of sufficiently hard one-way functions / pseudorandom function
  families, no property that is both constructive (decidable in polynomial time in
  the truth-table size) and large (a random function has it with non-negligible
  probability) can be useful against `P/poly`. The hardness assumption enters as a
  *hypothesis*, not as an imported definition — no importable Lean/Coq/Isabelle
  OWF/PRF substrate exists.
- **Algebrization (Aaronson–Wigderson 2009).** Pinned to the original
  multiquadratic formulation (the ITCS 2026 multilinear refinement is tracked as a
  candidate v2, deliberately not folded in). The relevant shape is an
  `(A, Ã)` pair — an oracle and a low-degree extension of it — with
  `NP^A ⊄ P^Ã`, the analogue of BGS clause (b). Depends on the relativization
  work plus a finite-field extension construction.

**Questions for critics.**

1. Is `Relativizing` propagation through a proof's dependency closure sound as
   stated, or are there proof patterns `#barrier_check` misclassifies in either
   direction?
2. Do the frozen barrier statements over machine-grounded classes match the
   published theorems closely enough that a proof would count?
3. Read as a hostile reviewer: which gap in the repo's own gap analysis is fatal,
   and which are cosmetic?

Repo: `github.com/philipdallen/PleaNP`. The statements are in
`docs/STATEMENTS/`; the gap analysis is `docs/GRANT_READINESS.md`.

---

## Trace table — every figure in the drafts

| Figure / claim | Record |
|---|---|
| No machine-checked proof of the three barriers in any proof assistant | `docs/PRIOR_ART.md` §"Closer prior art" and final findings; `README.md` |
| `P^A ⊆ NP^A` proved, both directions, zero-`sorry` | `lean/PleaNP/Computability/OracleComplexity.lean` (`P_A_subset_NP_A`); `README.md` status note |
| Oracle determinism `evalsTo_unique_result` | `lean/PleaNP/Computability/Oracle.lean`; `docs/SORRY_TRACKER.md` |
| BGS diagonalization substrate zero-`sorry` (`DiagonalUB.lean`) | `docs/SORRY_TRACKER.md` (RESOLVED 2026-09-13) |
| Axiom fingerprint `{propext, Classical.choice, Quot.sound}`, no `sorryAx` | `docs/SORRY_TRACKER.md` §"Tier-2 axiom check" |
| Four open `sorry` sites | `docs/SORRY_TRACKER.md` (Total: 4 open); `grep -rn '^\s*sorry\s*$' lean/PleaNP/` |
| Relativization = 2 `sorry` (statement root), DiagonalAssembly = 1, OracleUpstreamP = 1 | `docs/SORRY_TRACKER.md` detailed inventory |
| `P^∅ = P` compatibility open; local classes not connected upstream | `docs/GRANT_READINESS.md` §1 and §2 |
| `#barrier_check` soundness unproven; partial `UniformInOracle` model | `lean/PleaNP/Calculus/Soundness.lean` header; `docs/GRANT_READINESS.md` §4 |
| `Relativizing` propagates through the dependency closure | `lean/PleaNP/Calculus/BarrierCalculus.lean` header |
| Unconditional `funeq`/`funne` atoms | `lean/PleaNP/Calculus/BarrierCalculus.lean` header |
| BGS clause shape: existential, total, computable oracle; set extensional equality; `List Bool` query type | `docs/STATEMENTS/Relativization.md` §3; `lean/PleaNP/Barriers/Relativization.lean` (traps 1–3) |
| Natural proofs: conditional on OWF/PRF; constructive + large + useful; no importable substrate | `docs/STATEMENTS/NaturalProofs.md` §1, §2, §3 |
| Algebrization: multiquadratic v1 pin; `(A, Ã)` shape; `NP^A ⊄ P^Ã` | `docs/STATEMENTS/Algebrization.md` §1 |
| Prior renderings stop at axioms / vacuous classes / abstract schemes | `docs/PRIOR_ART.md` §"Closer prior art" (gobbleyourdong, konard, Coq neighbors) |
| Barriers formalized on paper in bounded arithmetic (Razborov 1995 et al.) | `docs/PRIOR_ART.md` |

## Claim check (required by the issue)

Every number in the drafts was checked against its source record above. The
machine checks run for this task:

```
$ python3 tooling/gates/sorry_tracker_scan.py
SORRY_TRACKER scan clean: tracker matches lean/PleaNP/ (sites + counts).

$ grep -rn '^\s*sorry\s*$' lean/PleaNP/ --include=*.lean
lean/PleaNP/Computability/OracleUpstreamP.lean:32:  sorry
lean/PleaNP/Barriers/Relativization.lean:89:  sorry
lean/PleaNP/Barriers/Relativization.lean:110:  sorry
lean/PleaNP/Barriers/DiagonalAssembly.lean:105:  sorry

$ grep -c '^\s*sorry\s*$' lean/PleaNP/Computability/Oracle.lean \
    lean/PleaNP/Computability/OracleComplexity.lean \
    lean/PleaNP/Computability/OracleSmoke.lean \
    lean/PleaNP/Barriers/DiagonalUB.lean \
    lean/PleaNP/Challenges/Relativization.lean
0
0
0
0
0
```

**Drift found: none.** The four open `sorry` sites match `docs/SORRY_TRACKER.md`
exactly, and the zero-`sorry` modules the drafts cite are zero-`sorry` on `main`.
The one number in #210's framing that the drafts deliberately *avoid* repeating is
"no `sorry`" stated for the whole repo — the correct statement is "the substrate
is zero-`sorry`; four tracked `sorry` sites remain", which is what both drafts
say.

## Notes for the owner

- The Zulip post is written to invite unkind review; the `#barrier_check`
  soundness gap and the local-class caveat are stated before they can be found.
- Part B is aimed at the statements, not the tooling, so it stands alone if you
  would rather not post the Lean side at all.
- If critique lands, the logging step in #210 turns any statement-level mismatch
  into a specification defect — the drafts say so explicitly so a critic knows the
  repo will treat disagreement as a bug report.
