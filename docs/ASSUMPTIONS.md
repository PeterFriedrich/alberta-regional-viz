# Assumptions log

Every premise a published number rests on that is **not** proven by a guard,
with its status and how to test it. Use it to come back to an assumption, and
check it before scoping an audit.

How this differs from the other docs:
- `DECISIONS.md` records the *choices*.
- `DATA_ISSUES.md` records *defects* in other people's data.
- `AUDIT_LEDGER.md` records *what has been checked*.

This log records *what we take as true without having proven it*.

Rules:
- **Add an entry when a number starts depending on something unproven.** That
  includes an inference written as "looks like" or "probably" in `data/DATA.md`.
- **Keep an entry when its status changes.** Update its status and evidence and
  keep the history, as `DECISIONS.md` does. An entry a test now proves becomes
  `VERIFIED`, with the test ID.
- **Size it.** "What breaks if wrong" says which outputs move and by roughly how
  much, so an audit can rank the entries.

Status values:
- `VERIFIED`: a guard or primary source proves it; the test ID is named.
- `SUPPORTED`: evidence agrees, but it doesn't cover every year or member it is
  applied to.
- `UNVERIFIED`: taken on trust.
- `ACCEPTED`: known to be wrong by a measured amount, and used anyway by decision.

---

### A1. `taxation_year = report_year − 1`
- **Used by:** every output's `taxation_year` column; the timeline's x-axis.
- **Status:** SUPPORTED.
  - The publisher's wording agrees: the "Updated 2024 Equalized Assessment"
    reflects "assessment changes for the 2022 assessment year". Alberta taxes
    the 2022 assessment year in 2023, so report 2024 = taxation 2023
    (`/home/opc/research/alberta-regional-viz/fir_pdf_gap_2026-10-17/u2024.xlsx`, row 3).
  - `test_reproduces_upe01548` passes for any of taxation years 2021–2024, so it
    doesn't pin the year (`docs/FINDINGS_quick_audits_2026-09-28.md` §#3).
- **If wrong:** every point shifts one year, and annexation markers sit a year
  off the steps they explain.
- **Test:** a second external anchor at another year (TODO).

### A2. Equalized assessment is on one basis across 1998–2026
- **Used by:** the core-vs-ring share timeline.
- **Status:** UNVERIFIED before 2000. The 1997–1999 totals are printed "capped"
  and 2000 "uncapped", and the provincial total rises 18.25% that year
  (`docs/FINDINGS_quick_audits_2026-09-28.md` §#4).
- **If wrong:** the share moves only if capping affected core and ring
  unevenly. That is not measured.
- **Test:** audit candidate #2 in `docs/AUDIT_LEDGER.md`.

### A3. The PDFs are the original equalized assessment; FIR's `EA` is a later, revised extract
- **Used by:** the choice of the PDFs as the series source; the 2008–2010 fill (A4).
- **Status:** SUPPORTED.
  - For report year 2025, the province's updated report equals FIR on 101 of
    104 member-class values, and the PDF on 81.
  - FIR 2024 matches neither report exactly.
  - Measured 2026-10-17 (`data/DATA.md` §"Parsed (2026-10-02)").
  - Earlier years are inferred from the pattern: market classes, mostly
    reductions, cores never exact.
- **If wrong:** the explanation of the gap fails, and A4's size estimate with it.
- **Test:** re-run the three-way join when the province publishes another
  updated year (research folder `fir_pdf_gap_2026-10-17/join.py`).

### A4. FIR is close enough to fill report years 2008–2010
- **Used by:** the core share for taxation years 2007–2009, which includes
  Edmonton's 72% anchor year. Option (a), Peter, 2026-10-17; not built yet.
- **Status:** ACCEPTED.
  - Where both sources exist, FIR's core share is within 0.27 pp of the PDF on
    `nr` across 2005–2012 (Edmonton −0.21 in 2006, −0.16 in 2011).
  - The gap can't be measured in the filled years themselves, because there is
    no PDF value there.
  - The worst observed year is Edmonton 2016: −0.84 pp `nr`, in a downturn
    with heavy appeals. 2008–2009 was also a downturn.
- **If wrong:** Edmonton's share in those years is off by up to about 1 pp,
  probably low (FIR is mostly reduced).
- **Test:** text-layer versions of the 2008–2010 reports (the `DATA_ISSUES.md`
  ask to Municipal Affairs) would replace the fill outright.

### A5. Railway inside NR in 1998–2004 moves the share by about 0.1 pp at most
- **Used by:** `nr` basis 1998–2004 (DECISIONS 2026-09-28).
- **Status:** UNVERIFIED for those years. Railway was 0.03–0.6% of NR in
  2007–2019, and that share is assumed to hold earlier.
- **If wrong:** the `nr` headline steps at 2005.
- **Test:** FIR's railway column 08290 for 1998–2004, where it exists; 2001
  has none.

### A6. FIR 2001's NR column includes railway
- **Used by:** any FIR-vs-PDF comparison for 2001.
- **Status:** SUPPORTED. It matches the PDF's NR-including-railway exactly for
  14 of 21 members (`data/DATA.md` §"Parsed (2026-10-02)").
- **If wrong:** 2001 comparisons are off by the railway amount.

### A7. Spruce Grove's −$1.76M conditional transfers in 2015 are a reversal
- **Used by:** `transfers_per_capita.csv`, kept as printed and named in `basis_note`.
- **Status:** UNVERIFIED. The amount follows $20.1M in 2014 (`data/DATA.md`
  §"Transfers per capita").
- **If wrong:** nothing numeric changes, but the explanation in the note does.
- **Test:** Spruce Grove's 2015 audited statements.

### A8. Edmonton FCSS before 2007 is on a different basis
- **Used by:** the exclusion of Edmonton FCSS rows before 2007 (`NOT_COMPARABLE`).
- **Status:** SUPPORTED, "probably" in `docs/FINDINGS_spending_jumps_2026-10-10.md`.
- **If wrong:** six years of a real series are dropped.
- **Test:** the City's 2005–2007 annual reports, line by line.

### A9. Calgary's 2025 FCSS/housing movement is another reclassification
- **Used by:** not building Calgary FCSS and housing (DECISIONS 2026-10-10).
- **Status:** UNVERIFIED for 2025, while 2016, 2020 and 2022 are shown
  (`docs/FINDINGS_spending_jumps_2026-10-10.md`).
- **If wrong:** none today, because the series is not built.

### A10. Nominal dollars are acceptable for core-vs-ring comparisons within a year
- **Used by:** `transfers_per_capita.csv`, `spending_per_capita.csv`.
- **Status:** ACCEPTED (Peter, 2026-10-02). The ratio within a year is unaffected.
  A 25-year line overstates growth.
- **If wrong:** growth claims across years. The deflator is still open in TODO.

### A11. The brief's history and fiscal figures
- **Used by:** nothing yet. This is a gate on Phase 3 captions.
- **Status:** UNVERIFIED except the items ticked in `TODO.md` ("Phase 3 gate").
  One was already found wrong: the Leduc annexation is 2019 / 8,260 ha.
- **Test:** primary documents, as listed in that TODO item.
