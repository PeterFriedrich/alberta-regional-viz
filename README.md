# cc-data-project-template

A GitHub template for a Python data-analysis project worked on with Claude Code.
It carries the **workflow apparatus** — the parts that stop a session from
losing context, shipping a wrong number silently, or stranding work — and
nothing about any particular dataset.

Extracted from a project where every piece below was earned by a failure it
now prevents. The theme running through all of it: **a working guard on a
channel nobody reads is not a guard.**

## What's in it

| Piece | What it prevents |
|---|---|
| `CLAUDE.md` skeleton | Sessions that start without the rules, or with rules Claude can derive itself |
| `/handoff` skill + `scripts/handoff_gap.py` (SessionStart/End hooks) | Context wiped without a written record — the hook **names the unrecorded commits** and is silent when nothing is owed |
| `.githooks/pre-push` | Pushing to a branch whose PR already merged (work reaches origin, never master) |
| `tests/test_loaded_path.py` | The handoff pile growing into every session's mandatory reading; the archive being deleted instead of appended to |
| `scripts/check_decisions_log.py` | A decision recorded with no test protecting it; a superseded row left looking current |
| `scripts/check_doc_citations.py` | A doc citation that rots in place (line numbers banned; `§N` pointers verified) |
| `tools/todo_archive.py` | Closed work accumulating in the file read first every session |
| `tools/retrieval_report.py` + Read/Grep/Glob hook | Pruning docs on a guess instead of a read log |
| `/project-audit` skill + `docs/AUDIT_LEDGER.md` | Audits that sweep broadly, re-run what was already run, or never record their verdict |
| `docs/DECISIONS.md`, `docs/DATA_ISSUES.md`, `docs/TOKEN_EFFICIENCY.md`, `data/DATA.md` | Format contracts for the ledgers the guards read |
| `.github/workflows/tests.yml` | A merge gate that is offline, secret-free, and therefore never ignored for flaking |

## Use it

```bash
gh repo create <owner>/<new-project> --template <owner>/cc-data-project-template --private --clone
cd <new-project>
./bootstrap.sh            # hooks path, venv, first pytest, memory seed prompt
```

Then, in order:

1. Fill every `<placeholder>` in `CLAUDE.md`, `TODO.md`, `data/DATA.md`.
2. Write `docs/SPEC_phase1.md` before any code (`CONTRIBUTING.md`).
3. Keep `requirements-ci.txt` to what the merge gate needs.
4. Delete this section of the README and describe the project.

## What is deliberately NOT here

- Any dataset, downloader, pipeline stage or rendering code.
- A scheduled data-refresh workflow or a deploy workflow — add them when there
  is data to refresh and a site to deploy, each with its own pytest step.
- A plugin/marketplace packaging of `.claude/`. Extract one the first time a
  workflow fix has to be hand-copied into a second project.
