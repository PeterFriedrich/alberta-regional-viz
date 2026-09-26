# SPEC — Phase 1: the core-vs-ring assessment-share series

Written 2026-09-26. Scope decisions 1–11 are locked (`docs/DECISIONS.md`). The
reasoning behind them is in `docs/SCOPE_candidates.md`. This spec covers Phase 1
only. The later phases are listed so Phase 1's outputs are shaped for them, but
they get their own specs.

## Where Phase 1 sits

| Phase | Builds | Why in this order |
|---|---|---|
| **1** | Region membership table plus a yearly core-vs-ring non-residential assessment share for Edmonton and Calgary, from the equalized assessment reports | This is the backbone metric of the timeline, and it is checkable against the City's own figure |
| 2 | FIR provincial transfers (codes 1912/1922) and StatCan population, per capita | Decision 9. Needs the FIR fetch copied from the Edmonton repo (decision 5) |
| 3 | Boundary snapshots (AltaLIS 2014+; the 1982 boundary from ATS legal descriptions) and a curated events table | The map layer of the timeline. The history must be verified first (TODO) |
| 4 | The static map app: timeline with playhead, plus the Edmonton ⇄ Calgary split-screen snapshot | Decision 3. Needs its own architecture pass |

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
   `package_show?id=2368-657x` on open.alberta.ca (OGL-Alberta). The quirks are
   listed in `data/DATA.md` §"equalized assessment report (PDF series)".
2. **`data/regions.csv`**: hand-maintained and committed. It is the single
   source of region membership. Columns:
   - `muni_id`: a stable internal id that survives renames and status changes
   - `name`: current official name
   - `region`: `edmonton` | `calgary`
   - `role`: `core` | `ring`
   - `eq_aliases`: `|`-separated names as they appear in the reports (e.g.
     `Foothills No. 31, M.D. Of|FOOTHILLS COUNTY`)
   - `member_basis`: e.g. `EMRB 2025`
   - `notes`: status changes, with dates

   Dissolved municipalities merged into a member (decision 8) are added as
   extra alias rows pointing at the absorbing `muni_id`.

## Modules (`src/`, each independently runnable)

1. **`fetch_equalized.py`**: downloads every report PDF into
   `data/raw/equalized/` (gitignored). Writes `data/raw/equalized/manifest.json`,
   one entry per file: report year, URL, retrieval timestamp (UTC), bytes,
   sha256, and the CKAN `last_modified`. It re-downloads only when the sha256
   differs. It fails hard if the CKAN listing has fewer years than the manifest
   (a year vanished).
2. **`parse_equalized.py`**: turns the PDFs into
   `data/processed/equalized_long.csv` with columns `report_year,
   muni_type, muni_name_raw, class, value, source_file, page`. It detects the
   column set from the header on each page (7 or 8 value columns) rather than
   assuming it. Image-only years (2009, 2010) are **listed in the output log as
   skipped, with the reason**, and never silently absent.
3. **`build_share_series.py`**: joins the long table to `regions.csv` through
   `eq_aliases` and writes `data/processed/core_ring_share.csv`, one row per
   `(region, report_year, basis)`, with columns `core_value, ring_value,
   core_share, n_members_found, n_members_expected`. It also writes a
   per-municipality file for the later stacked layer.

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
   point of 60% for the report year that corresponds to assessment year 2022.
   The spike gave 60.5% (report 2022) and 59.6% (report 2023). Only one of
   those two is the right year to compare, and the test pins which one.
3. **Year semantics resolved:** the mapping from report year to assessment
   year and condition date is confirmed from the report text or Municipal
   Affairs documentation. It is recorded in `data/DATA.md` and carried as an
   `assessment_year` column. Acceptance 2 cannot pass without it.
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

## Out of scope for Phase 1

- OCR of 2009–2010. Revisit only if the timeline needs 2008–09. The City's 72%
  anchor is a 2008 figure, so the series will start one or two years later
  than the City's, and the chart says so.
- The pre-2009 FIR raw-assessment fallback.
- The CMA variant (decision 8). It goes in Phase 2 alongside the StatCan work.
- Any web output.

## Dependencies

`requirements.txt` gains `pypdf` and `pandas` (pinned). `requirements-ci.txt`
gains only what the synthetic tests import.
