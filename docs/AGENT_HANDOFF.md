# Agent handoff — START HERE for a new agent context

**Purpose:** this is the single pointer a fresh agent (or a new session) should
read first. It tells you how to pick up work, what the current state is, and
what the highest-value next moves are. Read `AGENTS.md` for the full repo
conventions; this doc is the "what do I do on day one" summary.

---

## How to pick up work (the protocol in one paragraph)

1. **Read this file + `docs/MULTI_AGENT_WORKFLOW.md` + the repo-root `AGENTS.md`.**
2. **List the open issues** (GitHub API or `gh issue list`). Tasks labeled
   `status:available` are claimable. **One claim per agent at a time.**
3. **Sweep first** (per the protocol): check `status:claimed` issues older
   than 1h with no activity → reclaim; check for protocol violations (two
   status labels); check docs coherence.
4. **Pick work:** lowest issue number first; `priority:high` jumps the queue.
5. **Claim:** swap the label `status:available` → `status:claimed` in one
   atomic API call, self-assign, comment `claimed by <name> run=<run-id> at
   <utc>`. **Generate a run-id** `<YYYYMMDD-HHMM>-<4 chars>` and use it in
   every claim/done/blocker comment.
6. **Do the work; prove the done:** commit to `dev` (never force-push)
   and **push to `dev` immediately after the commit** — `git push origin dev`
   — before closing the issue or citing it in the done comment. A commit
   that exists only locally is invisible to siblings (the system of record is
   `git log origin/dev`) and counts as undone until pushed. Then include gate
   evidence in the done comment (gate commands + output); swap
   `status:claimed` → `status:done` and close with the commit link.
7. **No task available?** Fall through: `Tests:` issues → PR review comments →
   blockers. Only when all are exhausted is the queue empty.
8. **Before pushing, run the local CI-equivalents.** The Tier-1 scanners and
   `pytest` do not cover every CI step. In particular the **Galaxy regen
   smoke** (the committed `tooling/galaxy/galaxy.html` must match a fresh
   regeneration) has bitten two sessions (#112, #118) because
   `docs/SORRY_TRACKER.md`, `docs/ROADMAP.md`, `formalization.yaml` and the
   review points are all embedded in that page. The **Review-inbox index
   smoke** (`reviews/INBOX.md` must match `review_inbox.py index`) is the same
   failure class (#119). Run:
   ```bash
   python3 tooling/pre_push_check.py         # exit 1 if a tracked artifact is stale
   python3 tooling/pre_push_check.py --fix   # regenerate in place, then git add it
   ```
   The check covers every listed artifact; a new CI-only staleness step should
   extend the `CHECKS` list in `tooling/pre_push_check.py` rather than add a
   one-off script.

## Current state (2026-09-16, run=20260916-1622-p8k2)

- **Working tree:** `dev` — sweep + `#80` Pass 2 landed (see below).
- **Lean builds:** clean modules green (BarrierCalculus, Oracle substrate,
  Williams chain, Circuit substrate, **LowerBoundCompiler**);
  `lean/PleaNP/Barriers/Relativization.lean`,
  `lean/PleaNP/Barriers/DiagonalAssembly.lean` + `lean/PleaNP/Computability/OracleUpstreamP.lean`
  fail ONLY on their tracked sorries (expected; see SORRY_TRACKER).
- **Queue sweep (2026-09-16):** five stale `status:claimed` claims reclaimed to
  `status:available` (#37/#72/#74/#90/#91 — heartbeats 2 days old, commits
  verified landed); the completed Williams-transfer passes closed
  (#88/#89/#90/#91 `status:done`, umbrella #76 closed; residual proof = #98);
  #22 closed as superseded by the #37 chain; #23 unblocked to `available`.
  **Label drift is real — re-sweep before claiming.**
- **Tools (all tested; `pytest tooling/` — 176 passing):** hygiene/vacuity/model/
  binder/unicode/pass scans, `axiom_check.py` (no sorryAx), `lean_readback.py`,
  `readback.py`, `dual_render.py`, `statement_lint.py`, `multi_render.py`,
  `review_inbox.py`, `lakefile_sync_check.py`, `docs_links_scan.py`
  (**pre-existing 43 broken refs — not CI-wired**).
- **Repo hydrology:** `docs/REVIEW_INBOX.md` (human review surface),
  `docs/GRANT_READINESS.md` (funding gap analysis),
  `docs/STATEMENTS/SEMANTIC_APPROVAL.md` + `HUMAN_REVIEW_LAYERS.md`.

## Highest-value open issues (agent-pickup, in priority order)

1. **#17 — Multi-agent rendering-campaign protocol** (high): true N-parallel
   agent renderings + merge step; fixes the `sync-pending` idempotency bug.
   *Unlocks #19.*
2. **#18 — BGS separating-oracle proof path** (high): the first zero-sorry
   barrier theorem — the funding-relevant move. Soft-blocked by #4.
3. **#20 — Sweep duplicate review issues #7–#16** (high): 10 dupes of 5
   disagreements; close per protocol + fix root cause.
4. **#19 — Measured multi-rendering corpus experiment**: the Tier-1 #3
   quantitative table. Blocked by #17.
5. **#1–#5**: existing queue (Rung-5 extension #1, P/NP grounding #4,
   gate/tests #2/#3, LLM-in-CI decision #5).

## The human's part (don't block on it, but surface it)

- **Review-pending issues #7–#16** are for the human to mine (comment
  `confirm` / `flag <reason>`). Agents file these; the human answers in batch.
- **#18** (BGS proof): when it lands, the human must approve the semantic
  claim via the probe/review tooling (that's the irreducible human step).
- **Human-side grant items** (paper skeleton, named lead, co-PI) are NOT
  agent-tasks — flag them in session reports, don't do them for the human.

## Honest constraints (from the failure audit — do not violate)

- **Never claim `Complexity.*` namespace** (DEC-002); import P/NP from
  upstream when it lands (DEC-003), don't define locally.
- **Never run proof search against a non-frozen statement** (Gates 1–6 first).
- **A `sorry` needs a tracker row** in `docs/SORRY_TRACKER.md` (same commit).
- **No force-push to `dev`** — it can destroy a sibling agent's work.
- **The human never arbitrates** a two-translation disagreement; resolve it in
  the machinery.