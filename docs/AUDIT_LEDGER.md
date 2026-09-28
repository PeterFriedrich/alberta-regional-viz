# AUDIT LEDGER — what has been audited, when, and what came back

One row per **executed audit run**. This is the coverage map the audit docs
don't give individually: briefs are reusable *instruments*, findings docs record
*one run's output*, and the `project-audit` skill deliberately picks ONE target
per session — so nothing else says what has and hasn't been looked at. This does.

Rules: add a row when an audit **executes** (not when a brief is written); every
row carries a **pointer to the findings doc**; verdicts are **point-in-time** — a
row says the target was audited *as of that date*, not that it's still clean
after later changes. Not part of any session's mandatory reading — open it to
scope an audit or to check what has already been covered. Audits are framed
top-down, fundamental decisions first.

## Executed audits

| Date | Target / scope | Instrument | Output | Verdict (one line) | Outstanding |
|------|----------------|------------|--------|--------------------|-------------|
| 2026-09-28 | #4 parsed values: external + continuity | 1999 p11 / 2000 p10 by-type tables; spike-and-revert scan of `member_assessment.csv` | `docs/FINDINGS_quick_audits_2026-09-28.md` §#4 | WARN: parser faithful (2 reports tie to the dollar); 4 publisher-printed one-year anomalies, Airdrie NR=0 (2016) −1.9 pp Calgary, Sturgeon NR (2000) −2.4 pp Edmonton; "capped" pre-2000 method change found | Treatment of anomalies (Peter); continuity warning (proposed); capping → #2 |
| 2026-09-28 | #6 known-defect confinement | Code read + mutation of the `is_sub` guard | `docs/FINDINGS_quick_audits_2026-09-28.md` §#6 | PASS; `is_sub` guard was untested (mutant green), test added | — |
| 2026-09-28 | #3 `test_reproduces_upe01548` strength | Alternative bases/years/zeroed members against the ±1 pp band | `docs/FINDINGS_quick_audits_2026-09-28.md` §#3 | WARN: pins basis (≥3.7 pp margin), not year convention (2021–2024 all pass) nor a zeroed small member | Second external anchor at another year |
| 2026-09-28 | #7 `CLAUDE.md` currency | Every claim and path checked against DECISIONS/SPEC/tree | `docs/FINDINGS_quick_audits_2026-09-28.md` §#7 | FAIL → fixed: "no output form decided" contradicted decision 3; SPEC missing from Key Files; `.venv` note added | Trimming Track A rules is Peter's scope call |

## Queued — briefed, not yet run

## Never audited (candidates, roughly ranked)

Listed 2026-09-28, after Phase 1b, ranked top-down: the metric first, then the
data under it, then the project's shape. Each entry is a question, not a finding.

**A. The metric**

1. **Does the headline measure what the argument claims?** The core share of the
   region's NR (fixed 2025 membership) falls 76% → 61%.
   - Question: is that "base moving to the ring", or industrial growth in
     Strathcona and Sturgeon (Industrial Heartland) that was never going to be
     Edmonton's?
   - Evidence: a per-member decomposition of the change, from
     `member_assessment.csv`.
   - Also: Calgary's decline since 2016 is still uninvestigated.
2. **Is the series comparable end to end?** It joins two report layouts, a
   3-year gap and 28 years of equalization practice.
   - Did the method for equalizing linear, M&E or regulated property change
     inside 1997–2025? The NR+linear rise across the gap is explained as a
     composition effect; check that no rule change is also in it.
   - Evidence: the report prefaces (the 1998, 2002 and 2003 intros describe
     the method) and the MA Guide.
   - **Found 2026-09-28:** the 2000 report marks the 1997–1999 totals "capped" and
     2000 "uncapped" (+18.25%). Nothing in the repo covers it; start here.
3. *(Run 2026-09-28, see Executed.)* **How much does `test_reproduces_upe01548` actually pin?**
   - It is the only external anchor, and the City's basis is decoded "by fit",
     not stated.
   - Its tolerance is ±1 pp, against a year-to-year movement of about 1 pp.
     Size the tolerance against that distribution.
   - Can the City's basis be confirmed at the source instead of fitted?

**B. The data under it**

4. *(Run 2026-09-28, see Executed.)* **The 1998–2007 values have only internal checks** (row sums, subtotals,
   alignment). Two external checks are available:
   - The 1999 report's p12 prints Total Equalized for 1990–1999. Compare it
     with the parsed 1998/1999 grand totals.
   - A per-member year-over-year continuity scan (flag any jump over X%) would
     catch a column swap that still sums correctly.
5. **Membership and aliases** (`data/regions.csv`, hand-maintained).
   - Check the 13 EMRB / 8 CMRB lists against a primary source.
   - Decision 8 says dissolved municipalities are merged into their absorber,
     but nothing has checked whether any dissolution into a member happened
     in 1997–2025.
   - Confirm what "City of Calgary (Part II)" (1998) actually is.
6. *(Run 2026-09-28, see Executed.)* **The known-defect tables now hold 15 corrections** (13 subtotal cells in `KNOWN_DEFECTS`, 2 row totals in `KNOWN_TOTAL_DEFECTS`). Each correction is justified by a
   sum. Is "corrected by name" still the right tool at that size, and is every
   correction confined to cells that are never output?

**C. The project's shape**

7. *(Run 2026-09-28, see Executed.)* **`CLAUDE.md` is stale, and it is read every session.**
   - It says "no output form is decided" and "write the spec before any
     pipeline code".
   - It still carries the Track A rules (St. Albert per-parcel, EPSG:3400) and
     points at the spike doc, but decision 1 dropped Track A.
   - Question: what should an always-loaded file hold now that Phase 1 exists?
8. **Should `docs/SCOPE_candidates.md` (281 lines) be split?** It mixes
   dropped-track notes, research distillations and the decision list. The
   decisions are locked and indexed in `DECISIONS.md`. Split it into live
   reference vs history?
9. **The parser's regression guard lives outside the repo.** Phase 1b's
   "2009–2026 byte-identical" check was an ad hoc scratchpad comparison, and
   the PDFs are gitignored, so CI can't parse them.
   - Candidate: commit a per-report fingerprint (row count plus a hash per
     report year) of `equalized_long.csv` and test against it.
10. **Is `parse_equalized.py` still the right shape?**
    - It is 500 lines. `parse_pages` holds two layout families and about ten
        year-specific rules added this session.
    - Question: split layout detection and rules from placement and
      reconciliation, or keep it one flow?
    - Measure it against the next foreseeable change: OCR of the 2008–2010
      reports.
11. **The data contract.**
    - `equalized_long.csv` now has 11 class values across two families, but
      only the spec and code say which is which.
    - Only `core_ring_share.csv` is committed.
    - Question: document the contract in one place (`DATA.md`, or a schema
      test)? `docs/ARCHITECTURE.md`, which is due before Phase 2, may be where.
12. **Is the governance tooling earning its keep here?** The template brought
    guards, hooks, the handoff machinery, `todo_archive` and
    `retrieval_report`. Have any of them fired or caught something in this
    repo, or are some dead weight? Count firings, not lines.
13. **Unsent upstream reports.** Five `DATA_ISSUES.md` rows are NOT SENT or
    WONTFIX, none sent. This is the standing failure mode, and it's not an
    audit so much as a check that the send happened.
