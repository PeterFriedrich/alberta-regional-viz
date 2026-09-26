# Decisions Index

Append-only. **One ROW per locked decision** — when, what, why (including what
was rejected), and a pointer to where the argument lives in full. When a decision
locks, add a row; when one is superseded, strike it (`~~...~~`) or mark it
`SUPERSEDED <date>` in place and add the successor — don't delete history.

**What a row owes you:**

1. ⚠️ **EVERY ROW CARRIES A POINTER TO A DOC** — not only to code. Code moves;
   the argument has to live somewhere prose can hold it.
   `scripts/check_doc_citations.py` checks that every pointer resolves.
2. **The row is a self-contained summary** and may paraphrase the argument.
3. **The pointer is the authority.** When a row and its target disagree, the
   target wins and the row gets fixed.
4. **A row names the test that protects it**, or carries `[unverifiable]`.
   `scripts/check_decisions_log.py` enforces this on the merge gate (and that a
   superseded row is marked where it stands).

| When | Decision | Full reasoning |
|------|----------|----------------|
| 2026-09-26 | **The core-vs-ring historical timeline is the project's main scope** (decision 6). The annexation history (1979 bid → 1982 → 2019 Leduc → 2025 EMRB dissolution) is the backbone; Tracks A and B provide the data for it rather than competing with it. Rejected: a straight fiscal-comparison table. [unverifiable] — a scope call, not a number. | `docs/SCOPE_candidates.md` §"Research brief (2026-09-26)", §"Decisions that are Peter's" 6 |
| 2026-09-26 | **Calgary is in scope as a same-metric snapshot comparison in split screen** (decision 7). Edmonton's region and Calgary's region are shown side by side at a single point in time. A Calgary timeline may follow but is not committed. [unverifiable] — a scope call. | `docs/SCOPE_candidates.md` §"Decisions that are Peter's" 7 |
| 2026-09-26 | **The voting overlay is deferred, not dropped** (decision 11). A historical map of voting is a candidate later phase; the ecological-inference caveat still applies whenever it is built. [unverifiable] — a scope call. | `docs/SCOPE_candidates.md` §"Decisions that are Peter's" 11 |
