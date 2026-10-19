# Persistent & cloud toolchain options for Lean 4 + Mathlib

**Status:** 2026-09-13 — Plans A (devcontainer) and B (CI oracle) implemented; Plan E (warm ghcr image + leancheck/elantool tooling) also implemented and VERIFIED live (see §Plan E). The earlier GitHub `ACTIVATION_CHECKLIST.md` billing-lock note is superseded: Actions runs are executing normally (warm-toolchain + review-issue + CI workflows all run on pushes). Plans C and D remain reference options.
**Audience:** anyone who needs a Lean 4 + Mathlib environment for PleaNP without re-provisioning a toolchain from scratch each session (the pain this solves: `elan install` + Mathlib cache download + full build every new workspace).

The problem statement: *"What could be a free and more persistent way to have access to the Lean toolchain and mathlib corpus without having to connect to the local M4 system or build in the temporary sandbox from scratch every time work is done on the repo?"*

Verified facts that shape every option below (all confirmed working from this repo's own sandbox on 2026-09-06):

- The Lean toolchain ships as a self-contained binary bundle via **elan** (`~/.elan/toolchains/leanprover--lean4---v4.31.0/`).
- Mathlib serves **precompiled `.olean` caches** via `lake exe cache get` (Azure-backed, hosted by `leanprover-community/mathlib4`; ~8542 files, a few minutes at ~200KB/s, decompressed in place). Cache variants exist per toolchain and per branch/tag.
- `lean-toolchain` pins the toolchain; `lean/lakefile.lean` pins mathlib `@ "v4.31.0"`.
- Mathlib's own CI (GitHub Actions + Bors) uploads `.olean` caches so **PR branches get cache hits**.
- The "globally shared mathlib installation" pattern exists and is documented by the community (multi-project cache sharing).

---

## TL;DR — recommended strategy (for PleaNP)

**Primary (zero-cost, public, persistent): GitHub Codespaces (or Gitpod) with a checked-in `.devcontainer` that runs `lake exe cache get` once.** The container image is pre-built with elan + the pinned toolchain + Mathlib cache baked in (or pulled in <5 min on first use), and *persistence comes from the container image + Mathlib's Azure cache*, not from a living VM. Every new session starts from the same warm image → no from-scratch toolchain or build.

- **Plan A — warm devcontainer (recommended).** Commit a `.devcontainer/Dockerfile` (from `alan-turing-institute/lean-devcontainer` or mathlib's Codespace setup) that installs elan, sets `lean-toolchain`, then runs `lake exe cache get` and prebuilds `Mathlib` + `PleaNP` (optionally only `PleaNP`'s dependency closure). Codespaces: 60 h/month free (personal), Gitpod: 50 h/month free; both *public* options; the workspace dies but the **image + cache do not**.
- **Plan B — dedicated free cloud runner.** Self-host the repo's existing CI workflow (`.github/workflows/ci.yml`) on GitHub Actions free minutes (2000 min/month private / unlimited public). CI re-pulls Mathlib cache each run (fast) — a persistent *build oracle* for the repo even with zero local toolchain.
- **Plan C — live web playground** (`live.lean-lang.org`, `lean.math.hhu.de` — the `lean4web` app): zero-setup for single-file experiments/snippets against latest Mathlib. Not for multi-file repos.
- **Plan D — local M4 (least preferred for persistence):** as now — install elan once per machine and rely on `lake exe cache get`; fine for a long-lived workstation, irrelevant for throwaway sandboxes.

For an AI agent that works *inside* PleaNP's repo, **the practical answer is Plan A/B combined:** the repo becomes self-provisioning (devcontainer + CI both run `lake exe cache get`), so *any* execution environment (local laptop, sandbox, cloud runner, Codespace) converges to the same warm state in minutes using the community's public cache — nothing about the M4 box or a bespoke build is required.

---

## Option table

| Option | Cost | Persistence | Pain to set up | Good for | Notes / URLs |
|---|---|---|---|---|
| **A. Codespaces / Gitpod devcontainer** | Free quotas (Codespaces 60 h/mo personal; Gitpod 50 h/mo) | Warm image + Mathlib cache = minutes to warm | Low (check-in `.devcontainer`; mathlib provides one) | Day-to-day editing/building in the browser | GitHub "Open in Codespaces" buttons on every mathlib repo; `leanprover-community/lean4web` for the playground; HHU instance `lean.math.hhu.de` |
| **B. GitHub Actions CI as the build oracle** | Free (unlimited for public repos) | Cache is per-run but ~minutes | Low (CI already exists in-repo) | Headless builds, PR checks, benchmark harnesses | Repo's own `.github/workflows/ci.yml`; mathlib olean cache now works from forks |
| **C. lean4web playgrounds** | Free | Session-scoped | None | Single-file experiments vs. latest Mathlib | `live.lean-lang.org`, `lean.math.hhu.de` |
| **D. Local M4 / long-lived workstation** | Free | Need elan+cache once; then persistent | Medium | Big lemma development | `lake exe cache get` wiki (mathlib4 "Using mathlib4 as a dependency", "globally shared mathlib installation") |

**Not recommended for PleaNP:** self-hosting the package (a `lake`-servable mirror) or vendoring Mathlib sources into the repo — both add maintenance and disagree with DEC-003 (import upstream). The community cache *is* the decentralization already in place.

---

## Compartmentalizing / decentralizing the dependency (the "little pieces" question)

Per-session from-scratch provisioning is expensive mostly because Mathlib is monolithic (~5k+ source modules / 8.5k cached oleans). Options to pull *only what we need*:

1. **Dependency-closure builds (cheap now).** `lake build PleaNP.Import.Path` builds only PleaNP's import closure, not all of Mathlib — the cache still supplies the prebuilt Mathlib oleans, so only `PleaNP.*` gets rebuilt from source. This is already how we iterate (the `#barrier_check` module builds in ~4 s with the cache warm). **For even smaller slices:** keep `lean/PleaNP/Calculus/BarrierCalculus.lean` import-light (it only needs core `Mathlib`, not the whole `import Mathlib` — worth a follow-up to trim the import) so a fresh checkout can build JUST that module against the cache.
2. **Standalone sub-project for the calculus layer.** The `lean/PleaNP/Calculus/` module has zero dependency on the unvalidated `Oracles` substrate; it could be split into its own tiny lake project with its own `lakefile` (still requiring mathlib from cache). This makes the Rung-5 prototype independently extractable and CI-able in isolation (matches DEC-001's "extractable lean/ tree" spirit, one level deeper).
3. **Fine-grained olean cache sharing.** Mathlib's `lake exe cache` and the "globally shared mathlib installation" wiki pattern let multiple projects share one installed Mathlib. For a small project like PleaNP this mostly matters where many projects share a single runner (e.g. a shared devcontainer for several repos).
4. **Offline/local mirrors of the cache** (e.g. a repo-scoped self-hosted Actions runner with a warm `~/.elan` + `.lake`): persistent but even-more-infra; only worth it if the free quotas become binding.
5. **Downstream split (long term).** When `PleaNP/Calculus` stabilizes, consider proposing the `Relativizing` typeclass + `#barrier_check` pattern as a standalone published lake package (folder or git dependency) so other projects depend on the calculus, not the whole repo. This is *decentralization of our own layer*, not of Mathlib.

**Bottom line:** the cheapest "compartmentalization" is (1) + (2): keep new modules import-light, build per-module against the public cache, and keep the calculus layer physically separable. The parts we tend to re-provision are the *toolchain + cache*, which are exactly the parts the community already serves publicly and persistently.

---

## Concrete recommendation to implement now (files to add)

1. `.devcontainer/devcontainer.json` + `Dockerfile` (elan + mathlib cache get + prebuild `PleaNP.Calculus.BarrierCalculus`) — gives browser-based persistent editing for humans, and a canonical warm image the repo always refers to.
2. Extend `.github/workflows/ci.yml` to *also* run `lake build PleaNP.Calculus.BarrierCalculus` (or the full tree) with mathlib cache restored — already partly there; ensure a `cache` step for the Mathlib oleans so PRs don't re-download 8.5k files.
3. Document in `AGENTS.md` the one-line bootstraps: `elan install` → `lake exe cache get` → `lake build <module>` (this is the entire "persistence" story: the cache is the persistence layer; nothing else needs to be stored).
4. (Follow-up) trim `import Mathlib` in `lean/PleaNP/Calculus/BarrierCalculus.lean` to the minimal core imports, and note it in the module header — makes single-module fresh builds even faster.

None of this requires the M4 machine; any free public runner + the community cache reproduces the environment.

---

## References

- Mathlib's "Using mathlib4 as a dependency" wiki (cache get, toolchain pinning) — github.com/leanprover-community/mathlib4/wiki
- "Globally shared mathlib installation" wiki page (multi-project cache sharing) — same wiki
- lean4web (playground app; `live.lean-lang.org`, HHU `lean.math.hhu.de`) — github.com/leanprover-community/lean4web
- Mathlib repo README (Codespaces/Gitpod buttons; "Gitpod Ready-to-Code"; PR olean cache now works from forks) — github.com/leanprover-community/mathlib4
- Lake docs on `cache` and `post_update` hooks (pinning toolchain + cache-get after `lake update`) — lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake

**Status for the decision log:** this is a *recommendation*, recorded here for a future DEC once the `.devcontainer` + CI-cache landing is scheduled. Not yet a decision — the repo continues to build via the community cache from any environment.


---

## Plan E (implemented 2026-09-13) — warm ghcr image + leancheck iteration tool

The two follow-ups from "what to implement" are now in the repo:

### E1. Warm toolchain image (the 'toolchain that persists' for agents, free)

- **.github/workflows/warm-toolchain.yml** — on every push to main,
  builds the multi-stage warm image and pushes two tags to ghcr.io:
  ghcr.io/philipdallen/pleanp:main and :lean-<sha>. The image bakes
  in elan + the pinned Lean toolchain and a warm lean/.lake (Mathlib
  oleans fetched once at image build). Also adds an actions/cache step for
  ~/.elan so CI runners restore the toolchain in seconds.
- **.devcontainer/Dockerfile.warm** — the multi-stage build (builder
  installs elan + Lean + lake exe cache get; runtime stage copies the warm
  ~/.elan and lean/.lake).
- **For agents:** docker pull ghcr.io/philipdallen/pleanp:main then
  mount the repo — no elan install, no toolchain download, no olean fetch.
- **Cost:** free for public repos (GHCR + Actions public minutes).
- **Practical how-to:** docs/TOOLCHAIN_AGENTS.md sec 1.

### E2. Lean iteration tool (leancheck), to speed proof authoring

The edit→typecheck loop was the practical gating cost during the U_B
machine work. Two stdlib-only tools now compress it:

- **tooling/leancheck.py** — runs lake env lean <file> and prints only
  the FIRST error (file:line:col + message + compact goal context + a fix
  hint). --all / --no-context / --json flags; exits 0/1/2.
- **tooling/watch_leancheck.py** — polls a file until clean, then stops
  (prints iterations + elapsed); Ctrl-C re-checks for a final picture.
- Tests: tooling/gates/tests/test_leancheck.py (7 tests, stdlib-only).
- Practical how-to: docs/TOOLCHAIN_AGENTS.md sec 2.

**Status (2026-09-13, confirmed live):** Plan E implemented and VERIFIED.
The warm-toolchain workflow runs on [main, dev] pushes — consecutive runs
completed `success` (26500ba/329cad7/c3916e5/116aaa6) — and
`ghcr.io/philipdallen/pleanp:dev` + `:main` are both pullable (docker
manifest inspect returns the OCI index). The `ci-toolchain-cache` job
caches `~/.elan` for CI runners. `tooling/elantool.sh` is live-verified
(working-docker-daemon detection + AGENTS.md bootstrap fallback);
`tooling/leancheck.py`/`watch_leancheck.py` are live-validated against
Lean v4.31.0 and adopted on real proof work (#37 Pass 1).
