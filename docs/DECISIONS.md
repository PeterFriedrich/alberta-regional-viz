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
| 2026-09-26 | **Region = fixed membership for all years** (decision 8): the 13 EMRB members for Edmonton and the 8 CMRB members for Calgary, each as of their 2025 dissolution. Status changes keep a stable ID; dissolved municipalities are merged back into the ones that absorbed them; a StatCan CMA variant is published alongside. Charts must state "2025 board membership applied to all years". Rejected: as-of-year membership, which introduces membership jumps (CRB 25→24→13; CMRB lost Wheatland and Strathmore) unrelated to the argument being tested. [unverifiable] — a definitional choice; the membership lists will get a test once the pipeline exists. | `docs/SCOPE_candidates.md` §"Research reply (2026-09-26)" |
| 2026-09-26 | **Transfers = FIR lines 1912 (provincial operating) and 1922 (provincial capital)** (decision 9), as 5-year rolling averages per capita, with program-break markers at 2014, 2021–23 and 2024. Grantor allocations appear only as a separate "formula intent" panel. Charts state that the charter cities receive no MSI/LGFF operating grants by design. Rejected: splicing MSI and LGFF allocations into a single series. [unverifiable] until the FIR ingest exists. | `docs/SCOPE_candidates.md` §"Research reply (2026-09-26)" |
| 2026-09-26 | **Normalization = equalized non-residential assessment excluding linear and M&E as the headline, with linear and M&E stacked separately** (decision 10). Population = StatCan census counts, interpolated between census years. Rejected: raw FIR levels across municipalities, and an all-non-residential share (Edmonton levies no M&E tax, and linear/M&E move with provincial policy). [unverifiable] until the 2022 UPE01548 reproduction check exists (TODO). | `docs/SCOPE_candidates.md` §"Research reply (2026-09-26)" |
