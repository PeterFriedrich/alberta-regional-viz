# Findings: is equalized assessment on one basis across 1997–2025? (audit #2, A2)

Run 2026-11-20 (S17) from `docs/AUDIT_equalization_basis.md`. Scripts, their
output and the two Municipal Affairs bulletins are in
`/home/opc/research/alberta-regional-viz/equalization_basis_2026-11-20/`
(`measure.py`, `fir_vs_pdf.py`, `steps.py`, `headline.py`, `*_out.txt`, `src/`).
All figures are equalized assessment, 2025 board membership, from
`data/processed/` as committed at `0fda1c4`.

## Verdict: FAIL for the 1998–1999 reports (taxation 1997–1998); SUPPORTED from the 2000 report on

The capped reports are not on the later basis, and the change at the boundary
was not uniform: it raised both cores well above their rings. The two capped
points sit low for the core, so they **understate** the 28-year fall in the
core's share rather than create it. The effect is small on the headline `nr`
basis and large on `nr_linear` and `nr_all`.

## 1. What was the cap? (partly answered)

- **The reports:** the 2000 report's history table (p11) marks the 1997–1999
  totals `* capped` and prints no flag for 2000 (`** uncapped`). Its preface
  (p2, dated 1999-10-26) says "It is important to note that the 2000 equalized
  assessment is not capped." The 1998 and 1999 prefaces describe equalizing to
  a base year (1996 and 1997) under AR 366/94, and say nothing of a cap.
- **The 2000 measures are a different instrument:** *Advisory Aspects* No. 6
  (Municipal Affairs, 1999-12-22, p4, `src/ma_advisory_aspects_issue6_1999-12-22.pdf`,
  retrieved 2026-11-20 from `municipalaffairs.gov.ab.ca/documents/as/issue6.pdf`)
  says Cabinet approved for the 2000 tax year "Average growth in equalized
  assessment over a period of two years, combined with a 5% cap on growth on
  residential equalized assessment, and 10% on growth of non-residential
  equalized assessment", under a new "Equalized Assessment Variance Regulation"
  for school requisitions. So from 2000 the report prints the uncapped figure,
  and the requisition adjustment sits outside it.
- **The pre-2000 rule itself is not found.** *Advisory Aspects* No. 2
  (1998-12-21, `src/ma_advisory_aspects_issue2_1998.pdf`, retrieved 2026-11-20
  from open.alberta.ca) mentions only an "Assessment Equalization Amendment
  Regulation" that "will clarify the process", without terms. It also lists
  Municipal Government Board appeals of the 1997 and 1998 equalized
  assessments by Calgary (MGB 218-98), Airdrie (MGB 221-98) and five other
  municipalities, all arguing that equalization was not fair and equitable.
  *Advisory Aspects* No. 6 lists the City of Edmonton's appeal of its 1999
  equalized assessment (MGB 136/99, 138/99). The basis of those years was
  contested at the time.
- **Not reached:** the Guide to Equalized Assessment and the Nov 1996 Education
  Property Tax Bulletin (both `municipalaffairs` URLs reset the connection), and
  the Alberta Gazette text of the AR 366/94 amendments.

## 2. Did it hit core and ring unevenly? Yes

Growth from the 1999 to the 2000 report:

| | Province | Edmonton core | Edmonton ring | Calgary core | Calgary ring |
|---|---|---|---|---|---|
| NR (incl. railway) | +23.0% | +19.7% | +9.0% | +44.0% | +15.9% |
| Residential (incl. farmland) | +21.8% | +15.8% | +11.9% | +32.9% | +38.9% |

In the neighbouring years province-wide NR grew 4.4% (1999) and 3.3% (2001), and the
1990–1999 totals grew 3–8% a year. The regulated classes, which are not
equalized by ratio, did not jump (linear +2.7%, M&E +8.5%). A one-year jump in
the market-value classes only is what releasing a cap on equalization looks
like, not a market move.

Core-share step at the boundary (taxation 1998 → 1999), against the series'
other 27 year-to-year steps:

| Region | Basis | Step | Median \|other step\| | Rank of \|step\| |
|---|---|---|---|---|
| Edmonton | `nr` | +1.68 pp | 1.14 | 4 / 28 |
| Edmonton | `nr_linear` | +2.67 pp | 0.94 | 2 / 28 |
| Edmonton | `nr_all` | +1.95 pp | 0.79 | 6 / 28 |
| Calgary | `nr` | +0.96 pp | 0.48 | 5 / 28 |
| Calgary | `nr_linear` | +2.01 pp | 0.62 | **1 / 28** |
| Calgary | `nr_all` | +2.34 pp | 0.67 | **1 / 28** |

None of the known anomalies sits on this boundary: Devon (1999 report) and
Sturgeon (2001 report) are already corrected from FIR (`data/corrections.csv`).

**FIR has no uncapped figure.** FIR EA for report years 1998–1999 equals the
PDFs (core and ring within 1.1%), so it is capped too. FIR 2000 is 4–6% *below*
the PDF for both cores and within 1% for the rings. That is unexplained, and the
series doesn't use FIR for 2000. It could be a revision (Edmonton's 1999 appeal)
or the variance-regulation figure; it is noted, not chased.

## 3. Any other method change inside 1997–2025?

- **Province-wide steps:** only two of the 25 year-on-year steps fall outside
  median ± 3 MAD (6.95% ± 9.2): 2000 (+18.25%, the cap) and 2011 (+77%). The
  2011 step spans the four-year 2008–2010 gap in the PDF series. FIR fills it
  with 2008–2010 growth of 21–42% a year, the 2007–09 boom, so it is not a rule
  change in the parsed data.
- **Prefaces:** 2002 and 2003 state the standard ("100% of market value";
  regulated property not adjusted) and AR 289/99 replacing AR 366/94. That
  restates practice; no step sits there (+7.3%, +8.3%). The 2005–2026 reports
  carry no method text in their first four pages.
- **Railway, 2020:** the railway column ends with the 2019 report, and
  railway-heavy members' linear rises by about that amount (Banff 16.9M →
  36.9M, Lacombe County 816M → 886M). It moved into linear, so `nr` is
  unaffected and `nr_linear` / `nr_all` already carry both (matches the
  `build_share_series.py` comment).
- **The class-set switch after the 2004 report:** no step at 2005 beyond
  railway, which A5 already covers.

## 4. Remedy, sized (Peter decides)

The fall in the core share, measured from taxation 1997 and from 1999, to 2025:

| Region | Basis | From 1997 | From 1999 | Difference |
|---|---|---|---|---|
| Edmonton | `nr` | 16.12 pp | 16.38 pp | +0.26 |
| Edmonton | `nr_linear` | 8.34 pp | 10.20 pp | +1.86 |
| Edmonton | `nr_all` | 11.19 pp | 12.50 pp | +1.31 |
| Calgary | `nr` | 11.97 pp | 12.89 pp | +0.92 |
| Calgary | `nr_linear` | 9.11 pp | 11.35 pp | +2.25 |
| Calgary | `nr_all` | 7.55 pp | 10.17 pp | +2.62 (+35%) |

Options:
- **A (recommended): the headline's start year is taxation 1999 (report 2000).**
  Taxation 1997 and 1998 stay in the CSV, with a `basis_note` saying "capped".
  Drawn, they get a marked break. This is the brief's FAIL remedy, and it is the
  only option where a "fell X pp since Y" caption is on one basis.
- **B: keep 1997 as the start, with a caption** that the first two points are
  capped and understate the core. Cheaper, but the 1997 start understates the
  fall on `nr_linear` / `nr_all` by 1.3–2.6 pp.
- **C: drop taxation 1997–1998** from the committed series. Loses the context
  that the series has an earlier stretch.

A changes `core_ring_share.csv`'s `basis_note` and the caption text, an output
change, so it is a proposal. A test now pins the finding:
`tests/test_build_share_series.py::test_capped_reports_understate_the_core`.

## What this run got wrong

- **I planned to net out Devon's 1999 anomaly** from the boundary step, from
  the 2026-09-28 finding. It had already been corrected from FIR on 2026-10-02.
  The DECISIONS row was there to read, and I read `FINDINGS_quick_audits` first
  instead. No figure here used the uncorrected value.
- **My first mutation of the new test was invalid.** It multiplied the int64
  columns, overflowed, and the test went red on a garbage value. A red for the
  wrong reason proves nothing. The re-run in floats put Edmonton's 2000 core on
  the ring's growth rate exactly, and the test failed on `0.0904 - 0.0904 >= 0.08`.
- **The causal claim is inferred, not sourced.** "The jump is the cap
  released" rests on the shape of the evidence: market classes only, every
  member, flagged by the publisher. No document states the pre-2000 rule. If
  part of the 2000 step is instead the 1999 tax roll's general reassessment
  showing through, the verdict holds, since the boundary is still uneven, but
  the cause in §2 would be wrong.
- **The FIR check is eight region sums.** Core and ring totals within 1.1% for
  1998–1999 are sums over members. A member-level uncapped figure could hide under it,
  though FIR's EA is the same metric, so that's unlikely.
