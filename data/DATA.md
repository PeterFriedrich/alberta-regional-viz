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

⚠️ Unless a section says it was fetched into this repo (the equalized PDFs, the
FIR workbooks), it was verified in the Edmonton repo on the dates shown and
**has not been re-fetched since**.

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
- **Verified:** FIR workbooks fetched and fingerprinted here 2026-10-01 (below); tax-rates and equalized XLSX not since 2026-07-18.
- **Rows / columns:** one row per municipality-year; Schedule MR: `MR(1)` municipal levy, `MR(2)` taxable assessment by class, `MR(3)` mill rates; 51 sheets per workbook.
- **Quirks:** cross-municipality assessment *levels* need the equalized report. Raw FIR assessment is annual market value, but municipal assessment levels and bases differ, and equalized = taxable ÷ assessment level (corrected 2026-09-26: the old wording blamed missing revaluation, which is wrong). Within-year shares only with care.
- **Transfers** (per the 2024 FIR Manual, p. 11, checked 2026-09-26): line 1902 federal capital, **1912 provincial operating**, **1922 provincial capital**, 1931/1932 local government operating/capital. Revenue is recognized under PS 3410, not as cash allocated. Class buckets are not 1:1 with municipal tax classes (an "Other" bucket). Manual, reviewed input: re-fetch annually, eyeball the diff, commit.

#### Fetched into this repo (2026-10-01): `src/fetch_fir.py` → `src/fingerprint_fir.py`
- **Package:** CKAN `package_show?id=municipal-financial-and-statistical-data`.
  The slug and the id `cde4c4fd-a0b2-4816-af43-13de7a3fd3e3` resolve to the same
  package. It has 13 resources: workbooks for 2017–2025, a `2026_Tax_Rates.xlsx`,
  and three era zips (2009–2016, 2003–2008, 1994–2002). **Coverage is financial
  years 1994–2025**, with no gap. The publisher re-stamped the 2022–2025
  workbooks in July–September 2026, so expect restatements.
- **Raw files** go to `data/raw/fir/` (not committed), with a `manifest.json`
  (sha256, retrieval time, publisher `last_modified`). **The committed
  fingerprint is `data/fir_schema.json`.** It records every sheet of every file:
  title, header row, item-code row, municipality-row count, and the YEAR values
  in the rows. `tests/test_fir_schema.py` pins the facts below against it.
- **Four layouts:**
  - **2009+:** one workbook per year, one sheet per schedule (`D(1)-Total`,
    `EA(1)-Assessment`, `POPL(1)-Population`, …).
  - **1994–2000 and 2004–2008:** one `.xlsx` per schedule, `YYYY/YYYY-<schedule>.xlsx`.
  - **2001:** legacy `_colN.XLS` files with **no item-code row**.
  - **2002 and 2003:** legacy `.xls` in sub-folders. `2003-EA-MR/` ships in
    *both* era zips, byte-identical (checked).
- **Every sheet:** row 2 (the YEAR row) is the header, and the next row holds
  5-digit item codes (`01920`). Municipality rows carry a 4-digit `CODE`
  (Edmonton `0098`, Calgary `0046`). The codes are in `data/regions.csv` → `fir_code`.
- ⚠️ **Lines 1912/1922 exist only from 2023.** From 1994 to 2022 the provincial
  transfer lines are **01910 "Unconditional" / 01920 "Conditional"**, which is a
  different cut from operating/capital. The two can't be spliced. Decision 9
  is amended (2026-10-01): the headline is the total of the two lines.
- ⚠️ **MR(2) taxable assessment by class exists only from 2023** (sheet
  `MR(2)-Assessment`). 2009–2022 have no MR(2). 1998–2008 have per-class `MR-*`
  files. Their columns 08200–08240 look like assessment, but this is unverified.
- **EA (equalized assessment) is published in FIR for 1997–2025**, with
  columns for Linear, M&E, Non-Residential, Railway and Co-gen M&E subtotals.
  This is the same metric as the Phase 1 PDFs, published a second time. It is
  not an independent valuation, but it can catch parse slips and print typos.
  2001's `EQASSMT 2001.XLS` has no railway column, and its title says "figures
  downloaded as of November 2002 and can change".
- **The `2001/` folder holds some 2002 data.** `EQASSMT 2002.XLS` and both
  `Mr_col*.XLS` files carry YEAR 2002 in their rows. A parser must use the
  row's YEAR, not the folder name.
- **FIR has no "City of Calgary (Part II)" row.** Code 0046 is "CALGARY" in
  every year. Compare this with the PDF alias in `regions.csv`.
- **Unreadable files:** `sir Form.xls` (2003) and the root-level
  `Statistical_Return.xls` are encrypted. Together with `Financial_*.xls`, they
  look like blank return forms, not data. They are recorded in the fingerprint
  as `unreadable`.

#### Parsed (2026-10-02): `src/parse_fir.py` → `data/processed/fir_long.csv`
- **Year mapping: FIR financial year Y = equalized REPORT year Y** (taxation
  year Y−1). Member-level NR/linear/M&E match the parsed PDFs exactly on 1,048
  of 1,532 values at that offset, and on ≤ 12 one year either side
  (`test_fir_year_is_the_equalized_report_year`).
- **FIR vs PDF, same report year:** 68% exact, 89% within 1%, 98% within 5%.
  Where they differ, FIR is usually *lower* (402 lower vs 82 higher). The cause
  is unknown (a later revision? a different inclusion rule?). It is TODO, and
  it matters because FIR could fill the PDF gap (below).
- **FIR covers report years 2008–2010**, which is the scanned-PDF gap that holds
  Edmonton's 72% anchor year. This is not used yet (TODO).
- **The four kept-as-printed anomalies:** in each case FIR's row adds up to its
  own total and sits within 25% of its neighbours' midpoint. The printed value
  is ≥ 40% off. Airdrie 2017 is the clearest: the PDF total omits NR, while
  FIR's total includes 1,548M. Devon 1999 differs in NR, linear *and* M&E, but
  its residential matches. See `test_fir_resolves_the_four_kept_as_printed_anomalies`.
  **Corrected 2026-10-02**, six cells, in `data/corrections.csv`. FIR 2001's NR
  column includes railway: it matches the PDF's NR-incl-railway exactly for 14 of 21
  members.
- **FIR's own error: Calgary 2001 NR = 1,622.9M** in the legacy `EQASSMT 2001.XLS`
  (PDF: 16,560M). FIR's components fall 14.6B short of its own grand total. It
  is the only EA row in FIR that doesn't add up (`test_fir_ea_rows_add_up_except_calgary_2001`).
- **No POPL sheet in the 2020–2022 workbooks** (`parse_fir.POPL_ABSENT`).
- **Electric (-E) and gas (-G) supplements** reuse Schedule D's title in the
  per-schedule eras (1994–2000, 2004–08). They are excluded by file name.
- **The 2002 copy in `2001/` is not read.** `2002/EA/` is the year's own file;
  the `2001/` copy is an earlier download whose title says "can change".
- **Blank ≠ 0:** 640 member-line values are empty cells (mostly co-gen M&E and
  railway). They are written empty, not as 0.

#### Transfers per capita (built 2026-10-02): `src/build_transfers.py` → `data/processed/transfers_per_capita.csv`
Committed, 625 rows: 21 members plus core and ring for each region, × 2001–2025.
Columns: `region, level (member|side), unit, role, year, transfers, population,
per_capita, per_capita_5yr, basis_note`. Nominal dollars.
- **Absorbed villages:** `fir_long.csv` files Blackie (0032), Entwistle (0104),
  New Sarepta (0234) and Wabamun (0364) under the absorbing member's `muni_id`,
  with their own `fir_code`. Their Schedule D rows end in 1997, 2000, 2009 and
  2020. EA keeps all-zero placeholder rows for Blackie and Entwistle until 2004.
  New Sarepta and Wabamun print their names in capitals in some eras.
- **Negative line:** Spruce Grove 2015 conditional transfers are −$1,760,210, after
  $20.1M in 2014. This looks like a reversal of grant revenue recognised the year
  before. It is kept as printed and named in `basis_note` (member and ring rows).
- **No blank transfer values** in any member-year.

#### Spending per capita (built 2026-10-02): `src/build_spending.py` → `data/processed/spending_per_capita.csv`
Committed, 2,300 rows: 21 members plus core and ring for each region, × police,
transit and FCSS for 2001–2025, and housing for 2009–2025. Columns: `region, level,
unit, role, function, year, gross, user_charges, net, population, gross_per_capita,
net_per_capita, excluded, basis_note`. Nominal dollars. Basis: `docs/SPEC_phase1.md`
§"Phase 2b basis" and §"The 2009 accrual switch, measured".
- **`fir_long.csv` schedules added:** `C_OP` (Schedule C Operating expenditure,
  1994–2008), `C` (Schedule C REVENUE/EXPENSE – TOTAL, 2009–2025), `E_AMORT`
  (Schedule E Annual Amortization Expense, 2009–2025) and `E_UC` (Schedule E Sales
  and User Charges, 1994–2025), for the four functions. Schedule E's sheets share
  function codes (02250 police, 02350 transit, 02440 FCSS, 02520 housing), so a
  row is identified by schedule *and* line code. 2001 is mapped by function name.
- **Pre-2009 Operating carries no amortization.** Schedule D Operating has an
  amortization line (02110), and every member reports $0 in it for 2003–2008.
- **Blank cells count as 0** here: C 6, E_AMORT 10, E_UC 58 member-lines
  (e.g. Foothills 2009 police, transit and housing).
- **Negative gross:** 12 member-function-years, all small, where 2009+
  amortization exceeds Schedule C expense (Morinville transit −$11,730 a year
  2020–24). Kept as printed and named in `basis_note`.
- **Police zeros:** Foothills to 2020; Parkland 2012–25 except 2018; Rocky View
  2012–25; Sturgeon 2001–25 except 2011; Cochrane 2022; Devon 2021.
- **Calgary FCSS swings as printed:** Schedule C 01400 is $233M in 2022, $185M
  (2023), $136M (2024) and $245M (2025). Not investigated.
- **Annual reports used for the 2009 overlap** (Wayback copies, in
  `/home/opc/research/alberta-regional-viz/`): Edmonton 2009 Financial and
  Operational Annual Report (Consolidated Statement of Operations, p.37) and
  Calgary 2009 Annual Report (Consolidated Statement of Operations). edmonton.ca
  serves its reports from 2010 only. From this box it needs the certifi CA bundle.

### StatCan — CSD crosswalk (hand-built 2026-10-02): `data/csd_crosswalk.csv`
One row per member per census year (1996, 2001, 2006, 2011, 2016, 2021):
`muni_id, census_year, csd_uid, csd_name, relation, note`. Pinned by
`tests/test_csd_crosswalk.py`. Census population is published per CSD on that
census's boundaries, so a member's population is the sum of its rows that year.
- **Sources (StatCan Open Licence):**
  - SGC structure lists 2011, 2016, 2021 (`statcan.gc.ca/en/subjects/standard/sgc/<year>/index`).
    Every 2011–2021 code and name in the file was matched against them, with no mismatches.
  - SGC concordances 1996→2001 (`sgc/2006/sgc01sgc96`), 2001→2006 (`sgc/2006/2001-2006`),
    2006→2011 (`sgc/2011/concordances-2006-2011-1`), 2011→2016 (`sgc/2016/concordance-2011-2016`).
    They list only changed CSDs, so a code absent from them is unchanged.
  - Interim List of Changes to Municipal Boundaries, Status and Names (92F0009X),
    2019–2024 issues, for 2016→2021. StatCan's 2016→2021 concordance page returned 500.
- **Every member's code is constant 1996–2021.** Only names and types change; renames
  are in `note`.
- **`relation = absorbed`**: four dissolved villages, merged into a member by
  decision 8, listed until their last census as their own CSD:
  Blackie → Foothills (gone by SGC 2001), Entwistle → Parkland County (gone by
  SGC 2001), New Sarepta → Leduc County (gone by SGC 2011), Wabamun → Parkland
  County (2021-01-01, 92F0009X 2021). They were found by listing every
  municipality that stops appearing in `equalized_long.csv`, then checked
  against the concordances. Edmonton Beach (1998–99 reports) was renamed
  Spring Lake, which is not a member.
- **Not included:** First Nations reserves inside or next to members (e.g.
  Wabamun 133A/B, Stony Plain 135, Tsuu T'ina 145). They are separate CSDs, are not
  municipalities, and have no FIR or equalized rows.
- **Boundaries are as of each census.** Annexations between members, or from
  non-members, are not adjusted. This is the same basis as the equalized assessment.
- **No CSD type column:** the SGC structure lists carry no type. Type changes
  (Beaumont, Chestermere to city; Leduc and Parkland County CM to MD) are in `note`.

### StatCan — population estimates, table 17-10-0155 (fetched 2026-10-02): `src/fetch_population.py` → `data/processed/population.csv`
July 1 estimates by CSD on **2021 boundaries**, 2001–2025, release 2026-01-14
(StatCan Open Licence). Decision 2026-10-02. The output is committed, 525 rows:
`muni_id, region, role, year, population, estimate_status, csd_uid, release`.
- **Source:** the full-table CSV `www150.statcan.gc.ca/n1/tbl/csv/17100155-eng.zip`.
  `releaseTime` and the footnotes come from WDS `getCubeMetadata`. The raw zip and
  `manifest.json` (sha256) are in `data/raw/population/` (gitignored).
- **Join:** the last 7 digits of `DGUID` (`2021A0005` + CSD code) against the
  2021 member rows of `data/csd_crosswalk.csv`. Absorbed villages need no rows here:
  on 2021 boundaries they are already inside their member.
- **Estimate status** is parsed from the table footnote: final intercensal
  2001–2020, final postcensal 2021, updated postcensal 2022–2024, preliminary
  2025. A release that rewords the footnote fails the fetch.
- **The estimates are 0–6% above the 2021 census counts** (98-10-0002), because they
  correct for undercoverage. Edmonton +4.0%, Fort Saskatchewan +5.5%,
  Parkland +2.9%. Never mix them with census counts in one series.
- **Annexations are back-cast** to 2021 boundaries, unlike the equalized
  assessment, which uses each year's boundaries.
- Replaces the inactive 17-10-0142 (2016 boundaries).

### Candidate sources — UNVERIFIED, not yet used
Carried over from the retired claude.ai spec (2026-10-01). None has been fetched
or checked here; verify licence, URL and coverage before adding a full entry above.
- **StatCan:** 2021 CSD profiles, commuting tables 98-10-0459 / 0460 / 0462, 2021
  boundary files (StatCan Open Licence).

- **AltaLIS municipal boundaries** (annual snapshot): Phase 3.
- **Police Funding Model** municipal tables, one XLSX, 2020-21 → 2024-25 (parked,
  decision 2026-09-30).
- **Alberta Regional Dashboard** CKAN exports; **ETS / Calgary Transit GTFS**;
  **Socrata** elections (Edmonton `32te-6grv`, Calgary `tty8-276j`), permits,
  assessment. None is needed by Phases 1–4 as scoped.
- **Homeward Trust PiT counts:** not OGL, so confirm the reuse terms first (parked).

