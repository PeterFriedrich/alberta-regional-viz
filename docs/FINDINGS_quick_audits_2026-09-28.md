# Findings — four quick audits, 2026-09-28 (S3)

Candidates #4, #6, #3 and #7 from `docs/AUDIT_LEDGER.md` §"Never audited". I picked them
because each can be run end to end on local data, with no decision needed from Peter.
All of them are correctness audits. Every figure is taken from the processed files as of
`3ab17d6`.

## #4 — External and continuity checks on the parsed values

**Verdict: WARN.** The parser is faithful. The series carries four one-year values that
the publisher printed, and two of them move a core share by 1.9–2.4 pp.

**External check (PASS).** The summary pages that the parser skips are an independent
by-type × by-class tally, so I compared them with the parsed rows:

- The 1999 report, p11 (types × 4 classes): the 32 M&E, NR and linear cells match to the
  dollar. Five residential cells differ by 1–5 dollars, which is the known 1999 subtotal
  rounding (`docs/DATA_ISSUES.md`).
- The 2000 report, p10: every cell and the grand total (212,044,260,337) match exactly.
  Special Areas and Redwood Meadows fall under our "IMPROVEMENT DISTRICTS" `muni_type`,
  and their sum still matches.
- The grand totals on the p12/p11 history tables match the parsed 1998 total exactly and
  the 1999 total to within the same 5 dollars.

A column swap between classes would break the by-class cells, so the 1999 and 2000
reports are clear of that. This check can't see a swap between two municipalities of
the same type. Only these two reports carry a summary page.

**Continuity scan (WARN).** I looked for members whose value in one class jumps more
than 40% away from the midpoint of its neighbours and then returns within 30%. All four
rows are printed in the PDFs as parsed, and each row's total agrees with its own
classes:

| Member / class | Taxation yr (report) | Neighbours → printed | Share effect if replaced by the neighbour midpoint |
|---|---|---|---|
| Airdrie NR | 2016 (2017) | 1,478M / 1,598M → **0** | Calgary `nr` 93.75% → 91.89% (−1.9 pp) |
| Sturgeon County NR | 2000 (2001) | 289M / 287M → **648M** | Edmonton `nr` 73.80% → 76.21% (+2.4 pp) |
| Devon NR (also M&E, linear) | 1998 (1999) | 43M / 39M → **100M** | Edmonton `nr` 75.36% → 75.82% (+0.5 pp) |
| Calgary linear | 2002 (2003) | 1,003M / 1,142M → **1,860M** | Calgary `nr_linear` 92.40% → ~92.1% (−0.3 pp) |

The first two account for most of the sawtooth in the published series: Edmonton `nr`
moves +2.1, −3.7, +3.4 pp over 1999–2001, and Calgary `nr` moves +1.1, −2.7 pp over
2016–2017. Both are larger than the ±1 pp tolerance of the only external anchor (see #3).
Airdrie is a city with about $1.5B of NR, so a printed zero is almost certainly an
omission. Sturgeon and Devon could be genuine one-year rolls, such as an assessment
reversed on appeal. The report can't tell us which, but the Phase 2 FIR data could.

**Method change found incidentally (feeds candidate #2).** The 2000 report's history
table marks the 1997–1999 totals "capped" and 2000 "uncapped", and its preface says
"the 2000 equalized assessment is not capped". The provincial total rises 18.25% in that
year. The 1998 and 1999 prefaces state the base years (1996 and 1997) but don't describe
the cap. The repo says nothing about capping. Taxation years 1997–1998 (reports
1998–1999) may therefore be on a different footing from 1999 onward. If the cap applied
unevenly across municipalities, the shares are affected too.

**Fix:** none in code. Correcting, flagging or interpolating a printed value is Peter's
call, and each option is a different way of handling a number the publisher printed. I
logged the anomalies in `docs/DATA_ISSUES.md`. `TODO.md` gets the treatment decision and
a proposed build-time continuity warning. Adding that warning is a new behaviour, so it
is proposed, not built.

## #6 — Are the known-defect corrections confined to cells that are never output?

**Verdict: PASS, with one guard that had no test (now fixed).**

- `KNOWN_DEFECTS` (13 entries) applies only when `is_sub` is true
  (`src/parse_equalized.py`). Subtotal rows `continue` before `records.append`.
- `KNOWN_TOTAL_DEFECTS` (2 entries) touches only the `grand_total` column of a data row.
  Output writes `classes[:-1]`, so `grand_total` never reaches `equalized_long.csv`
  (checked: no `grand_total` class in the file).
- Keying on (year, column, printed value) is narrow. A correction can only make one
  exact difference reconcile, so it can't hide a different misparse.
- **Gap:** replacing `if fixed is not None and is_sub:` with `if fixed is not None:`
  left all 13 parser tests green, because the existing test never puts the defect value
  on a data row. The new assertion in
  `test_known_defect_is_corrected_only_in_a_subtotal` places it on a data row. It goes
  red under the mutant (`row 'Leduc' classes sum to 22 but its total is 119`) and green
  on the real code.
- 15 entries doesn't argue for a different tool. Each entry is a one-line, exact,
  logged correction, and the 1999 block is one defect repeated six times.

## #3 — How much does `test_reproduces_upe01548` pin?

**Verdict: WARN.** It pins the basis, but not the year convention or a single zeroed
member.

- **Basis: pinned.** The other bases for taxation year 2022 are `nr` 63.29% and `nr_all`
  48.17%, at least 3.7 pp from 60%, while `nr_linear` is 59.57%.
- **Year convention: NOT pinned.** Taxation years 2021 (60.52), 2022 (59.57), 2023 (60.20)
  and 2024 (59.18) all pass 60 ± 1. Tightening the tolerance to ±0.5 pp, the
  integer-rounding bound on "60%", would still pass 2022 and 2023. The convention rests
  on the MA Guide citation in `data/DATA.md` and on no test at all. That's acceptable,
  but the SPEC should not describe this test as protecting it.
- **Missing member:** caught earlier by `BuildError("members not found")`.
- **Member present but zeroed** (the Airdrie case above): zeroing any one of the 6
  smallest Edmonton members (Devon up to Fort Saskatchewan, 2.0% of the region) keeps
  2022 inside the band, at 60.80% at most. Leduc City (61.46%) and larger would fail
  it. The continuity warning proposed in #4 is the guard for this, not the tolerance.
- **The 2010 ≤ 72% assertion is one-sided:** any fall passes. It is consistent with the
  City's 2008 anchor but constrains little.

**Fix:** none to the test. A second external anchor at a different year would pin the
convention. Recorded as a TODO.

## #7 — Is `CLAUDE.md` stale?

**Verdict: FAIL on currency, now fixed.** Every path it names exists. Three statements
were stale or missing:

1. **"No output form is decided yet … write `docs/SPEC_phase1.md` before any pipeline
   code."** This contradicts decision 3 (a static map app), and the SPEC and the pipeline
   both exist. It is replaced with the current state.
2. **`docs/SPEC_phase1.md` wasn't in Key Files**, although it is the doc that governs the
   pipeline. It is added. The `SCOPE_candidates.md` line described open decisions that
   are now locked, and it is reworded.
3. **System `python` is 3.8, so `.venv/bin/python` is required.** This was recorded only
   in handoffs, and it is added.

The Track A rules (St. Albert never committed, EPSG:3400 on ingest) are kept. The
St. Albert rule is a live safety rule while the licence is unanswered, and decision 3's
map app may still need a CRS rule. Trimming them is a scope call for Peter, not a
staleness fix.

## What this run got wrong

- **My first Calgary linear adjustment used the wrong neighbour.** I averaged taxation
  years 2000 and 2001 instead of 2001 and 2003. I caught it before recording and
  corrected the figure to about −0.3 pp. It's the same class as the audit target: a
  check built on the wrong reference still returns a plausible number.
- **I first said "any of the 8 smallest members" could be zeroed inside the band.** I
  had counted the list, not read it: 6 members pass, and the 7th (Leduc City) fails.
  This was corrected in the text above, and the in-session message to Peter was wrong
  too.
- **The continuity scan's thresholds (±40% jump, returning within 30%) are unsized.** I
  chose them without looking at the distribution of year-on-year changes. The scan is
  blind to a step that doesn't revert (for example, a column swap from some year onward),
  to a two-year anomaly, to anomalies under 40%, and to the gap years. "Four anomalies"
  is a floor, not a count.
- **The external check covers 2 of the 26 parsed reports**, at type level only. "The
  parser is faithful" is proved for those two, and elsewhere only in the sense that each
  printed row is reproduced.
