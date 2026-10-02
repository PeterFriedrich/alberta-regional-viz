# SPEC — Phase 1: the core-vs-ring assessment-share series

Written 2026-09-26. Scope decisions 1–11 are locked (`docs/DECISIONS.md`). The
reasoning behind them is in `docs/SCOPE_candidates.md`. This spec covers Phase 1
only. The later phases are listed so Phase 1's outputs are shaped for them, but
they get their own specs.

## Where Phase 1 sits

| Phase | Builds | Why in this order |
|---|---|---|
| **1** | Region membership table plus a yearly core-vs-ring non-residential assessment share for Edmonton and Calgary, from the equalized assessment reports | This is the backbone metric of the timeline, and it is checkable against the City's own figure |
| 2 | FIR total provincial transfers and StatCan population, per capita | Decision 9, as amended 2026-10-01. Needs the FIR fetch copied from the Edmonton repo (decision 5) |
| 2b | FIR spending by function, per capita, core vs ring: Police, Public Transit, Family and Community Support + Public Housing Operations | The "what each side carries" half of the backbone. Same FIR fetch and population as Phase 2 |
| 3 | Boundary snapshots (AltaLIS 2014+; the 1982 boundary from ATS legal descriptions) and a curated events table | The map layer of the timeline. The history must be verified first (TODO) |
| 4 | The static map app: timeline with playhead, plus the Edmonton ⇄ Calgary split-screen snapshot | Decision 3. Needs its own architecture pass |

### The backbone (locked 2026-09-30)

One question: **how does the regional tax base split between core and ring over
time, and what does each side carry?** Phase 1 is the base, Phase 2 the money in
(transfers), Phase 2b the costs carried (spending by function), Phases 3–4 put
them on the timeline and map.

- **Phase 2b source.** FIR Schedules C (revenue) and E (expenses) break out, per
  municipality, the functions *Police*, *Other Protective Services*, *Public
  Transit*, *Family and Community Support* and *Public Housing Operations*
  (checked in the 2024 workbook only, 2026-09-30). Their line codes across
  2003–2025 are unverified: build the per-year code dictionary `data/DATA.md`
  already requires before concatenating. Net-of-own-revenue vs gross spending is
  a Phase 2b spec decision.
- **Shelter** has no FIR line. FCSS + public housing is the nearest proxy, and
  a chart must say so.
- **Parked** (not in Phases 1–4; revisit after Phase 2b ships):
  - the mandate register (fiscal-gap figures that exist only in PDFs, hand-curated);
  - homeless/shelter counts (Homeward Trust PiT is not OGL);
  - the Police Funding Model as a series (2020-21 → 2024-25 only; already ruled
    out as a transfer).
- **Research topic only:** the "lost tax base + lost votes → ring-vs-core
  coalition" idea. It came from the 2026-09-26 research brief, is unverified, and
  no output asserts it (`docs/SCOPE.md`). Annexation events on the timeline are
  factual annotations.

### Transfers basis (decided 2026-10-01)

Decision 9 named FIR lines 1912 (provincial operating) and 1922 (provincial
capital). The fetch showed those lines exist only from financial year 2023
(`data/DATA.md` §"Fetched into this repo"). From 1994 to 2022 the provincial
transfer lines are 01910 *Unconditional* and 01920 *Conditional*. That is a
different cut, not a renaming.

| $M (FIR D(1)) | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| Edmonton, uncond./cond. → oper./capital | 0 / 386 | 0 / 453 | 87 / 431 | 106 / 411 | 92 / 457 |
| Edmonton, total | 386 | 453 | 518 | 517 | 549 |
| Calgary, uncond./cond. → oper./capital | 55 / 344 | 47 / 373 | 170 / 300 | 170 / 463 | 176 / 488 |
| Calgary, total | 399 | 420 | 469 | 633 | 664 |

- **Headline: the total.** It is 01910+01920 through 2022 and 01912+01922 from
  2023. It is the only basis that means the same thing in every year, and it
  shows no step at the reclassification in these two cores. A continuity test
  over every member lands with `parse_fir.py`.
- **Detail panel:** operating vs capital, 2023 onward only.
- **Unchanged from decision 9:** per capita, 5-year rolling averages,
  program-break markers at 2014, 2021–23 and 2024, and the separate
  "formula intent" panel for grantor allocations. **Added:** a 2023
  "FIR reclassification" marker.
- **Rejected:**
  - Plotting unconditional/conditional before 2023 next to operating/capital
    after it. Edmonton's unconditional line is 0 in every year checked
    (2019–2022), so the old split carries no information for the core.
  - Operating/capital from 2023 only. Three years is not a timeline.

## Phase 1 goal

For every report year that has a text layer (2011–2026), produce each region's
core share of non-residential equalized assessment under **three class bases**.
Every number is traceable to a PDF page and row:

| Basis id | Classes in the numerator and denominator | Role |
|---|---|---|
| `nr` | Non-residential (non-regulated) | **Headline** (decision 10) |
| `nr_linear` | + NR linear + NR railway | Matches the City's UPE01548 series (spike) |
| `nr_all` | + co-generating M&E + M&E | Shown as the stacked layer (decision 10) |

Core = Edmonton / Calgary. Ring = the other members of the region's fixed set
(decision 8: 13 EMRB members / 8 CMRB members, applied to every year).

## Inputs

1. **The equalized assessment report PDFs**: the resource list comes from CKAN
   `package_show?id=2368-657x` on open.alberta.ca (OGL-Alberta), plus
   `1844032` for reports 1998–2008 (Phase 1b). The quirks are
   listed in `data/DATA.md` §"equalized assessment report (PDF series)".
2. **`data/regions.csv`**: hand-maintained and committed. It is the single
   source of region membership. Columns:
   - `muni_id`: a stable internal id that survives renames and status changes
   - `name`: current official name
   - `region`: `edmonton` | `calgary`
   - `role`: `core` | `ring`
   - `eq_aliases`: `|`-separated names as they appear in the reports (e.g.
     `Foothills No. 31, M.D. Of|FOOTHILLS COUNTY`)
   - `fir_code`: the province's 4-digit municipal code in the FIR workbooks
     (Phase 2; added 2026-10-01). FIR rows are matched on it, not on the name.
     Each member's code is constant across every FIR equalized-assessment
     schedule, 1997–2025.
   - `member_basis`: e.g. `EMRB 2025`
   - `notes`: status changes, with dates

   Dissolved municipalities merged into a member (decision 8) are added as
   extra alias rows pointing at the absorbing `muni_id`.

## Year semantics (resolved 2026-09-27)

The Municipal Affairs *Guide to Equalized Assessment in Alberta* §5 says the
2010 equalized assessment reflects the 2009 assessment roll: assessments
prepared in 2008 for taxation in 2009. So:

**`taxation_year = report_year − 1`**

Assessments are prepared in the year before that. Every output carries both
`report_year` and `taxation_year`. Charts are labelled by `taxation_year`,
which is the year a municipality's own reports (e.g. UPE01548) use.

## Parser approach (decided 2026-09-27)

**Read positioned words (`pdfplumber`), not text lines.** In the 2012–2016
layouts a zero is printed as a *blank cell*. Beaumont's 2014 row has 6
numbers for 8 columns, so a line-based parser cannot know which columns are
empty. Values are right-aligned, and each column's right edges agree to
within about 1 pt (measured on the 2014 report). The parser:

1. finds the header words on each page and derives an ordered column list
   with each column's right-edge x from the numbers beneath it;
2. assigns every numeric token on a municipality row to the column whose
   right edge it matches (within 3 pt). A token matching no column fails the
   page;
3. treats a column with no token on that row as 0, and records that it was
   blank rather than an explicit 0.

A row whose value lands in the wrong column **still sums to its total**, so
reconciliation alone cannot catch a placement error. The alignment check in
step 2 is the guard for placement.

## Modules (`src/`, each independently runnable)

1. **`fetch_equalized.py`**: downloads every report PDF into
   `data/raw/equalized/` (gitignored). Writes `data/raw/equalized/manifest.json`,
   one entry per file: report year, URL, retrieval timestamp (UTC), bytes,
   sha256, and the CKAN `last_modified`. It re-downloads only when the sha256
   differs. It fails hard if the CKAN listing has fewer years than the manifest
   (a year vanished).
2. **`parse_equalized.py`**: turns the PDFs into
   `data/processed/equalized_long.csv` with columns `report_year,
   taxation_year, muni_type, muni_name_raw, class, value, was_blank,
   source_file, page`. It detects the
   column set from the header on each page (7 or 8 value columns) rather than
   assuming it. Image-only years (reports 2009, 2010) are **listed in the output log as
   skipped, with the reason**, and never silently absent.
3. **`build_share_series.py`**: joins the long table to `regions.csv` through
   `eq_aliases` and writes `data/processed/core_ring_share.csv`, one row per
   `(region, report_year, basis)`, with columns `core_value, ring_value,
   core_share, n_members_found, n_members_expected`. It also writes a
   per-municipality file for the later stacked layer. `core_ring_share.csv` is committed
   (the one tracked file in `data/processed/`) so CI runs the reproduction test
   against it; a rebuild that moves a share shows up as a diff.
   Before writing, `check_continuity` fails the build on a ring member whose
   basis value spikes and reverts (at least 40% off its neighbours' midpoint, with
   the neighbours agreeing within 30%), drops to zero, or jumps at least 40% in the
   newest report year. Each flag must also move the core share by at least
   0.25 pp. The core is not checked. Printed values that have been inspected are
   listed in `KNOWN_ANOMALIES` and logged as warnings. An entry that stops firing
   also fails. Before the check, `apply_corrections` replaces the printed values
   listed in the committed `data/corrections.csv` (FIR-verified; DECISIONS
   2026-10-02). It fails if a listed printed value is no longer what the report
   gives. `member_assessment.csv` keeps the printed value in `printed_value`, and
   `core_ring_share.csv` names each corrected cell in `basis_note`. Sizing: `docs/FINDINGS_quick_audits_2026-09-28.md` §#4.

Phase 2 (FIR):

4. **`fetch_fir.py`** → `data/raw/fir/` + manifest (as `fetch_equalized.py`).
5. **`fingerprint_fir.py`** → the committed `data/fir_schema.json`: every
   sheet's header, code row, row count and row YEARs; pinned by
   `tests/test_fir_schema.py`.
6. **`parse_fir.py`** → `data/processed/fir_long.csv` (committed, so CI runs
   the cross-checks in `tests/test_parse_fir.py`): one row per member, FIR year
   and line, for the transfer lines (decision 9 as amended), the EA subtotals
   (1997+) and POPL, with the file and sheet each came from. **FIR year Y
   carries equalized REPORT year Y** (taxation year Y−1); see
   `data/DATA.md` §"Parsed (2026-10-02)".

Every module writes structured (JSON-lines) logs, not prints, and takes its
paths from arguments with repo defaults.

## Guards (no silent drops)

- **Row reconciliation:** for every parsed municipality row, the sum of the
  classes equals the Grand Total **exactly**. Any mismatch fails the parse.
- **Membership completeness:** every `regions.csv` member must be found in
  every parsed year, or the build fails and names the missing member and year.
  The spike's Beaumont/Devon 2012–2016 miss is exactly the defect this catches.
  An alias that matches two rows also fails.
- **Denominator sanity:** each report's type-subtotal rows, where present,
  equal the sum of their member rows (checks that no row was lost on a page
  break).
- **Download completeness:** the number of manifest entries equals the number
  of CKAN resources whose name matches the report pattern.

## Acceptance criteria

1. `core_ring_share.csv` has 16 report years × 2 regions × 3 bases, with
   `n_members_found == n_members_expected` in every row. The 2009 and 2010
   report years are recorded as skipped (image-only).
2. **Reproduction check** (the pipeline's first data test,
   `test_reproduces_upe01548`): Edmonton `nr_linear` is within ±1.0 percentage
   point of 60% for taxation year 2022 (report 2023). The spike gave 59.6%.
   Taxation year 2010 (report 2011; the spike gave 71.1%) must be ≤ 72%,
   consistent with the City's decline from its 2008 anchor.
3. **Year semantics** are carried as the `taxation_year` column (see §"Year
   semantics").
4. Unit tests run on synthetic fixtures only, offline (CI installs nothing
   beyond `requirements-ci.txt` plus whatever a test genuinely needs):
   alias join, both column layouts (7 and 8), reconciliation failure,
   missing-member failure, double-match failure. The reproduction test reads
   the real processed file and is skipped (with a reason) when the file is
   absent.
5. `DATA.md`, `DATA_ISSUES.md` (the 2009–2010 image-only PDFs, which are worth
   telling the publisher about) and `DECISIONS.md` are updated. Decision 10's
   row gains its test id.

## Every output carries its basis

This follows the CLAUDE.md rule on cross-municipality numbers. Each share row
and every later chart label states:

- equalized, not raw
- the class basis id
- "2025 board membership applied to all years"
- report year and assessment year

A share with no basis is a wrong number that looks right.

## Phase 1b (built 2026-09-28)

The 1998–2007 reports (publication `1844032`) extend the series back to
taxation year 1997. The gap for taxation years 2007–2009 stays, because
reports 2008–2010 are image-only.

- **Fetch:** `fetch_equalized.py` reads both CKAN packages, each with its own
  resource-name pattern. A report year listed by both fails.
- **Layouts:**
  - Reports 2005–2007 use the 2011+ layout unchanged.
  - Reports 1998–2004 print 4 classes plus the total. Their class set is
    residential including farmland, NR, M&E and linear, and M&E prints left
    of linear.
  - Old-layout columns are named from the header's x-positions, never assumed,
    and are stored under two new classes: `residential_incl_farmland` and
    `nr_incl_railway`.
- **Railway is inside the old NR column.** The evidence is Jasper National Park:
  - I.D. No. 12 in the 2005 report: NR 7.2M, railway 5.6M, linear 10.9M.
  - The same I.D. in the 2004 report: NR 17.4M, linear 10.8M, and no railway
    column.
  - Linear matches across the two years, so the 5.6M of railway can only sit
    inside the 2004 NR figure. Beaver County agrees.
- **Bases for 1998–2004 reports** (`build_share_series.OLD_BASES`):
  - `nr_linear` and `nr_all` map exactly.
  - `nr` is NR including railway, and its `basis_note` says so.
  - Railway was 0.03–0.6% of NR in the 2007–2019 reports, so it moves a core
    share by about 0.1 pp at most.
- **Split rows:** the 1998 report prints "City of Calgary (Part II)" as a second
  Calgary row. A `+`-prefixed alias in `regions.csv` sums it into Calgary. It is
  logged, and a non-`+` duplicate still fails.
- **Guard:** the parser rewrite left the 2009–2026 rows of
  `equalized_long.csv` byte-identical, which was checked against a pre-change
  copy. The committed `core_ring_share.csv` only gained rows.

## Out of scope for Phase 1

- OCR of reports 2008–2010 (taxation years 2007–2009): all three are scanned
  images. The City's 72% anchor (taxation year 2008) is in this gap, and the
  chart says so until OCR fills it.
- The CMA variant (decision 8). It goes in Phase 2 alongside the StatCan work.
- Any web output.

## Dependencies

`requirements.txt` gains `pdfplumber` (pinned; pandas turned out unnecessary). `requirements-ci.txt`
gains only what the synthetic tests import.
