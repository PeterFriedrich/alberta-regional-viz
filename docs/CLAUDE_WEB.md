# CLAUDE_WEB — giving a Claude web chat the project, and getting rows back

**Read when:** starting a research chat in claude.ai about this project, or
setting up its claude.ai Project.

Claude web sees only what it is given. The brief, `scripts/make_brief.py`, is
built from `CLAUDE.md`, `docs/SCOPE.md`, `docs/DECISIONS.md`, `TODO.md`,
`docs/DATA_ISSUES.md` and the requirements files, so the "my situation" block
is never re-typed by hand and cannot silently go stale. It ends with a required
reply format whose tables map onto `TODO.md` / `DECISIONS.md` rows.

## Public repo: sync the brief into a claude.ai Project

1. Commit the brief once: `python scripts/make_brief.py --write`.
   From then on `tests/test_brief.py` fails the merge gate whenever
   `docs/BRIEF.md` no longer matches its sources; the fix is to re-run
   `--write` in the same PR.
2. In claude.ai, create a **private** Project (the GitHub integration is not
   offered on a shared one) and add the repo from GitHub. Select
   `docs/BRIEF.md`. Add `CLAUDE.md` or `TODO.md` in full only if the project's
   capacity allows — the brief already summarises both.
3. ⚠️ **The sync is manual.** claude.ai fetches the files when you press
   **Sync now**, not on push. A green merge gate means the *repo's* brief is
   current, not the Project's copy. Press Sync before each research chat.

The integration reads file contents only — no history, PRs or issues. A
research chat that needs one of those gets it pasted.

## Private repo: paste it

The GitHub integration has been reported to authenticate and then 404 on
private repos (anthropics/claude-code #98050, open as of 2026-09-29). Don't
commit `docs/BRIEF.md`; instead run

```bash
python scripts/make_brief.py | xclip -selection clipboard   # or: > /tmp/brief.md
```

and paste it at the top of the chat. With no committed file, the staleness
test skips itself.

## Before each research round

- Update `docs/SCOPE.md` if an idea was turned down since the last round.
- Keep the brief's reply-format section in the prompt (it is in the brief;
  if the prompt is written separately, say "end with the brief's reply format").
- File the reply outside the repo first (on the owner's server,
  `/home/opc/research/<repo>/`), then triage its
  tables into `TODO.md` / `docs/DECISIONS.md` by hand. A parser for them
  (`ingest_reply.py`) is deferred until three rounds have used the format —
  `docs/FINDINGS_harvest.md` §"D (spec sheet): recommendation".
