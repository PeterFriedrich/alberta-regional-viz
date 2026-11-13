# Findings: does the headline core share measure "base moving to the ring"?

Run 2026-11-13 (S14) from `docs/AUDIT_headline_share.md`, ledger "Never
audited" #1. A decision audit, top-down. Remedies are proposed, not built.

## Criteria fixed before the decomposition

Committed before any per-member number was computed. At this point the run had
seen only the region-level shares in `core_ring_share.csv`.

The headline `nr` share is **misleading as "base moving to the ring"** if any
of these holds:

- **A (Edmonton, Heartland).** The three EMRB members inside Alberta's
  Industrial Heartland (Strathcona County, Sturgeon County, Fort
  Saskatchewan) account for half or more of the fall in Edmonton's core `nr`
  share, taxation 1997 → 2025.
- **B (Edmonton, without them).** With those three removed from the region,
  the core share falls by less than a third of the headline fall.
- **C (Calgary, shrinking core).** Calgary's core `nr` value is lower in 2025
  than in 2015, and holding the ring at its 2015 value still reproduces half
  or more of the 2015 → 2025 fall in share. The share would then be measuring
  a devaluation of the core, not growth in the ring.

If none holds, L0 is SOUND or CONDITIONAL, depending on what the per-member
split shows.

## Basis of every number below

Equalized assessment, basis `nr` unless a line says otherwise, nominal
dollars, taxation years (`report_year − 1`), fixed 2025 board membership
(13 EMRB, 8 CMRB). Rebuilt from `member_assessment.csv`; the rebuild
reproduces every published `core_share` on all three bases before any split
is trusted. Taxation 2007–2009 are FIR-filled (A4), so the 2007 sub-period
boundary rests on FIR. A member's contribution is the change in its share of
the regional total; contributions sum to the fall in the core share.

Scripts and their inputs: `/home/opc/research/alberta-regional-viz/headline_share_2026-11-13/`
(`decompose.py`, `permits.py`, `membership.py`).

## Verdicts

| Level | Verdict | One line |
|---|---|---|
| L0 share as "base moving to the ring" | **CONDITIONAL** | True as "the core's share of assessed NR fell". Not shown as "base moved": 61% (Edmonton) and 81% (Calgary) of the fall happened 2015–2025, while each core's NR assessment fell in nominal dollars. |
| L1 decomposition | **SOUND** | The Heartland is not the story on `nr`. Leduc County, Strathcona, Parkland and Leduc City are 94% of Edmonton's fall. |
| L2 composition inside NR | **CONDITIONAL** | No source in the repo splits equalized NR. Permit values say ring growth is industrial and core building is commercial. |
| L3 Calgary since 2015 | **CONDITIONAL** | Rocky View is 75% of the fall; the core lost $11.3B of NR assessment over the same years. Criterion C fails as written. |
| L4 fixed membership | **SOUND** | Adding the former members moves the 28-year fall by 0.17 pp (Edmonton) and 0.04 pp (Calgary). The CMA variant decision 8 promises was never built. |

## The pre-registered criteria

| | Result | Holds? |
|---|---|---|
| A | The three Heartland members account for 3.30 of 16.12 pp, 20.5% | No |
| B | Without them the core share falls 87.09 → 71.53, 15.56 pp, 96.5% of the headline fall | No |
| C | Calgary core 73.14B (2015) → 61.85B (2025): lower. Ring held at its 2015 value: 92.66 → 91.44, 1.22 of 9.72 pp, 12.6% | No (first half only) |

None holds, so by the rule fixed in advance L0 is SOUND or CONDITIONAL. It is
CONDITIONAL for a reason the criteria did not anticipate; see L0.

## L0. Is the share the right quantity? CONDITIONAL

The brief's counter-argument (Heartland growth) fails on `nr`. A second one
holds.

**When the fall happened.**

| | 1997→2007 | 2007→2015 | 2015→2025 | 1997→2025 |
|---|---|---|---|---|
| Edmonton fall, pp | 3.02 | 3.20 | 9.90 | 16.12 |
| core × / ring × | 2.36 / 2.77 | 2.40 / 2.81 | **0.94** / 1.46 | 5.29 / 11.39 |
| Calgary fall, pp | 0.19 | 2.07 | 9.72 | 11.97 |
| core × / ring × | 3.63 / 3.78 | 1.95 / 2.77 | **0.85** / 2.20 | 5.98 / 22.99 |

Through 2015 both sides grew fast and the ring grew somewhat faster. After
2015 the core's assessed NR went down in both regions at once:

- Edmonton core: 41.41B (2015), low of 36.22B (2022), 38.81B (2025).
- Calgary core: 73.14B (2015), low of 53.30B (2022), 61.85B (2025).
- Alberta CPI rose 28.8% over 2015–2025 (StatCan 18-10-0005-01). In constant
  dollars the cores are ×0.73 and ×0.66, the rings ×1.13 and ×1.70.

**Who "caused" the 2015–2025 fall depends on the benchmark** (the second and
third rows were computed after seeing the result):

| Benchmark for "no change" | Edmonton: core / ring | Calgary: core / ring |
|---|---|---|
| Nominal value held (criterion C's test) | 14% / 86% | 13% / 87% |
| Nominal, averaged over both orders | 15% / 85% | 18% / 82% |
| Value held in constant dollars (log-odds) | 72% / 28% | 44% / 56% |

So the share alone cannot say whether the ring gained base or the core lost
value. Under the first reading the ring did it; under the third the core's
real decline is most of Edmonton's fall and nearly half of Calgary's.

**New construction does not account for it.** FIR Schedule ST reports the
estimated value of commercial and industrial building permits per municipality
(self-reported, construction cost only). Adding each side's permits to its
base-year `nr` assessment gives a quantity-only share:

| | Actual fall | Quantity-only fall | Core: base + permits → actual | Ring: base + permits → actual |
|---|---|---|---|---|
| Edmonton, 2017→2025 | 7.09 pp | 4.01 pp; 0.06 pp without one outlier | 40.41B + 10.21B → 38.81B | 19.04B + 9.48B (4.88B) → 24.94B |
| Calgary, 2018→2025 | 7.23 pp | 2.12 pp | 64.16B + 8.74B → 61.85B | 6.99B + 2.90B → 12.72B |

The Edmonton core received about $10B of permitted commercial and industrial
construction and its assessment went down. The outlier is Sturgeon County's
2019 industrial permit value of $4.6B, unexplained here; industrial permits
include machinery and equipment that `nr` excludes, so counting it at all
overstates the quantity-only fall. Weaknesses of this test are under "What
this run got wrong".

**A common outside cause fits.** Calgary's downtown office assessments were
about $24B in 2015 and were projected at about $12B for 2019, and the City
reported the resulting shift of tax onto other non-residential property
(sources below). Edmonton's core was flat in nominal dollars from 2015 to
2020 (41.41B → 40.55B) and fell in 2021–2022 (to 36.22B). This run did not
source Edmonton's fall.

- **Sharpest counter-argument.** A share is what tax-base competition is
  about: when core office value falls, the levy shifts to the rest of the
  core's base whatever the cause, and the core's share of the region's NR is
  a fact. As a statement of where assessed value sits, the series is right.
- **What the share does not support.** "Businesses moved to the ring" or
  "the ring took Edmonton's base". Most of the fall is a decade in which
  existing core property was revalued downward while ring industrial
  property was revalued upward.
- **Evidence that would change the verdict to SOUND.** A quantity series
  (floor area, parcel counts, or assessment growth split into new
  construction and revaluation, which assessors report to the province)
  showing the ring's new construction share rising in step with the value
  share.
- **To UNSOUND.** The same series showing a flat construction share.

## L1. Decomposition. SOUND

**Edmonton, 1997 → 2025** (core 77.01% → 60.88%, fall 16.12 pp):

| Member | 1997 $M | 2025 $M | × | Contribution, pp | % of fall |
|---|---|---|---|---|---|
| Leduc County | 286 | 5,239 | 18.3 | +5.22 | 32.4 |
| Strathcona County | 523 | 6,248 | 11.9 | +4.31 | 26.7 |
| Parkland County | 197 | 3,109 | 15.8 | +2.81 | 17.4 |
| Leduc (city) | 111 | 2,512 | 22.6 | +2.78 | 17.2 |
| Spruce Grove | 109 | 1,307 | 11.9 | +0.90 | 5.6 |
| St. Albert | 259 | 2,114 | 8.1 | +0.59 | 3.7 |
| Sturgeon County | 224 | 1,847 | 8.3 | +0.55 | 3.4 |
| Stony Plain | 47 | 557 | 11.7 | +0.37 | 2.3 |
| Beaumont | 11 | 299 | 26.6 | +0.35 | 2.2 |
| Morinville | 23 | 193 | 8.5 | +0.06 | 0.4 |
| Devon | 43 | 119 | 2.8 | −0.26 | −1.6 |
| Fort Saskatchewan | 356 | 1,392 | 3.9 | −1.56 | −9.6 |
| Edmonton (core) | 7,334 | 38,813 | 5.3 | −16.12 | |

The fall is the south and west (Leduc County, Leduc, Parkland: 67%) plus
Strathcona. Fort Saskatchewan grew more slowly than the core. Sturgeon's
share of the region fell until 2015 (2.35% → 1.61%) and rose after.

**Why the Heartland guess failed: decision 10 already removed it.** On
`nr_all` (linear and M&E included) Edmonton's 1997 → 2025 fall is 11.19 pp
(56.32% → 45.14%), Strathcona is 66.5% of it and Sturgeon 35.3%. Heartland
value is mostly machinery, equipment and linear property, which the `nr`
headline excludes. The Heartland caveat belongs on any `nr_all` chart, not on
the headline.

**Edmonton, 2015 → 2025** (fall 9.90 pp): Parkland +1.93, Leduc County +1.83,
Strathcona +1.58, Sturgeon +1.29, Leduc +1.02, St. Albert +0.75, Spruce Grove
+0.55, Fort Saskatchewan +0.33. Every ring member but Devon gains share,
which is what a fall in the denominator's largest term produces.

**Calgary, 1997 → 2025** (core 94.92% → 82.95%, fall 11.97 pp): Rocky View
+8.90 (74.3%; 131M → 7,532M, ×57), Airdrie +1.71 (14.3%), Okotoks +0.83,
Cochrane +0.37, Chestermere +0.32, Foothills +0.10, High River −0.25.

- **Sharpest counter-argument.** The split is exact arithmetic on a share,
  so it inherits L0's problem: a member "contributes" when it holds value
  while the core loses it.
- **Evidence that would change it.** A defect in a leading member's series.
  Rocky View 2023–2024 match FIR `EA` line 08275; 2025 matches the province's
  dashboard (+19.1% to $7.5B). Both are the province's own figure, so they
  confirm the parse, not the assessment.

## L2. Composition inside NR. CONDITIONAL

No source in the repo splits equalized NR into industrial and commercial.
`fir_long.csv` holds the `EA` subtotals only. FIR's tax-rate schedule has
small-business and designated-industrial columns; this run did not open it.

The nearest evidence is the permit values (FIR Schedule ST, 2017–2025
pooled, commercial + industrial, self-reported):

| | Commercial: core share | Industrial: core share |
|---|---|---|
| Edmonton region | 81.3% (8.73B of 10.74B) | 15.3% (1.48B of 9.68B; 29% without the Sturgeon 2019 value) |
| Calgary region | 86.9% (7.74B of 8.91B) | 31.0% (1.01B of 3.25B; Rocky View alone 2.10B) |

New commercial building stays about as concentrated in the core as the stock
is. New industrial building goes mostly to the ring. On commercial permits
alone the Edmonton core share would have risen 2017–2025.

- **What the answer would change.** Nothing in criteria A or B: a member's
  NR is counted whole. It changes the reading: if ring NR is industrial and
  logistics and core NR is office and retail, the post-2015 share tracks the
  relative price of two property types as much as a choice of location.
- **Sharpest counter-argument.** Permit values are construction cost,
  include equipment outside `nr`, and have reporting defects (below).
- **Evidence that would change it.** The cities' own assessment rolls by
  class (both publish them) and the counties' assessment reports, for 2015
  and 2025.

## L3. Calgary since 2015. CONDITIONAL

Core share 92.66% → 82.95%, fall 9.72 pp. Rocky View +7.27 pp (74.8%;
2,238M → 7,532M, ×3.37), Airdrie +1.04, Okotoks +0.41, Foothills +0.37,
Cochrane +0.35, Chestermere +0.21.

| Taxation year | 2015 | 2017 | 2019 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| Calgary core, $B | 73.14 | 67.34 | 56.74 | 53.30 | 56.08 | 58.71 | 61.85 |
| Ring, $B | 5.79 | 6.62 | 7.32 | 8.06 | 9.55 | 11.27 | 12.72 |
| of which Rocky View, $B | 2.24 | | 3.30 | 3.90 | 5.08 | 6.32 | 7.53 |

Both candidates are real, in sequence. To 2022 the share fell 5.8 pp while
the core lost $19.8B, in step with the documented downtown office collapse.
From 2022 to 2025 it fell 3.9 pp more while the core recovered $8.5B and
Rocky View nearly doubled (3.90B → 7.53B). Airdrie and Chestermere are
minor.

- **Sharpest counter-argument.** Criterion C says the ring did it (87%
  under the nominal test). But that test is the one most favourable to the
  ring reading; in constant dollars the core's decline is 44%.
- **Evidence that would change it.** What Rocky View's 2023–2025 growth is:
  new buildings entering the roll (the county reports large warehouse
  development at Balzac) or revaluation. Its own assessment reports would say.

## L4. Fixed membership. SOUND (size only)

Adding the municipalities that left the boards (ten from the Capital Region
Board, two from the CMRB) to the ring for every year:

| | Level shift, pp | Fall 1997→2025: fixed / with former members |
|---|---|---|
| Edmonton | −0.33 to −0.61 | 16.12 / 15.95 |
| Calgary | −0.85 to −1.23 | 11.97 / 12.01 |

A caption-level difference in level, none in trend.

**Found: the CMA variant was never built.** Decision 8 says "a StatCan CMA
variant is published alongside". `docs/SPEC_phase1.md` moves it to Phase 2.
Phase 2 is built without it, `core_ring_share.csv` has no such region, and
`TODO.md` does not track it. The table above is close to what it would show.

Not measured: annexations that moved ring land into the core (Edmonton from
Leduc County, 2019; Calgary from Rocky View, 2007). They raise the core
share, so they work against the fall, not for it.

- **Sharpest counter-argument.** The former-member list for Edmonton is
  inferred, not sourced (below).
- **Evidence that would change it.** A member whose 1997 base sat outside
  the 2025 list and was large. None of the twelve is.

## Recommendation

**Keep the headline, with a caveat, and add one companion view.** Proposed,
not built; Peter's call.

1. **Caveat on every chart of the share** (draft):
   > Share of assessed value, not of buildings or businesses. It falls when
   > ring property gains value faster than core property, through new
   > construction or through revaluation. Most of the fall came after 2015,
   > when the core's non-residential assessment fell in dollar terms in both
   > cities (Edmonton −6%, Calgary −15%, 2015–2025) while the ring's rose.
2. **Companion view: the two levels.** Core and ring `nr` value indexed to a
   base year, on one chart per region, with the CPI line or in constant
   dollars once the deflator is chosen (`TODO.md` "Inflation adjustment",
   A10). It shows which side moved, which the share hides.
3. **Per-member contribution chart**, replacing the Heartland guess with the
   measured split (Leduc County, Strathcona, Parkland, Leduc; Rocky View).
4. **Do not build "excluding the Heartland members".** It moves the fall by
   3.5% on `nr`.
5. **Any `nr_all` chart carries the Heartland caveat**: on that basis
   Strathcona and Sturgeon are the whole fall.
6. **Follow-ups**, none blocking:
   - a quantity series to settle L0 (new construction vs revaluation);
   - Edmonton's 2015–2022 core decline against a City source;
   - Rocky View 2023–2025 against the county's assessment reports;
   - the CMA variant: build it or amend decision 8;
   - `docs/DATA_ISSUES.md` rows for the FIR permit defects, if the permit
     series is ever used in an output.

## Sources

Retrieved 2026-11-13 unless noted.

- Industrial Heartland membership (Fort Saskatchewan, Lamont County,
  Strathcona County, Sturgeon County; Edmonton joined 2010):
  https://en.wikipedia.org/wiki/Alberta%27s_Industrial_Heartland ;
  https://www.strathcona.ca/business-and-development/development/albertas-industrial-heartland/ ;
  https://www.edmonton.ca/city_government/city_organization/albertas-industrial-heartland-association
- Calgary downtown office assessments and the tax shift:
  https://www.calgary.ca/PDA/Assessment/Documents/pdf/Projected_Tax_Shift_Non-residential_Properties.pdf ;
  https://www.calgary.ca/content/dam/www/ca/city-manager/documents/tax-share-communications---the-present-f.pdf ;
  https://globalnews.ca/news/4816164/calgary-commercial-office-property-value-oil-gas
  (the $24B and $12B figures are from search-result summaries of these; the
  CBC article that states them returned HTTP 403)
- Board membership, 24 → 13 in 2017:
  https://en.wikipedia.org/wiki/Edmonton_Metropolitan_Region_Board
- Rocky View: https://regionaldashboard.alberta.ca/region/rocky-view-county/property-assessments ;
  https://renx.ca/rocky-view-county-calgary-explosive-growth-industrial-retail
- Alberta CPI, all items: StatCan table 18-10-0005-01,
  https://www150.statcan.gc.ca/n1/tbl/csv/18100005-eng.zip
- Permit values: FIR Schedule ST, `data/raw/fir/fir_year_2017.xlsx` to
  `fir_year_2025.xlsx`, sheet `ST(1)-Stat`.

## What this run got wrong

1. **Criterion C tested the wrong benchmark, and it favoured the claim under
   audit.** Holding the ring at its nominal 2015 value treats all nominal
   growth as "the ring gaining". Under that test the ring explains 87%; in
   constant dollars, 56%. The constant-dollar test was written after the
   result was known, so neither number is a clean pre-registered verdict.
2. **Criterion C was written for Calgary only.** Edmonton's core also fell
   in nominal terms after 2015. The criteria were fixed having seen only
   region-level shares, not levels; looking at levels first would have
   caught it.
3. **The brief's L0 counter-argument was aimed at the wrong basis.** The
   brief (written by the same session) proposed the Heartland as the
   sharpest objection to an `nr` series that decision 10 had already
   stripped of most Heartland value. Reading decision 10's body against
   what the Heartland's assessment consists of would have shown that
   before two criteria were spent on it.
4. **The permit test is weak evidence presented next to strong arithmetic.**
   - Edmonton's 2017 and Calgary's 2017–2018 permit values are about $1–2M,
     a unit or reporting error; the base years were chosen to avoid them,
     after seeing them.
   - Zeros that are probably blanks: Beaumont 2024–2025, Chestermere 2025,
     Foothills 2022–2023, Okotoks 2017.
   - One value (Sturgeon 2019, $4.6B industrial) moves the Edmonton
     quantity-only fall from 0.06 to 4.01 pp. It was not traced.
   - Construction cost is not assessed value: no land, no demolitions, and
     assessment lags permits by a year or more.
5. **"Common cause" for Edmonton is an inference.** Only Calgary's office
   collapse is sourced, and partly from search summaries. Edmonton's core
   decline is measured but unexplained.
6. **The core's nominal fall is smaller on the FIR vintage.** FIR `EA` has
   the Edmonton core at 39.37B for taxation 2015 against the PDF's 41.41B
   (the known 2016 gap), and 38.85B for 2024 against 39.03B: about −1%
   over 2015–2024, not −6%. Still well below inflation. The caveat's "−6%"
   is the PDF series.
7. **The former Capital Region Board list was written from memory.** Lamont
   County and the Town of Lamont are sourced; the other eight names are an
   inference from population, and one source counts 25 original members.
   Every name was found in every year of the data, so the sizing ran, but
   on a list that may be a member short.
8. **Rocky View's 2022–2025 rise is confirmed only against the province's
   own figures.** Whether it is new property or revaluation is open, and
   the 2022–2025 phase it drives is 40% of Calgary's post-2015 fall.
9. **L2 stopped at the nearest source.** FIR's tax-rate schedule and the
   cities' assessment rolls by class were not opened.
