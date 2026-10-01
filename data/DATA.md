# Data Sources

Reference for raw input files. Update this file when you discover column name
quirks, encoding issues, or anything unexpected. Do not rely on memory — write it
down here. A defect in the *publisher's* data goes in `docs/DATA_ISSUES.md`,
with a status saying whether they have been told.

**Download completeness:** an API that pages or caps truncates *silently* — it
returns exactly that many rows with no error. ArcGIS REST caps at
`maxRecordCount` per call (paginate with `resultOffset` + `orderByFields`);
every downloader verifies its row count against the live
`returnCountOnly=true` count and fails hard on a mismatch.

**Vintage:** record, per source, the dataset id, the retrieval timestamp and
the publisher's own last-updated stamp. A guard must measure the DATA (row
counts, max date in the file), never a metadata string that can go stale
while the guard stays green.

⚠️ Everything below was verified in the Edmonton repo on the dates shown and
**has not been re-fetched since**. Nothing has been downloaded into this repo.

## Sources

### St. Albert — LandScape property info (ArcGIS Online)
- **Publisher / URL:** City of St. Albert, ArcGIS Online org `fyyY0cNXvmUWvX1x`;
  `https://services1.arcgis.com/fyyY0cNXvmUWvX1x/arcgis/rest/services/LandscapePropertyInfo2026/FeatureServer/0`
  (prior year: `LandscapeTaxAssessment2025_view`). The on-prem `gis.stalbert.ca` server is decommissioned (301).
- **Licence: UNRESOLVED** — not catalogued on `data.stalbert.ca`; no `licenseInfo` on the item. **Do not bulk-pull or commit per-parcel rows.** Server-side `outStatistics` aggregates are the permitted fallback pending the City's answer.
- **Verified:** 2026-07-17 — **not since**
- **Rows / columns:** 29,366 (2026); `Roll_Number`, `Neighbourhood`, `Property_Class`, `Assessment_Class` (code), `Assessment_Description`, `LotSize_sqm`, `Assessment_Year`, `Assessed_Value`, `CurrentTaxLevy`, `Year_Built`, `Shape__Area`. `maxRecordCount` 2000.
- **CRS:** wkid 102187 / **EPSG:3776** (NAD83 / Alberta 3TM 114°W) — reproject to EPSG:3400 on ingest.
- **Quirks:** `CurrentTaxLevy` is the TOTAL bill (municipal + education + Heartland) — validated by rate arithmetic (res ≈ 11.08/$1000, non-res 17.587/$1000); back the education share out for municipal-only comparisons. Exempt classes carry value with levy = 0 (a real zero). Service name embeds the year — expect it to roll.

### Strathcona County — property tax assessment (ArcGIS Hub, annual)
- **Publisher / URL:** Strathcona County Open Data, org `B7ZrK1Hv4P1dsm9R`, hub `opendata-strathconacounty.hub.arcgis.com`; one service per tax year 2012–2026 (2016 absent). 2026: item `211214c329394005a5a3c43a277b0d38`, layer `.../services/2026%20Property%20Tax%20Assessment/FeatureServer/0`.
- **Licence:** Open Government Licence – Alberta (catalogued; attribution required).
- **Verified:** 2026-07-17 — **not since**
- **Rows / columns:** 43,365 (2026); `roll`, `address`, `bldg` (dwelling type), `assess_2025` (field name embeds the valuation year), `parcelarea` + `measured_in` ("Acres" / "Sq. Mete" / "Units"), `latitude`/`longitude`. `maxRecordCount` 1000. **No class field, no levy.**
- **CRS:** point geometry, lat/lon — every vintage checked. No polygons; lot area is an attribute.
- **Quirks:** residential-improved only — the county's heavy-industrial base is absent. ⚠️ **Whole-building value repeated on every unit record** for some complexes (6101 Eton Blvd: 259 rows × $70.7 M) but not others; naive sum $116.8 B, strict dedup $21.3 B; dedup rule unsolved. Mill rates: municipal res 4.5822 / non-res 10.9933 per $1000 (2026 bylaw); history table at `strathcona.ca/.../tax-rates/` is server-rendered, plain scrape works.

### Alberta Municipal Affairs — equalized assessment report (PDF series)
- **Publisher / URL:** open.alberta.ca publication `2368-657x` (list the resources via CKAN `package_show?id=2368-657x`). One PDF per report year, 2009–2026.
- **Licence:** OGL-Alberta.
- **Verified:** 2026-09-26 (spike: `docs/SCOPE_candidates.md` §"Spike").
- **Columns:** Municipality Type, Municipality, Residential, Farmland, Non Residential (Non regulated), NR Linear Property, NR Railway (present through the 2019 report, absent from 2020), NR Co-generating M&E, Machinery and Equipment, Grand Total. Type subtotal rows are unlabelled.
- **Quirks:**
  - **2009 and 2010 are scanned images with no text layer.** 2011+ extract with `pypdf`.
  - Names are mixed case up to about 2019 and upper case after. Old names differ: "Foothills No. 31, M.D. Of" (→ FOOTHILLS COUNTY); Rocky View is "Rocky View County" as early as 2011.
  - 2012–2016 layouts defeated a single-line regex for Beaumont and Devon.
  - **Year mapping: taxation year = report year − 1** (Municipal Affairs, *Guide to Equalized Assessment in Alberta* §5, `municipalaffairs.alberta.ca/documents/as/guide_to_equalized_assessment.pdf`, checked 2026-09-27). Reports are dated Oct/Nov of the prior year.
  - **2012–2016 print zero as a blank cell.** Rows have fewer numbers than columns, so place values by x-position (numbers are right-aligned per column), never by order.
  - **Older series:** publication `1844032` covers reports 1998–2008. Its resources are named "YYYY equalized assessment report", without the "Provincial" prefix. Reports 1998–2007 have a text layer; **2008 is image-only.** Parsed 2026-09-28 (`docs/SPEC_phase1.md` §"Phase 1b (built 2026-09-28)").
    - **Reports 2005–2007** use the 2011+ 8-column layout.
    - **Reports 1998–2004 layout:** 4 classes plus Grand Total: Residential (incl. farmland) / Non Residential / Machinery & Equipment / Linear. M&E prints *left* of Linear.
    - **Railway sits inside Non Residential in 1998–2004.** The evidence is I.D. No. 12 Jasper Park in 2004 vs 2005. **Co-generating M&E** has no column in these years.
    - **Section headings in the name column:** 1998–2004 print headings ("CITIES", 2001's "Rural Municipalities") where names go. 1999 and 2000 wrap long names *above* their values ("Regional Municipality of Wood" / "Buffalo 941,…"), and wrap subtotal labels around them ("TOTAL SPECIALIZED" / values / "MUNICIPALITIES").
    - **Uncovered rows:** Special Areas and Redwood Meadows sit outside every subtotal (first in 1998, last in 2002–2004). Only the grand total covers them.
    - **One-off quirks:**
      - 1998–1999 print zero as `-`, which sits about 10 pt left of the column's right edge.
      - 1999 splits the total's first digit into its own word (`7` + `32,059,142`).
      - 2004 prints Strathcona County's row without thousands separators.
      - One page of the 2000 report is shifted about 7 pt, and two 1998 rows by 3 pt; the parser anchors each row on its own total.
      - Some reports have a by-type summary page (1999 p11, 2000 p10) that is skipped.
        These pages tie to the parsed rows by class, to the dollar (audited 2026-09-28).
      - **"Capped" before 2000:** the 2000 report's history table marks the 1997–1999 totals "capped" and 2000 "uncapped" (+18.25%), and its preface says "the 2000 equalized assessment is not capped". Taxation years 1997–1998 may be on a different footing. Not yet investigated (`docs/AUDIT_LEDGER.md` #2).
    - **Names:** 1998 uses "City of Edmonton", "M.D. of Rocky View No. 44" and similar. 2001–2004 print "Airdire", and 2001 prints "Foothills No. 32" for No. 31. The 1998 report has a second Calgary row, "City of Calgary (Part II)", with no explanation in the report.
    - **Publisher rounding** (`docs/DATA_ISSUES.md`):
      - In 1999, six subtotals are off by 1–5 in the residential and grand-total columns.
      - In 2006, two row totals are off by 1 (Bassano, Swan Hills).
  - Each row's classes sum to its Grand Total. Use that as the parse check.
  - Dissolutions are noted in the page header (e.g., Hythe → County of Grande Prairie, 2022).

### Alberta Municipal Affairs — FIR workbooks, tax rates, equalized assessment
- **Publisher / URL:** `open.alberta.ca/opendata/municipal-financial-and-statistical-data` (FIR/SIR yearly workbooks 2003–2025, zips to 1994; `2026_Tax_Rates.xlsx`), `open.alberta.ca/dataset/equalized-assessment-report` (XLSX 2024–2026).
- **Licence:** OGL-Alberta.
- **Verified:** 2026-07-18 — **not since**; the Edmonton repo pulls these workbooks routinely (`fetch_fir_debt.py`, `fetch_fir_tax_base.py`), so the fetch idiom is proven.
- **Rows / columns:** one row per municipality-year; Schedule MR: `MR(1)` municipal levy, `MR(2)` taxable assessment by class, `MR(3)` mill rates; 51 sheets per workbook.
- **Quirks:** cross-municipality assessment *levels* need the equalized report. Raw FIR assessment is annual market value, but municipal assessment levels and bases differ, and equalized = taxable ÷ assessment level (corrected 2026-09-26: the old wording blamed missing revaluation, which is wrong). Within-year shares only with care.
- **Transfers** (per the 2024 FIR Manual, p. 11, checked 2026-09-26): line 1902 federal capital, **1912 provincial operating**, **1922 provincial capital**, 1931/1932 local government operating/capital. Revenue is recognized under PS 3410, not as cash allocated. Line-code stability across 2003–2025 is unverified, so build a code dictionary from each year's manual before concatenating. Class buckets are not 1:1 with municipal tax classes (an "Other" bucket). Manual, reviewed input: re-fetch annually, eyeball the diff, commit.

### Candidate sources — UNVERIFIED, not yet used
Carried over from the retired claude.ai spec (2026-10-01). None has been fetched
or checked here; verify licence, URL and coverage before adding a full entry above.
- **FIR/SIR CKAN dataset id** `cde4c4fd-a0b2-4816-af43-13de7a3fd3e3`: check that it
  is the same dataset as the open.alberta.ca slug cited above.
- **StatCan:** 2021 CSD profiles, commuting tables 98-10-0459 / 0460 / 0462, 2021
  boundary files (StatCan Open Licence). Needed for Phase 2 population, through the
  CSD crosswalk (TODO).
- **AltaLIS municipal boundaries** (annual snapshot): Phase 3.
- **Police Funding Model** municipal tables, one XLSX, 2020-21 → 2024-25 (parked,
  decision 2026-09-30).
- **Alberta Regional Dashboard** CKAN exports; **ETS / Calgary Transit GTFS**;
  **Socrata** elections (Edmonton `32te-6grv`, Calgary `tty8-276j`), permits,
  assessment. None is needed by Phases 1–4 as scoped.
- **Homeward Trust PiT counts:** not OGL, so confirm the reuse terms first (parked).

