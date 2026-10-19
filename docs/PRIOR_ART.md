# Prior art: Lean-community discussions and related formalizations

**Purpose.** Record what the Lean community (Zulip archive, project listings) and adjacent formalization efforts have already done or discussed around computational complexity, oracle machines, and the three barriers. This grounds PleaNP's novelty claims and surfaces reusable substrate.

Searched: the Mathlib4 Zulip archive at `https://leanprover-community.github.io/archive/stream/287929-mathlib4/` (and adjacent streams) for: oracle machines, Baker-Gill-Solovay, natural proofs, algebrization, complexity barriers, complexitylib. Supplemented by a broad literature/repo review across Coq, Isabelle/HOL (AFP), and the AI proof-search landscape, to verify the headline "no barriers in any proof assistant" claim beyond the Lean Zulip. Last searched: 2026-08-18.

---

## Headline finding

**The three barriers are absent from the Lean Zulip archive.** Searches for "Baker-Gill-Solovay", "natural proofs", "Razborov-Rudich", "algebrization", and "Aaronson-Wigderson" across the archive (`leanprover-community.github.io`) return **no** threads discussing them as formalization targets. The only Zulip "oracle" discussions are (a) the `linarith` tactic's certificate *oracle* (unrelated) and (b) decidability-oracle thought experiments (Damiano Testa / Mario Carneiro, new-members stream, Mar 2021 — about noncomputable reals, not complexity).

This corroborates the gap audit's central observation: **the barrier theorems are open ground in every proof assistant, in every model.** A broad literature search beyond the Lean Zulip — over Coq, Isabelle/HOL (Archive of Formal Proofs), and the AI proof-search tooling landscape — surfaced **no machine-checked proof** of relativization, natural proofs, or algebrization in any proof assistant. The closest existing formalizations (Cook–Levin in Coq and Isabelle; oracle *computability* in Mathlib; circuit lower bounds in complexitylib) all stop short of the barriers. **Caveat (see "Closer prior art" below):** the barriers have been *stated* as axioms and *gestured at* as abstract schemes in a few repos, and *formalized on paper* in bounded arithmetic — so "open ground" means "no provable, machine-checked, machine-grounded rendering," not "nobody has written the words." We record this to keep the substrate map accurate, not to stake a novelty claim.

---

## Prior art found

### 1. Oracle Computability Theory (mathlib4 stream, Jan–Feb 2026)

**Thread:** `stream/287929-mathlib4/topic/Oracle.20Computability.20Theory.html` (39 messages, latest Feb 28 2026).

- **Edwin Park** formalized the Kleene-Post theorem and degree-theoretic foundations in `https://github.com/hyeoniuwu/CiL` (Lean, toolchain `v4.33.0-rc2`, no license, 2 stars). Includes the KP54 capstone proof. Proposes merging into Mathlib.
- **Material finding for PleaNP — a defect in Mathlib's `TuringReducible`/`TuringDegree`:** Park (Feb 17 2026) reports that Mathlib's current `TuringReducible` is defined over *partial functions*, which actually yields **enumeration degrees**, not true Turing degrees (which require *total*-function oracles). Park fixed it in CiL's `lean/PleaNP/Computability/Oracle.lean`.
- **Tanner Duve** (author of Mathlib's `Mathlib/Computability/RecursiveIn.lean` (upstream), tracked in `UPSTREAM_TRACKING.md`) responded: the current definition is a "strict generalization" and the issue is "misnaming rather than definitions being incorrect"; proposed renaming `TuringReducible` → `PartialReducible` and recovering the standard notion by lifting total functions via `Part.some`.
- **Mario Carneiro** (Feb 27 2026) weighed in: keep the general (partial) definition, since "getting the equivalent notion is much harder without it"; totality is "the responsibility of whatever derived notion writes a quantification over those functions."
- **Implication for PleaNP:** PleaNP's oracle-machine work should be aware that Mathlib's `RecursiveIn`/`TuringReducible` is the *partial* (enumeration-degree) notion. For relativization (`P^A`, `NP^A`), oracles are total by definition (they answer in one step), so PleaNP's oracle machines will compose with *total* oracles regardless of the Mathlib partial-general definition. No conflict — but the naming/totality distinction must be respected. **No rung scope change.**

### 2. Complexity theory in Lean — "Is there code for X?" (Jul 2021)

**Thread:** `stream/217875-Is-there-code-for-X%3F/topic/Complexity.20theory.html`.

- **Mario Carneiro** (Jul 13 2021): the existing computability material was "written with an eye for complexity theory" (future work in the arXiv paper), "but not much in that direction has landed yet." Notes **Pim Spelier has some unmerged complexity theory work on P and NP** (link dead).
- **Martin Dvořák:** planning a PhD on formalizing complexity theory in Lean.
- **Implication:** confirms the gap audit — as of 2021, Mathlib had computability but essentially no complexity. Pim Spelier's unmerged P/NP work is the earliest such effort known; its status is unverified (predates the tracked #35366 / #33132 efforts in `UPSTREAM_TRACKING.md`).

### 3. Computational Complexity Theory (general stream, Dec 2021)

**Thread:** `stream/113488-general/topic/Computational.20Complexity.20Theory.html`.

- Multi-month discussion (Martin Dvořák, Bolton Bailey, Mario Carneiro, Arthur Paulino, Dima Pasechnik) on a roadmap for complexity in Lean.
- Discusses the **Arora-Barak book** as a definitional source (same source complexitylib uses — see `UPSTREAM_TRACKING.md` §6).
- Debates the **λ-calculus L model** (Forster/Kunze Coq route) vs Turing machines; concludes the λ-calculus route is more ergonomic ("I don't even want to imagine a formalization using turing machines" — unnamed). A concrete 11-step roadmap is sketched (define P/NP/reductions/NP-completeness in L, Cook-Levin).
- **Dima Pasechnik** notes the "1st order reductions" alternative (descriptive complexity) — the Senellart axis tracked in `GAP_AUDIT.md` §9.
- **Implication:** corroborates the upstream-tracking finding that the computational-model choice is contested; the λ-calculus fallback is a live community option, not just a Coq precedent. **No rung scope change** — Rung 2 already tracks this as upstream-blocked.

### 4. Ph.D. on formalizing complexity classes (general stream, Aug 2021)

**Thread:** `stream/113488-general/topic/Ph.2ED.2E.20on.20formalizing.20complexity.20classes.html`.

- Martin Dvořák seeks PhD advice; Mario Carneiro and Johan Commelin caution that formalizing complexity is library-grinding ("80% of your time writing libraries that prove stuff covered in the first two introductory courses") and that some advisors don't value formalization as research.
- **Implication:** methodological, not technical. Relevant to PleaNP's positioning — the barrier-library framing (meta-theorems, not class definitions) is precisely the high-value framing that avoids the "trivial class library" trap.

### 5. Hunter Monroe PR #8931 — P/NP definitions without theorems (Gödel thread, Dec 2023)

**Thread:** `stream/113488-general/topic/G.C3.B6del's.20first.20incompleteness.20theorem.html`.

- **Hunter Monroe** proposed Mathlib PR #8931 with definitions of P, NP, NP-completeness, and poly-time reductions, *without theorems*. Stalled on the **encoding/alphabet question**: "With a unary alphabet, P=NP... With a sufficiently inefficient encoding, anything computable is in P."
- **Mario Carneiro** points to `Primcodable` as the canonical answer to the encoding problem.
- **Implication for PleaNP — directly relevant to Gate 2 (model-consistency):** the unary-alphabet trap ("if the encoding is unary, P=NP") is a concrete instance of the statement-fidelity failure mode the integrity architecture is designed to prevent. PleaNP's model-consistency gate must pin the encoding (via upstream `Primcodable`) to avoid this. **No rung scope change**, but it sharpens Gate 2's linter requirement.

### 6. Claimed NP = PSPACE formalization (general stream, "Lean in the wild", Aug 2019)

**Thread:** `stream/113488-general/topic/Lean.20in.20the.20wild.html`.

- **Floris van Doorn** (Aug 5 2019): reports an FOM mailing-list thread where someone claims to be formalizing a proof that NP = PSPACE in Lean; notes the claim is "widely suspected to be false."
- **Implication for PleaNP:** a textbook instance of failure-audit Pattern A (formalizing a statement that is almost certainly false, trusting the formalization as authority). Reinforces the necessity of the statement-fidelity gates. **No rung scope change** — it is evidence *for* the existing architecture, not against the rungs.

---

## Related formalization efforts (from Lean project listings)

### CSLib — The Lean Computer Science Library

- Listed at `leanprover-community.github.io/lean_projects.html` (★ 640). A general CS library for Lean, distinct from complexity theory per se. **Tanner Duve** (Oracle Computability thread) noted oracle/degree theory is "firmly within mathematics" and "isn't very related to the kind of cs theory that would go into cslib."
- **PleaNP stance:** not a complexity substrate. Monitor for incidental overlap only.

### Edwin Park's CiL

- `https://github.com/hyeoniuwu/CiL` — computability and degree theory (Kleene-Post, Turing degrees). Lean, toolchain `v4.33.0-rc2`, **no license** (blocks import until added), 2 stars.
- **PleaNP stance:** closest existing work to PleaNP's oracle substrate, but it's *computability* (unbounded) not *complexity* (bounded). Its corrected `TuringReducible` definition is a useful reference for the totality question. Not importable (no license, and it's degree theory, not barriers).

---

## Cross-assistant survey: are the barriers formalized anywhere?

To back the headline claim beyond the Lean Zulip, the literature review checked the other major proof-assistant ecosystems for any formalization of the three barriers. **None found.** The closest neighbors, and where they stop:

### Cook–Levin in Coq (Gäher & Kunze, ITP 2021) and Isabelle/HOL (Balbach, AFP)

- **Coq:** `Mechanising Complexity Theory: The Cook-Levin Theorem in Coq` (Gäher & Kunze, ITP 2021; `drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITP.2021.20`). Defines P, NP, poly-time reductions over the call-by-value λ-calculus L; proves SAT NP-complete. This is the precedent already tracked in `FAILURE_AUDIT.md` Pattern B and `UPSTREAM_TRACKING.md` §5.
- **Isabelle/HOL:** `The Cook-Levin Theorem` (Frank J. Balbach, Archive of Formal Proofs, `https://www.isa-afp.org/entries/Cook_Levin.html`, dated 2025). Multi-tape TMs, P, NP, `P ⊆ NP`, polynomial-time many-one reduction, SAT — following Arora–Barak. Notably, an Isabelle *re-derivation of Cook–Levin* motivated early Lean complexity discussion (Martin Dvořák / Shreyas Srinivas, Zulip `Computational Complexity Theory` thread, Jan 2023), concluding "we should replicate this work in Lean" with better modularity.
- **Where they stop:** both formalize *one* NP-completeness theorem. Neither touches oracle machines, `P^A`/`NP^A`, the Baker–Gill–Solovay construction, natural proofs, or algebrization. Cook–Levin is the *famous* theorem; the barriers are the *anti-pattern library* nobody has built (per `FAILURE_AUDIT.md`, "What is NOT in the record").

### The original barrier papers (the informal source of truth)

PleaNP formalizes informal theorems, so the primary sources are the canonical references for the statement-to-informal mapping (Gate 4 read-back). They were not previously cited in this document:

- **Relativization:** Baker, T., Gill, J., Solovay, R. *Relativizations of the P =? NP Question.* SIAM J. Comput., 4(4):431–442, 1975.
- **Natural proofs:** Razborov, A., Rudich, S. *Natural Proofs.* J. Comput. System Sci., 55(1):24–35, 1997 (STOC '94; Gödel Prize 2007).
- **Algebrization:** Aaronson, S., Wigderson, A. *Algebrization: A New Barrier in Complexity Theory.* ACM TOCT, 1(1), 2009 (STOC '08; ECCC TR08-005).

### Recent theoretical refinements to watch (not formalization, but moving targets)

These are informal results that refine or extend the barriers. They matter for PleaNP because (a) they are candidate targets *beyond* Rung 3, and (b) they show the barrier landscape is still active — a formalization must pin a specific, dated statement, not a moving folk theorem:

- **New algebrization barriers via communication complexity (ITCS 2026).** *New Algebrization Barriers to Circuit Lower Bounds via Communication Complexity of Missing-String* (`drops.dagstuhl.de/.../LIPIcs.ITCS.2026.37`). Strengthens Aaronson–Wigderson's multiquadratic-extension barrier to *multilinear* extensions via the XOR-Missing-String problem. **Implication for PleaNP:** Rung 3c (algebrization) should pin the *original* AW09 multiquadratic formulation as the v1 target and track this ITCS 2026 result as a candidate strengthening — not fold it into the v1 statement, since it postdates the canonical barrier. No rung rewrite; a scoping note.
- **"Semi-relativization" / diagonalization-without-relativization (arXiv:2601.09702, Jan 2026).** Baruch Garcia, *Diagonalization Without Relativization: A Closer Look at the Baker-Gill-Solovay Theorem.* Argues a "semi-relativized" diagonalization (oracle fixed to the acceptance problem) evades all three barriers. **Implication for PleaNP:** this is exactly the kind of claimed barrier-evasion argument that Rung 8 is scoped to evaluate through the gates — and, per `FAILURE_AUDIT.md`, it must not be formalized by the same pipeline that searches its proof. Treat as a *test case for the integrity architecture*, not as established mathematics. No rung scope change; it sharpens what "done" means at Rung 8 ("gate-validated," not merely "compiles").
- **Williams, *Simulating Time With Square-Root Space* (STOC 2025, Best Paper; arXiv:2502.17779).** Not a barrier result, but the most consequential recent complexity theorem: `DTIME(t) ⊆ DSPACE(√(t log t))`, beating the 50-year Hopcroft–Paul–Valiant bound. Relevant to PleaNP in two ways: (1) it is *below* P vs NP (a Rung-7-class derandomization/structure result) and is itself now a formalization target in Lean (see Reitwiessner below); (2) it interacts with the algebrization barrier (any P ≠ PSPACE proof must be non-algebrizing, and this result is a candidate ingredient).

---

## New Lean complexity efforts (added to the tracked landscape)

The literature review surfaced two Lean 4 efforts not previously in `UPSTREAM_TRACKING.md`. They belong there too; recorded here first because they bear on Rung 2's "which model lands" question.

### Reitwiessner — formalizing space-bounded complexity in Lean (Lean Together 2026)

- **Talk:** Christian Reitwiessner, *Formalizing (space) complexity theory in Lean* (`leaning.in/2026/slides/reitwiessner.pdf`, Lean Together 2026).
- **Approach:** Extends Mathlib's single-tape `TM` to a *multi-tape* version, on top of which he builds a toolbox of computation primitives and composition connectives for reasoning about space *and* time. The motivating horizon goal is to formalize **Williams's 2025 *Simulating Time With Square-Root Space*** result.
- **Implication for PleaNP:** Two-fold. (a) This is a *fourth* candidate computational-model substrate for Rung 2 (alongside #35366, #33132, and complexitylib) — and notably the only one explicitly targeting *space* bounds, which the time-focused efforts lack. PleaNP's relativization work is time-bounded, so Reitwiessner's multi-tape + space model is a candidate base if it lands. (b) Williams's √-space result is already a Lean formalization target *by someone else* — meaning PleaNP's Rung 7 (open problems below P vs NP) should not duplicate it; it should *track* Reitwiessner's effort and pick a different open problem. **Action: add to `UPSTREAM_TRACKING.md` as effort #7.** No rung rewrite, but Rung 2's "watch list" grows and Rung 7 should de-scope the √-space theorem.

### Keßler — Mathlib fork formalizing P and NP

- **Repo:** Maximilian Keßler's Mathlib fork (`git.abstractnonsen.se/max/mathlib4`), README (Feb 2026): "Currently working on computability theory, trying to formalize the P and NP classes and proving some facts about them." Progress notes at a public Hedgedoc pad.
- **Implication for PleaNP:** Corroborates that the P/NP substrate is contested across *at least* five independent efforts now (#35366, #33132, descriptive-complexity, Simas, complexitylib, plus Reitwiessner and Keßler). Reinforces DEC-003 (import, don't define). **Action: add to `UPSTREAM_TRACKING.md` as effort #8.** No rung scope change.

---

## Cryptographic-primitive substrate for natural proofs (Rung 3b prerequisite)

The gap audit (`GAP_AUDIT.md` §6, open Q1) resolved that Mathlib has *no* one-way-function / pseudorandom-function infrastructure. The literature review checked whether any *other* Lean/Coq/Isabelle library provides an importable substrate for the natural-proofs prerequisites (OWF, PRG, PRF) so that Rung 3b doesn't build them from scratch:

- **EasyCrypt** (Coq-based, for game-based cryptographic proofs) and the **Foundational Cryptography Framework** are the mature formal crypto frameworks, but they are Coq-ecosystem and define primitives in a *proof-of-security* idiom (game-hopping), not as the bare complexity-theoretic objects (`OWF : Nat → Nat` with an inversion-hardness predicate) that Razborov–Rudich's "natural property" statement quantifies over. They are not directly importable into Lean.
- **No Lean 4 formalization of one-way functions or pseudorandom function families** surfaced. complexitylib (tracked) has `BPP`/`PP`/probabilistic classes but, per `UPSTREAM_TRACKING.md`, code search confirms no OWF/PRF.
- **Implication for PleaNP:** Rung 3b's prerequisite ("build OWF/PRFF substrate") cannot be shortcut by importing an existing crypto library — the gap audit's "build from scratch" conclusion stands. The natural-proofs barrier formalizes over a *hardness assumption* (OWFs exist with exponential hardness), which is itself an unproven conjecture; PleaNP will formalize the **conditional** (OWF exists ⟹ no natural property gives superpoly lower bounds), so the OWF enters as a *hypothesis*, not a constructed object. This is a meaningful simplification of Rung 3b's scope: PleaNP does **not** need to construct a PRF, only to state the conditional cleanly. **Suggests a clarification to Rung 3b's "done" criterion** (see Rung-scope notes below).

---

## AI proof-search / autoformalization landscape (Rung 6 context)

Rung 6 sits on top of a fast-moving tooling landscape. The failure audit (Pattern C) already flags the integrity risk; this section records the *current* tooling so Rung 6's design references real systems, not strawmen. This is prior art for the *tooling* layer, not the *mathematics*.

- **LeanDojo + ReProver** (Yang et al., NeurIPS 2023; `leandojo.org`). Open-source Lean interaction toolkit + retrieval-augmented prover. Premise selection is the named bottleneck (Recall@1 ≈ 9–13%); the `novel_premises` split is the honest eval. **Relevance to Rung 6:** the canonical premise-selection substrate to build on or benchmark against; also LeanDojo Benchmark 4 (2026) added an autoformalization track with a `proof-check success rate` metric — directly measuring the statement-fidelity problem PleaNP's Gate 3/4 exists to prevent.
- **Lean Copilot** (`leandojo.org/leancopilot.html`). Human-in-the-loop tactic/premise/search assistance. The non-adversarial design point — useful for Rungs 3–5 (human-strategy + AI-tactics), explicitly *not* the Rung 6 adversarial case.
- **AlphaProof** (DeepMind, IMO 2024 silver-medal equivalent; Nature, Nov 2025). AlphaZero-style RL over Lean 4, Monte-Carlo graph search with product nodes, test-time RL. **Relevance:** demonstrates that formal search at scale produces kernel-checkable output, but its statements are *competition problems* (already-correct, already-formalized) — the exact setting where Pattern C says AI is safe. Rung 6's integrity challenge is precisely the *opposite* setting (AI also touches the statement).
- **The broader 2025–2026 prover wave:** DeepSeek-Prover-V2, Goedel-Prover-V2, Kimina-Prover, BFS-Prover, HunyuanProver, InternLM2.5-StepProver, FormaRL, Seed-Prover, Gauss AI — all benchmarked on MiniF2F-class *already-correct* statements. None is built for the adversarial statement-fidelity case.
- **Autoformalization robustness (2026, already in `FAILURE_AUDIT.md` Pattern C):** LeanDojo Benchmark 4 quantifies that current autoformalizers are not faithful under paraphrase (exact-match < 10%, proof-check < 20%). This is the measured version of the risk Gate 4 (read-back) exists to block.
- **Implication for PleaNP:** Rung 6 should (a) build its premise-selection on LeanDojo/ReProver or explicitly justify diverging, (b) use LeanDojo Benchmark 4's autoformalization metrics as the *measured* threat model for Gates 3–4, and (c) treat the 2025–2026 prover wave as evidence that *search* is maturing faster than *statement integrity* — which is exactly why PleaNP's contribution (the barrier library + the gates) is timely. **No rung rewrite**; sharpens Rung 6's "done" criterion to reference these concrete baselines.

---

## Closer prior art (added 2026-08-19; corrects the over-broad "none found" claim)

A deeper sweep (GitHub code search across Lean/Coq/Isabelle, Reddit, CS Theory SE, MathOverflow, the complexity blogs, AFP, Metamath, and the bounded-arithmetic literature) surfaced prior art the earlier review missed. **None of it invalidates the project — the barriers remain unproven in every proof assistant — but three repos and one research tradition must be cited so the "what exists" map is accurate.** This matters for *substrate decisions* (what we build vs. import), not for staking a claim.

### GitHub repos with barrier *renderings or interfaces* (none are theorems over real classes)

- **`gobbleyourdong/open_problems` (Lean, Jun 2026).** `math/p_vs_np/lean/Barriers.lean` literally contains BGS statements — but as **axioms**, not theorems (`axiom bgs_exists_equal : ∃ A : Oracle, ...`), over **vacuous** classes (`InP_rel`/`InNP_rel` end in `∧ True` and never define polynomial time). This is the closest prior *rendering* of the BGS statement shape — and a textbook FAILURE_AUDIT Pattern A instance (a statement assumed, over classes that constrain nothing).
- **`khanukov/p-np2` (Lean, active).** A `pnp3/Barrier/` directory with `lean/PleaNP/Barriers/Relativization.lean`, `lean/PleaNP/Barriers/NaturalProofs.lean` (to be created), `lean/PleaNP/Barriers/Algebrization.lean` (to be created) — but these are **abstract schemes**, not theorems: `Relativizing (S : Type u → Prop) := ∀ O₁ O₂ : Type u, S O₁ ↔ S O₂` where the "oracles" are bare types. Zero oracle machines (repo-wide search), no P^A/NP^A classes, no BGS statements. The files are *contracts* — "our magnification pipeline must supply bypass witnesses" — inside a P≠NP attempt. (Fortnow's blog, Jun 2026, "Respect the P v NP Problem," calls this project out by name.) Strengthens the Pattern A record.
- **`konard/p-vs-np` (Lean/Rocq/Isabelle/Agda).** Already in FAILURE_AUDIT; confirmed here to stay at catalogue level — `axiom bakerGillSolovay : Prop` (a contentless proposition), `def OracleP (_O : Language) := ClassP` (oracle classes that ignore the oracle), `limitation := True`.
- **Coq neighbors:** `sethirus/The-Thiele-Machine` and `Horsocrates/theory-of-systems-coq` both *mention* the barriers; the latter explicitly states "DESCRIBED, NOT formalized as theorems."

**Why none of these is the infrastructure PleaNP builds:** every one either (a) assumes the barrier as an axiom, (b) defines vacuous or oracle-blind classes, or (c) states an abstract scheme with no machine model. PleaNP's difference is not priority — it's that the oracle-relative classes are *machine-grounded and non-vacuous* (real TM step function, `EvalsToInTime` step counting, 1-step oracle queries), so the barrier statements can eventually be *proved*, not just written down.

### The bounded-arithmetic tradition (the nearest intellectual prior art — must cite)

The barriers *have* been formalized in a formal system — just not a machine-checked proof assistant. **Razborov 1995, *Unprovability of Lower Bounds on Circuit Size in Certain Fragments of Bounded Arithmetic* (Izvestiya RAN 59:1)** derives the natural-proofs barrier as unprovability of circuit lower bounds in weak arithmetic (S¹₂, PV₁). Successors: **Pich 2015** (PCP theorem in PV₁; circuit lower bounds in bounded arithmetic), **Jeřábek** (approximate counting in APC¹), **Oliveira–Müller / Cook–Krajíček** (provability of circuit upper/lower bounds; the KPT theorem). This is paper-rigorous, theory-relative formalization — "which techniques are *feasibly provable*" — and it is the established framework adjacent to PleaNP's barrier map. Two consequences:

1. **Citation duty.** Any write-up of PleaNP's barrier library must cite this tradition as prior art, or a logic reviewer will (correctly) object.
2. **Rung 6 relevance.** Bounded arithmetic is the mature version of "formalize which proof techniques can't work." The specific theories (PV₁ = poly-time reasoning, APC¹ = probabilistic poly-time, the Jerˇábek counting framework) are the *target vocabulary* for what "a lower-bound proof is natural/constructive" should mean formally. Not a substrate to import (it is not machine-checked), but a conceptual reference for the barrier *statements*.

## What was NOT found

- **No machine-checked proof of any of the three barriers** (relativization, natural proofs, algebrization) in Lean, Coq, Isabelle, or any other proof assistant — confirmed across the Lean Zulip archive, a broad literature/repo review (Coq, Isabelle/AFP, Metamath, AI tooling), and the GitHub sweep above. The closer renderings (§"Closer prior art") all stop at axioms, vacuous classes, or abstract schemes — none is a provable statement over real machine-grounded classes.
- **No prior discussion of "complexitylib" by name** in the archive (it's a newer project; the Zulip search did not index a discussion thread for it).
- **No prior discussion of oracle *machines*** (TM + oracle tape + time bound) — only oracle *computability* (unbounded, recursion-theoretic).
- **No importable Lean 4 substrate for one-way functions or pseudorandom function families** — the natural-proofs prerequisites must be stated, not imported (see the crypto-substrate section above).
- **No non-axiom, machine-grounded rendering of a barrier statement** in any proof assistant. (The closest — gobbleyourdong's BGS — is an axiom over vacuous classes.) PleaNP's goal is to be the first *provable* such rendering, but that is an outcome of building the infrastructure correctly, not a claim to stake in advance.

---

## Rung-scope notes — clarifications (no goal or ordering changes)

Per the instruction, conflicts that would materially change a rung's scope are flagged here. The literature review found **no conflict requiring a rung rewrite** — the prior art remains consistent with the existing rung ladder. It did, however, surface four *clarifications* to rung "done" criteria and scope notes that make the rungs more defensible:

1. **Rung 3b (natural proofs) — clarify "done."** The OWF/PRF prerequisite enters as a *hypothesis*, not a constructed object (PleaNP formalizes the conditional `OWF exists ⟹ ...`, not a concrete PRF construction). Update the Rung 3 "done means" line to: *"natural-proofs conditional formalized with OWF as hypothesis, zero `sorry`"* — distinguishing it from needing to *build* a PRF.
2. **Rung 3c (algebrization) — pin the v1 statement.** Formalize the original Aaronson–Wigderson 2009 (multiquadratic) formulation as v1; track the ITCS 2026 multilinear-strengthening as a candidate v2, not part of v1. Prevents formalizing a moving folk theorem.
3. **Rung 7 (open problems below P vs NP) — de-scope Williams √-space.** Williams's *Simulating Time With Square-Root Space* (STOC 2025) is *already* a Lean formalization target by Reitwiessner (Lean Together 2026). Rung 7 should track that effort and pick a *different* open problem to avoid duplication — e.g., Ladner-style structure or derandomization consequences, which the roadmap already lists.
4. **Rung 6 (AI proof-search loop) — reference concrete baselines.** "Done means" should name LeanDojo/ReProver as the premise-selection substrate (or justify divergence) and LeanDojo Benchmark 4's autoformalization metrics as the measured threat model for Gates 3–4, rather than gesturing at generic "AI proof search."

These are clarifications to the rung *spec*, not rewrites of rung *goals or ordering*. The ladder as written in `ROADMAP.md` is sound.
