# alberta-regional-viz

How Edmonton's assessment base and tax levy compare with other Alberta
municipalities. Sibling of [`edmonton-tax-viz`](https://github.com/PeterFriedrich/edmonton-tax-viz)
— separate data, separate outputs, same workflow apparatus (this repo was
instantiated from [`cc-data-project-template`](https://github.com/PeterFriedrich/cc-data-project-template)).

**Status (2026-09-18): scoping.** No pipeline code, no data downloaded. The
two candidate data tracks, what each was verified to support, and the open
decisions are in `docs/SCOPE_candidates.md`; the 2026-07 feasibility spike is
`docs/SPIKE_regional_lens.md`.

## Working on it

```bash
./bootstrap.sh                          # hooks path, venv, guards
.venv/bin/python -m pytest tests/ -q
```

`CLAUDE.md` is the entry point for a Claude Code session; `TODO.md` is the
backlog; `CONTRIBUTING.md` is the spec-before-code pipeline.
