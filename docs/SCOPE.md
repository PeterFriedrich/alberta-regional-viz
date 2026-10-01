# SCOPE — what this project deliberately does not do

The one hand-kept input to the Claude web brief (`scripts/make_brief.py`, setup
in `docs/CLAUDE_WEB.md`). Everything else in the brief is generated from files
the repo already maintains; this is the list an outside reviewer can't derive —
ideas that were considered and turned down, so they stop coming back as
recommendations.

One bullet each: **the thing**, then why not, and a pointer if a decision row
or doc holds the argument. A turned-down idea that has a locked decision needs
no bullet here — the brief already carries `docs/DECISIONS.md`.

## Out of scope

- **Citing the City's published non-residential share figures as the series** (UPE01548's 72% → 60%, CR_3019's 76% → 72%). Neither publishes its method, and the two are different series, not one continued. They serve as a reproduction check only (`test_reproduces_upe01548`); the series is rebuilt from the equalized-assessment reports. `docs/SCOPE_candidates.md` §"Research reply (2026-09-26)".
- **Refactoring `edmonton-tax-viz`'s map app into a shared city-view module** (the 2026-09-26 brief's plan). This repo never restructures its sibling; map code is copied in and left to diverge. `CLAUDE.md` §Project; `docs/SCOPE_candidates.md` §"Research brief (2026-09-26)" item 2.
- **Counting the Police Funding Model as a provincial transfer.** It is a cost billed to municipalities (mostly the ring's rural ones), not money received. `docs/SCOPE_candidates.md` §"Research reply (2026-09-26)", Transfers.
- **Asserting a ring-vs-core political coalition** ("lost tax base + lost votes"). Heard in the 2026-09-26 research brief, never checked: a research topic to investigate later, not a finding. No output claims it; annexation events are factual annotations, and the voting overlay is deferred (decision 11). `docs/SCOPE_candidates.md` §"Research brief (2026-09-26)".
- **Automated watchers: scheduled fetch-and-fingerprint jobs that open issues, a claims register with executable PDF assertions, a data-health page, literature/vendor watchers, and a Playwright smoke test before any web code exists.** These come from the retired claude.ai spec. Inputs are manual and reviewed, and the merge gate is offline (DECISIONS 2026-09-27); `fetch_equalized.py` already keeps a sha256 manifest. Reopen only if Peter asks.
