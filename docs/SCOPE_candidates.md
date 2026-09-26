# Scope candidates — what this project could be built on, and what blocks each

Written 2026-09-18 when the project was split out of `edmonton-tax-viz`. Nothing
here is decided; the decisions at the bottom are Peter's. Both tracks were
verified against live sources in that repo (dates given); **re-fetch before
building on any figure here.**

## Track A — per-parcel peers via ArcGIS REST (capital region)

Source of truth: `docs/SPIKE_regional_lens.md` (2026-07-17). Two peers, and
they are not symmetric:

| | St. Albert | Strathcona County |
|---|---|---|
| Geometry | parcel **polygons** | **points** (every vintage) |
| Value | assessed value **and actual levy** per parcel | assessed value only |
| Classes | full multi-class roll | residential-improved only; no class field |
| History | 2025 + 2026 only | annual 2012–2026 (2016 absent) |
| Licence | **UNRESOLVED — likely not open data** (a lookup tool's backend, not a catalogued dataset) | clean: OGL-Alberta, catalogued |
| Known defect | — | whole-building value repeated on every unit record; truth ≈ $21–22 B vs naive $116.8 B |

What it supports: a citywide value-per-acre / levy-per-acre comparison on the
**lot-acre** basis (Strathcona cannot do ground acres). St. Albert alone could
support a full parallel per-parcel pipeline — the only peer with polygons +
class + levy — and that is exactly what its licence question gates.

**Blocked on (unchanged since 2026-07-17):**
1. St. Albert licensing — ask the City whether the LandScape service is
   reusable like its catalogued portal datasets. Until answered: **no raw
   per-parcel use, never committed anywhere.** Fallback: citywide aggregates
   via `outStatistics` (no bulk download) or published tax-rate-bylaw totals.
2. Strathcona dedup rule — a build-time task, independent of licensing.
3. Valuation-lag convention across the three municipalities — unchecked.

## Track B — province-wide aggregates via Alberta Municipal Affairs (OGL-Alberta)

Source of truth: `edmonton-tax-viz/docs/SPEC_industrial.md` §"Track B"
(2026-07-18; not copied here — the Edmonton repo owns that spec). The FIR
workbooks cover **every Alberta municipality, 2003–2025** (older zips to 1994),
one file per year; `2026_Tax_Rates.xlsx` carries every municipality's rates in
one file; the **equalized assessment report** (XLSX, 2024–2026) is the valid
instrument for cross-municipality *level* comparison. Raw FIR levels across
municipalities are invalid, and only within-year shares are usable with care.
The reason is that municipal assessment levels and bases differ, not that
revaluation is missing: Alberta reassesses every year (corrected 2026-09-26,
see §"Research reply").

The fetch idiom exists in the Edmonton repo (`scripts/fetch_fir_debt.py`,
`scripts/fetch_fir_tax_base.py`: manual, reviewed input; anchor cross-checks;
a `MUNICIPALITIES` stable-code dict). Candidate municipalities named there:
Edmonton, Strathcona County, Sturgeon County, Parkland County, City of Leduc,
Leduc County — but the source is province-wide, so the set is a choice.

What it supports: multi-year series per municipality of taxable assessment by
class, levy, mill rates, non-residential share. No licence question, no
per-parcel data, no geometry beyond a municipal-boundary layer (provincially
published; licence to verify).

Known open analytical question: two published series for Edmonton's regional
non-residential assessment share (76% → 72% over 15 years; 72% in 2008-09 →
60% in 2022) do not reconcile — rebuild from primary data before citing either.

**Blocked on:** nothing in the data. The blocker is the output decision — all
Track B outputs are charts/tables, not maps.

## Research brief (2026-09-26) — a third framing: the core-vs-ring timeline

Distilled from `alberta_region_timeline_update.md`, which consolidates three
earlier reports (2026-09-18/19) plus working discussion. All four live
**outside** the repo in `/home/opc/research/alberta-regional-viz/`, not
committed by design. The earlier three carry **no URLs** — citations are by
name only. Spot-checks 2026-09-26 are marked ✔/✘; everything else is unverified.

**Thesis it proposes.** Edmonton's weak share of regional tax base is
path-dependent: the 1979 bid to annex St. Albert and Strathcona County
(Refinery Row) was approved by LAB Order 14000 and nullified by the Lougheed
cabinet ✔; the 1982 annexation (O.C. 538/81) took mostly undeveloped land,
331.1 → 700.6 km² ✔; the Regional Planning Commission dissolved in 1995; the
2019 Leduc County annexation left North Nisku industrial land with the county
✔; the EMRB was dissolved 2025-04-01. The claimed original contribution is
fusing the annexation-fiscal literature with the urban-rural voting literature
into a "lost tax base + lost votes → ring-vs-core coalition" story. The brief
itself says the coalition claim is a **hypothesis**, and any precinct↔census
join is ecological inference that must be flagged on the output itself.

**Errors found in the brief:**
- ✘ "2017 Leduc annexation, ~9,500 ha". The Leduc annexation took effect
  **2019-01-01**: 8,260 ha from Leduc County plus 7 ha of 50 Street road
  allowance from Beaumont (MGB Order 050/18 of 2018-10-03; O.C. 359/2018).
  The application was filed in 2017. Any boundary snapshot is dated 2019.
- The 72% → 60% non-residential share is cited as settled. This doc (Track B)
  already records that two published series don't reconcile; rebuild it from
  primary data before citing it (the brief's own Stage 4 step 9 does this).
- Internal inconsistency on the deck.gl overlay switch: one report says
  "MapLibre v6", the consolidated brief says "past v5". Verify when it matters.
- Verified: the MapLibre 4.7.1 / deck.gl 9.0.38 pins and the ~16 MB of web
  data in `edmonton-tax-viz` (`web/data` is 17 MB).

**What it adds beyond Tracks A/B:**
1. **Calgary as the headline comparison.** The architecture assumes an
   Edmonton ⇄ Calgary map app: toggle by default, side-by-side or swipe
   compare, and camera sync by scale only (the cities are ~280 km apart).
   This repo's current scope is capital-region peers.
2. **A browser map app** built by "refactoring the existing app into a city-view
   module" (MapLibre + deck.gl, vendored, GitHub Pages). That app is
   `edmonton-tax-viz`'s. This repo must not restructure it (CLAUDE.md), so the
   code would be copied here, not refactored in place.
3. **Timeline mode.** A per-year non-residential share series from FIR (Track B
   data), boundary snapshots at annexation events (pre-1982, 1982, 2019, now;
   the 1982 and 2019 lines may need hand-digitizing from Board Order PDFs), a
   playhead-linked map and chart, and a curated events table.
4. **A Tier-2 "mandate register".** A hand-curated, cited CSV of fiscal-gap
   figures that exist only in PDFs: Calgary EC2026-0284 ($1.05 B downloaded
   2016–2026); Edmonton FCS02218's five categories, which deliberately give no
   total; and LGFF/MSI allocations, with the 2023→2024 MSI→LGFF program break
   annotated. Edmonton's eScribe portal blocks bots, so documents are
   downloaded by hand.
5. **More sources:**
   - Police Funding Model XLSX (per municipality, 2020-21 → 2024-25)
   - Alberta Regional Dashboard
   - StatCan 2021 CSD profiles and commuting flows (98-10-0459/0460/0462-01)
   - StatCan and AltaLIS boundaries
   - GTFS feeds
   - Socrata precinct results (Edmonton `32te-6grv`, Calgary `tty8-276j`)
   - Homeward Trust PiT counts, which are **not** OGL: check the terms first
   - No official Alberta-municipal-code ↔ CSD crosswalk exists, so one has to
     be hand-built.
6. **A recommendation for scheduled (cron) refresh of the Tier-1 data.** This
   conflicts with Track B's "manual, reviewed input until there is a reason".
   Changing it changes CI, so it needs a proposal first.

## Research reply (2026-09-26): region, transfers, normalization

Distilled from `edmonton_calgary_core_ring_timeline.md` (out-of-repo, same
folder). It answers the prompt `region_transfers_normalization_prompt.md` for
decisions 8–10. Unlike the earlier reports it has **48 URLs** and marks what it
could not verify. Local checks 2026-09-26 are marked ✔/✘.

**Corrections to what this repo said:**
- **"Raw FIR assessment is not revaluation-adjusted" is the wrong reason.**
  Alberta reassesses at market value every year. The actual problem is that
  municipal assessment *levels* and valuation bases differ, and equalized
  assessment ("taxable assessment ÷ the municipality's assessment level")
  corrects for that. The conclusion is unchanged: compare levels across
  municipalities only on equalized assessment.
- **The 72% → 60% figure is sourced now.** City of Edmonton UPE01548
  (Executive Committee, 2024-06-19, p. 5) gives Edmonton's share of *taxable
  non-residential* assessment within the 13 EMRB municipalities: 72% in 2008,
  60% in 2022. The 76% → 72% figure is CR_3019 (2016), covering about 15 years
  to around 2015 on a region that is not stated; it is a **different series,
  not the same one continued**. Neither report publishes its method (raw vs
  equalized; linear/M&E treatment).

**Recommendations (decisions 8–10, pending Peter):**
- **Region (8).** Use a fixed membership applied to every year: the 13 EMRB
  members for Edmonton (Edmonton, Beaumont, Fort Saskatchewan, Leduc,
  St. Albert, Spruce Grove, Strathcona County, Leduc County, Parkland County,
  Sturgeon County, Devon, Morinville, Stony Plain), and the 8 CMRB members for
  Calgary (Calgary, Airdrie, Chestermere, Cochrane, Foothills County,
  High River, Okotoks, Rocky View County) ✔. Carry a stable ID through status
  changes, merge dissolved municipalities back into the ones that absorbed
  them, and publish a CMA-based variant alongside.
  - The two regions behave differently. In Edmonton, the EMRB and the CMA
    carry almost the same fiscal weight. In Calgary, the CMA leaves out
    Foothills County, Okotoks and High River, so the board-vs-CMA gap is large.
  - ✘ The report missed a detail: **the CMRB's original membership was
    larger**, including Wheatland County and Strathmore
    ([Western Wheel](https://www.westernwheel.ca/local-news/calgary-region-planning-board-votes-to-cease-operations-10202384)).
    "Fixed = 2025 membership" is a choice that has to be stated, not the
    board's historical footprint.
  - Both boards are gone: the EMRB on 2025-04-01 and the CMRB on 2025-04-30.
    Calgary's successor is a voluntary "Regional Table".
- **Transfers (9).** Use FIR lines **1912** (provincial operating) and
  **1922** (provincial capital) ✔. These are in the 2024 FIR Manual, p. 11;
  whether the line codes drift across 2003–2025 is unverified.
  - Show 5-year rolling averages per capita, with break markers at 2014 (BMTG
    merged into MSI), 2021–23 (MSI stretched) and 2024 (LGFF).
  - Show grantor allocations as a separate panel labelled "formula intent".
  - Key caveat: **Edmonton and Calgary receive no MSI/LGFF operating grants by
    design**, and have their own charter-city LGFF formula, so part of the
    core-vs-ring transfer gap is legislated.
  - Conditional vs unconditional is not a split the FIR makes; it would have
    to be rebuilt program by program.
  - The Police Funding Model is a cost to municipalities, not a transfer, and
    falls on the ring's rural municipalities.
- **Normalization (10).** The headline measure is **equalized non-residential
  assessment excluding linear and M&E**, with linear and M&E stacked
  separately.
  - Edmonton levies no M&E tax, and linear and M&E move with provincial policy
    (shallow gas 2019–23, new-well exemption 2022–24, the 2025 modifier
    change, the 2026 MRRIA regulation). The UDI/EMRB State of Growth report
    also excludes them.
  - Population comes from StatCan census counts, interpolated between census
    years. The Municipal Affairs Population List (gap 2020–22) is used only
    where the chart needs what grant formulas saw.

**A first data test this makes possible:** for 2022, rebuild the UPE01548 figure
from the open equalized-assessment files, using the 13 EMRB members and
excluding linear and M&E. Landing near 60% would pin the method both reports
left unstated, and it would also be the pipeline's first acceptance check.

**Still unverified (per the report):**
- LAB Order 14000 and O.C. 538/81 against primary documents (Wikipedia only)
- **The 1995 RPC dissolution date.** No primary source was found, and one weak
  source implies the commission was still operating in 1997–98.
- CMA member lists (Wikipedia; confirm against StatCan)
- CR_3019's method
- The FIR-vs-allocation reconciliation gap

**Boundaries.**
- 2019 onward: AltaLIS municipal boundary snapshots (OGL-Alberta; archived
  years 2014, 2015, 2017–19 at the U of Lethbridge).
- 1982 and earlier: build polygons from the Alberta Township System legal
  descriptions in the Board Orders rather than tracing PDF maps. StatCan's
  historical CSD files (1981 onward) serve as an independent check.
- No official crosswalk exists between Alberta municipal codes and CSD codes.
  Build one by name plus polygon overlay.

## Spike (2026-09-26): the equalized-assessment PDFs reproduce the City's share

A throwaway parse of the provincial equalized assessment reports (open.alberta.ca
publication `2368-657x`), computing Edmonton's share across the 13 EMRB members.
Code was scratch only; nothing was committed.

- **Availability.** One PDF per report year, 2009–2026. **2009 and 2010 are image-only**
  (no text layer). 2011 onward extract cleanly with `pypdf`.
- **Columns.** Residential, farmland, non-residential (non-regulated), linear, railway
  (≤ 2019 only), co-generating M&E, M&E, and grand total. Every parsed row's classes sum
  exactly to its grand total.
- **Results** (by report year; the mapping to assessment year is not yet confirmed):

  | Report | NR only | NR + linear (+ railway) | All NR incl. M&E |
  |---|---|---|---|
  | 2011 | 76.2% | 71.1% | 60.4% |
  | 2017 | 69.1% | 65.0% | 55.3% |
  | 2022 | 64.5% | 60.5% | 48.9% |
  | 2023 | 63.3% | 59.6% | 48.2% |
  | 2026 | 60.9% | 57.5% | 45.1% |

- **Reading.** The City's UPE01548 "72% (2008) → 60% (2022)" fits **NR + linear,
  excluding M&E**. The 2016 "76%" fits **NR only**. The two published series are
  probably different class definitions, not a contradiction. This is an inference from
  the fit: the City's method is still unpublished.
- **Tension with decision 10.** Our headline (NR excluding linear and M&E) is *not* the
  City's basis. The pipeline must publish both, and the chart must say which one it
  shows.
- **Parser gap.** 2012–2016 dropped Beaumont and Devon: the text layout differs. The
  no-silent-drop guard is what caught it.

## Decisions that are Peter's

1. **Which track leads.** B is unblocked and province-wide; A is the richer
   story and licence-gated. They are not exclusive — B can carry A's citywide
   aggregates as two more rows.
2. **Municipality set** for Track B (capital region only, or all Alberta cities
   above some population?).
3. **Output form** — a chart/table surface (which neither repo has), a map, or
   a static report.
4. **Whether Edmonton's own numbers come from `edmonton-tax-viz`'s outputs or
   are recomputed here from the same provincial source as every peer.** The
   second is the only like-for-like basis; the first reuses verified work.
5. **Shared code with the Edmonton repo.** Nothing is shared yet, by the 3+
   call-sites rule: when Track B starts, copy `fetch_fir_*.py` in and let it
   diverge; extract a library only if a third consumer appears.
6. **DECIDED 2026-09-26: the timeline is the main scope** (`DECISIONS.md`). Was: *fiscal comparison or core-vs-ring timeline narrative?* The
   2026-09-26 brief (above) makes the annexation history the spine. That brings
   a map app, Calgary and a voting overlay, each a scope expansion.
7. **DECIDED 2026-09-26: yes, as a split-screen snapshot comparison of the two regions; a Calgary timeline is optional later.** Was: *is Calgary in scope?* It is the brief's headline peer; this repo's scope
   says capital-region first.
8. **What counts as the "Edmonton region"?** *(DECIDED 2026-09-26, see `DECISIONS.md`. fixed 13 EMRB / 8 CMRB membership; see the §"Research reply" above.)* StatCan CMA (2021), the former
   13-member EMRB (frozen since 2025-04-01), or a custom list. This replaces
   decision 2 if the timeline framing leads.
9. **Transfers basis** *(DECIDED 2026-09-26, see `DECISIONS.md`. FIR codes 1912 and 1922, 5-year average per capita, break markers.)* (only if transfers are in scope): FIR transfer lines as
   the reproducible spine and LGFF/MSI PDFs as a cross-check. Conditional vs
   unconditional and capital vs operating: split or combined?
10. **Normalization:** *(DECIDED 2026-09-26, see `DECISIONS.md`. equalized non-residential excluding linear and M&E, with those two stacked separately; StatCan population.)* per capita vs per assessment dollar, and how to handle
    linear and M&E assessment in industrial counties (Strathcona, Sturgeon,
    Parkland, Leduc).
11. **DECIDED 2026-09-26: deferred to a later phase (a historical voting map is a candidate).** Was: *voting overlay in or out?* It carries the ecological-inference risk.
    The brief's own threshold: if more than 15–20% of the precinct→census join
    is areally ambiguous, drop the causal claims.
