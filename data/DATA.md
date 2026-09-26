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
  - The report is dated Oct/Nov of the prior year. The report year ≠ the assessment year, and the mapping is **unconfirmed**.
  - Each row's classes sum to its Grand Total. Use that as the parse check.
  - Dissolutions are noted in the page header (e.g., Hythe → County of Grande Prairie, 2022).

### Alberta Municipal Affairs — FIR workbooks, tax rates, equalized assessment
- **Publisher / URL:** `open.alberta.ca/opendata/municipal-financial-and-statistical-data` (FIR/SIR yearly workbooks 2003–2025, zips to 1994; `2026_Tax_Rates.xlsx`), `open.alberta.ca/dataset/equalized-assessment-report` (XLSX 2024–2026).
- **Licence:** OGL-Alberta.
- **Verified:** 2026-07-18 — **not since**; the Edmonton repo pulls these workbooks routinely (`fetch_fir_debt.py`, `fetch_fir_tax_base.py`), so the fetch idiom is proven.
- **Rows / columns:** one row per municipality-year; Schedule MR: `MR(1)` municipal levy, `MR(2)` taxable assessment by class, `MR(3)` mill rates; 51 sheets per workbook.
- **Quirks:** cross-municipality assessment *levels* need the equalized report. Raw FIR assessment is annual market value, but municipal assessment levels and bases differ, and equalized = taxable ÷ assessment level (corrected 2026-09-26: the old wording blamed missing revaluation, which is wrong). Within-year shares only with care.
- **Transfers** (per the 2024 FIR Manual, p. 11, checked 2026-09-26): line 1902 federal capital, **1912 provincial operating**, **1922 provincial capital**, 1931/1932 local government operating/capital. Revenue is recognized under PS 3410, not as cash allocated. Line-code stability across 2003–2025 is unverified, so build a code dictionary from each year's manual before concatenating. Class buckets are not 1:1 with municipal tax classes (an "Other" bucket). Manual, reviewed input: re-fetch annually, eyeball the diff, commit.
