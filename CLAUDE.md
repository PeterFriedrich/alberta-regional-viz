# Claude Instructions

## Project
Alberta regional fiscal lens: how Edmonton's assessment base and tax levy compare
with other Alberta municipalities (capital-region peers first). Sibling of
`edmonton-tax-viz` — a separate repo with its own data and outputs; nothing
here restructures that project. Python-only, no GIS software. Scope is locked
(`docs/DECISIONS.md`): a core-vs-ring timeline of equalized non-residential
assessment, 1997–2025, from Municipal Affairs PDFs, ending in a static map app.
The Phase 1 pipeline (`src/fetch_equalized.py` → `parse_equalized.py` →
`build_share_series.py`) is built. Use `.venv/bin/python` — system `python` is 3.8.

## Key Files
- `TODO.md` — living backlog and **the source of truth for progress**. Read it first to know what to work on; update it in place as items open/close. Session summaries narrate *what happened*; TODO.md owns *what's left*. Never redo a closed item without asking — its `## Done` section lists every closed item in one line each. Conversely, an *open* item can be stale — reproduce the symptom and re-measure the stated cause before acting on it. **When an item closes, move its body to `docs/TODO_archive.md` and leave a `## Done` line** (`python tools/todo_archive.py` does it in bulk) — this file is read every session, so it must hold live work, not history.
- `docs/SPEC_phase1.md` — the pipeline's spec: bases, year semantics (`taxation_year = report_year − 1`), parser approach, Phase 1b. **Read before touching `src/`.**
- `docs/SCOPE_candidates.md` — the two data tracks (Track A per-parcel peers, dropped by decision 1; Track B province-wide aggregates) and the reasoning behind the locked decisions; also distils the 2026-09-26 core-vs-ring timeline brief (Calgary, map app, timeline mode, mandate register). **Read before proposing scope or touching a source.** The research reports themselves live outside the repo in `/home/opc/research/alberta-regional-viz/`.
- `docs/SPIKE_regional_lens.md` — the 2026-07-17 feasibility spike on St. Albert and Strathcona County (copied from the Edmonton repo; facts are as of that date).
- `docs/DECISIONS.md` — append-only index of locked decisions: one row + pointer to the doc holding the full reasoning. **Add a row whenever a decision locks.** Check it before re-opening anything that feels "already settled".
- `docs/TOKEN_EFFICIENCY.md` — context/token hygiene (what NOT to read raw, session-summary archiving). **Read before bulk-reading data or summaries.**
- `docs/DATA_ISSUES.md` — register of defects in data we DON'T control: evidence, what it breaks here, and **whether the publisher has been told**. A finding that never leaves the repo is the standing failure mode; "the artifact exists" is not sent.
- `docs/AUDIT_LEDGER.md` — coverage map of executed audit runs. **Add a row when an audit executes; check it before scoping a new one.**
- `data/DATA.md` — data source details, column names, known quirks. **Read before touching any data files. Update if you discover anything new.**
- `docs/REMOTE_VM.md` — **read FIRST in a Claude Code web/remote VM session**: network-policy constraints, environment setup.
- `session-summary/` — session handoff notes. Read the latest before starting work; older ones live in `session-summary/archive/` (don't bulk-read them).

## Token Efficiency
- **Never `Read` raw data files** (`.geojson`/`.csv`/large `.json`/`.xlsx`) — inspect via a small python summary instead. See `docs/TOKEN_EFFICIENCY.md`.
- Read only the **latest** session summary; keep the 3 most recent at top level, archive older — enforced by `tests/test_loaded_path.py`.

## Session Management
- **At session start, run `gh issue list --state open` — nothing pushes these to a model.** Automated reports file GitHub issues that email Peter and nobody else; a session sees them solely by going to look. ⚠️ **A working guard on a channel nobody reads is the standing failure mode** — treat an unread report as a finding, not as background.
- Always run `/handoff` before `/clear` — never wipe context without a written record in `session-summary/`. **You do not need to be told when one is owed**: the `SessionStart` and `SessionEnd` hooks run `scripts/handoff_gap.py`, which names the commits and uncommitted files that landed after the newest handoff was last committed, and **says nothing when nothing is owed**. Silence there means no code has moved — not that the record is good.
- Commit after each working unit with a descriptive message, rather than batching a session into one commit.
- **Pushing is normal — push proactively after committing, in every environment (including the Oracle box).** Standing authorization; it overrides the harness default of pushing only when asked.
- **Remote/cloud VM sessions: commit + push at every natural checkpoint.** The container is ephemeral; unpushed work is LOST when it is reclaimed. Never hold work waiting for a "push it". Quirks: `docs/REMOTE_VM.md`.
- **⚠️ Peter merges PRs MID-SESSION, often within minutes. Re-check before EVERY push to an existing branch — not once per session.** Commits pushed after the PR merged land on a dead branch: on origin, not on master.
  - Enforced by `.githooks/pre-push`, which blocks a push to a branch whose PR is `MERGED`. **A fresh clone must enable it: `git config core.hooksPath .githooks`.** It fails OPEN (no `gh`, no auth, no network, no PR), so it can never be the reason work goes unsaved. Escape hatch: `git push --no-verify`.
  - After any merge, confirm the work actually landed: `git merge-base --is-ancestor <sha> origin/master`. A merged PR is necessary, not sufficient.

## Code Style
- **A decision that protects a number is a test first, prose second.** Write the guard, then the `DECISIONS.md` row cites its ID; a row with nothing to cite is tagged `[unverifiable]`. `scripts/check_decisions_log.py` gates new rows on the merge path.
- Keep processing steps as separate, independently runnable modules in `src/`
- No silent data drops — flag unmatched or missing records explicitly
- Always set CRS explicitly before any area calculation; canonical CRS is **EPSG:3400** (NAD83 / Alberta 10-TM Forest), the same as the Edmonton repo — peers arrive in other systems (St. Albert 3TM EPSG:3776; Strathcona lat/lon points) and are reprojected on ingest.
- **Never commit St. Albert per-parcel data**, to this or any repo, until the licensing question in `docs/SCOPE_candidates.md` is answered. Citywide aggregates from server-side statistics are the fallback.
- **Every cross-municipality number states its basis**: municipal-only vs total bill; raw FIR vs equalized assessment (raw FIR levels are not comparable across municipalities); lot-acre vs ground-acre. A comparison that leaves one of these unstated is a wrong number that looks right.

## Comments & Scope
- Comments only where the *why* is non-obvious. Don't narrate what the code plainly does.
- Make the **smallest change that satisfies the request**. Don't refactor, rename, or reformat code you weren't asked to touch. No new files unless required.
- No abstractions for a single use case — inline until there are 3+ call sites. (The `src/` module split is a deliberate architecture choice, not an abstraction to collapse.)
- Deleting obsolete code is valid and **preferred** over leaving it behind.
- **Propose the plan first** for: a new module, a change to a data contract or output schema, or anything that changes CI behaviour. Routine edits don't need a proposal.
- These are scope rules, not verification rules. They do **not** relax `no silent data drops`, the guard scripts, or reproducing a bug before fixing it — data projects fail by silent-correctness, and that discipline is why failures get caught.

## Deployment Horizon
- Configurable paths over hardcoded ones
- Structured output over print statements for logging
- Clean module boundaries so rendering can be swapped out later
