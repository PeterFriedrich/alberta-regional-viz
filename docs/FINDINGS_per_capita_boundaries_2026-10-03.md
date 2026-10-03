# Findings: audit Q1, do per-capita numerators and denominators cover the same people? (2026-10-03, S9)

The instrument is in `docs/AUDIT_LEDGER.md` §"Q1". Every per-capita value in
`transfers_per_capita.csv` and `spending_per_capita.csv` divides FIR dollars by
StatCan 17-10-0155 population.
- **The dollars** are on the boundaries of their own year.
- **The population** is back-cast to 2021 boundaries for every year (decision
  2026-10-02, `docs/SPEC_phase1.md` §"Population basis").

Figures are from the processed files as of `d7f45aa`. The sources and scripts
are in `/home/opc/research/alberta-regional-viz/q1_boundary_audit_2026-10-03/`.

## Verdict

**FAIL against the brief's bar (member-year ≤ 1%, core/ring ≤ 0.5%).** Nothing
is charted yet, so no published number is wrong. Under this decision the
committed member rows and Calgary's police ring are wrong by more than the bar.

| Level | Verdict | Worst case |
|---|---|---|
| Edmonton core, ring and police ring | PASS | ring +0.21% (2001), decaying to 0 by 2019 |
| Calgary core | PASS | −0.08% (2001–05) |
| Calgary ring, all members | WARN | +0.75% in 2001, above 0.5% through 2004, 0 from 2009 |
| **Calgary police ring** | **FAIL** | **−2.6% in 2001**, still −0.7% in 2011 |
| **Member rows** | **FAIL** | **58 of 525 member-years beyond 1%**, worst 8.2% |

The sign is the error in the published per-capita value: `+` means it is
overstated.

## Decision stack

**L1: "Population on 2021 boundaries in every year" is CONDITIONAL.**
- **Sound for:** the core/ring headline in Edmonton, and in Calgary from 2005.
- **Unsound for:**
  - member rows of seven members before their last annexation;
  - Calgary's police ring before 2012;
  - Calgary's ring as a whole in 2001–04.
- **The sharpest argument against the decision isn't any single annexation.** It's
  the way annexations combine with the police exclusion:
  - Airdrie, Chestermere, Cochrane, Okotoks and High River annexed about 1,560
    people from Rocky View and Foothills.
  - Rocky View and Foothills are left out of police (`POLICE_EXCLUDED`).
  - On 2021 boundaries, those people sit in the police ring's denominator in
    years when they were RCMP-policed rural residents.
  - The ring's all-member total doesn't see this, because the moves stay inside
    the ring.
- **Evidence that would change the verdict:** a remedy that moves each year's
  population onto that year's boundaries (below).

**L2: The measurement is PASS.** The event table reconciles three ways:
1. Census adjusted counts, for all four windows (2001–06, 06–11, 11–16 and
   16–21). Every member's adjusted-minus-original count equals the sum of its
   92F0009X events, except where a row is a boundary correction (next
   section).
2. 17-10-0142 (2016 boundaries) against 17-10-0155, in 2011. For every member
   the gap equals the net 2016–21 events within 7 people. The exceptions are
   Edmonton (+73) and Calgary (+52), which have no event in that window, so
   their gaps are estimate revisions.
3. Edmonton +542 for 2019 reproduces `docs/SPEC_phase1.md`.

**L3: The code is not audited.** It is moot until the remedy is decided.

## Every annexation 2001–2025 that moved people and involves a member

These come from StatCan 92F0009X, the Interim List of Changes to Municipal
Boundaries.
- **People** is the census count of the transferred area at the census before
  the change.
- **Effective** is the legal date.
- 17-10-0155 is a July 1 estimate, so an annexation counts from the first year
  whose July 1 falls on or after its effective date.

| Effective | Gainer ← loser | People |
|---|---|---|
| 2002-01-01 | (Irricana) ← Rocky View | 5 |
| 2002-07-01 | High River ← Foothills | 38 |
| 2003-07-01 | Airdrie ← Rocky View | 25 |
| 2004-01-01 | Okotoks ← Foothills | 25 |
| 2004-07-01 | Cochrane ← Rocky View | 243 |
| 2005-01-01 | **Calgary ← Rocky View** | 38 |
| 2005-01-01 | **Calgary ← Foothills** | 99 |
| 2005-01-01 | (Crossfield) ← Rocky View | 10 |
| 2006-01-01 | Stony Plain ← Parkland | 35 |
| 2006-01-01 | Devon ← Leduc County | 5 |
| 2007-01-01 | **Calgary ← Rocky View** | 619 |
| 2007-01-01 | St. Albert ← Sturgeon | 45 |
| 2007-01-01 | Spruce Grove ← Parkland | 45 |
| 2007-03-31 | (Redwater) ← Sturgeon | 10 |
| 2008-05-01 | Okotoks ← Foothills | 5 |
| 2009-01-01 | Chestermere ← Rocky View | 359 |
| 2010-01-01 | (Crossfield) ← Rocky View | 20 |
| 2011-12-31 | Airdrie ← Rocky View | 707 |
| 2012-01-01 | High River ← Foothills | 10 |
| 2014-01-01 | Leduc ← Leduc County | 25 |
| 2015-01-01 | Devon ← Leduc County | 5 |
| 2017-01-01 | Beaumont ← Leduc County | 61 |
| 2017-07-01 | Okotoks ← Foothills | 135 |
| 2019-01-01 | **Edmonton ← Leduc County** | 542 |
| 2020-01-01 | Fort Saskatchewan ← Strathcona | 20 |
| 2020-01-01 | (Black Diamond) ← Foothills | 5 |
| 2021-01-01 | High River ← Foothills | 10 |
| 2021-01-01 | Spruce Grove ← Parkland | 42 |
| 2022-01-01 | St. Albert ← Sturgeon | 100 |

- **Names in parentheses are not members.** Those moves change a region's total
  population, not the split between core and ring.
- **About 20 more member annexations moved 0 people** and change nothing here.
  They include Edmonton ← Sturgeon (2019), St. Albert ← Edmonton (2002) and
  Fort Saskatchewan ↔ Strathcona (2002, 2022).
- **Not annexations:**
  - **Chestermere +442 (2001-01-02) is code 8, a boundary correction**: StatCan's
    2001 map was wrong, not the legal boundary. So 17-10-0155 is already right
    for those people. Municipal Affairs' own count supports this: it put
    Chestermere at 3,742 in 2001 (FIR POPL), above the census's 3,414.
  - The code 10/11 population revisions (Airdrie ↔ Rocky View 4 in 2003;
    Leduc County → Thorsby 17 in 2011) are corrections too.
  - Wabamun (2021) and New Sarepta (2010) are dissolutions, already
    consistent: their FIR rows are summed into the member (decision 8).
- **The direction flips after 2021.** St. Albert's 2022 annexation is missing
  from St. Albert in 2022–25 and still counted in Sturgeon.

## Where it bites (`member_year_error.csv` in the research folder)

| Member | Years beyond 1% | Worst year: published pop vs that year's boundaries | Per capita |
|---|---|---|---|
| Chestermere | 2001–08 | 2001: 4,388 vs 4,029 | understated 8.2% |
| Rocky View | 2001–11 | 2001: 29,128 vs 31,154 | overstated 7.0% |
| Leduc County | 2001–18 (18 years) | 2001: 12,567 vs 13,205 | overstated 5.1% |
| Airdrie | 2001–11 | 2001: 21,657 vs 20,925 | understated 3.4% |
| Cochrane | 2001–03 | 2001: 12,344 vs 12,101 | understated 2.0% |
| Foothills | 2001–04 | 2001: 16,864 vs 17,191 | overstated 1.9% |
| Okotoks | 2001–03 | 2001: 12,179 vs 12,014 | understated 1.4% |

- **It's a level bias, not a visible step.** Leduc County police per capita in
  2018 is published at 99.80 against 96.08 on 2018 boundaries. The 2019 drop
  that the annexation should produce is buried in year-to-year swings: small
  members' transfers move 40–80% a year. So no chart would show it, but every
  multi-year average and every member-vs-member comparison carries it.
- **Edmonton and Calgary themselves are never off by more than 0.08%.**

## Remedy, sized

**Peter chose A on 2026-10-03, and it is built:** `population_asof` in
`population.csv`, from `data/annexations.csv`. See the DECISIONS row of that date.

The choice is Peter's, because it changes the `population.csv` contract. My
recommendation is A.

- **A. Move each year's population onto that year's boundaries (recommended).**
  - Commit the 29-row event table above as data. Then derive a
    `population_asof` column: 17-10-0155, with each event's people moved back
    to the loser for the years before it took effect (and forward after 2021).
    Both builds then divide by it.
  - It touches 277 of 525 member-years, mostly by under 1%.
  - Guards:
    - every event nets to zero across gainer and loser;
    - the census adjusted counts, and the 0142-vs-0155 gaps in 2011, reproduce
      within 10 people (pinned numbers, since the raw tables are gitignored);
    - Edmonton 2018 differs by exactly 542.
  - Residual error: the area's population is held at its pre-change census count
    in every earlier year. The 0142 check bounds that at 7 people in 2011.
  - Cost: the spec once rejected census scaling as "a series StatCan does not
    publish, built to imitate one it does". This differs: each adjustment is
    StatCan's own count of the people a legal change moved, and the result
    matches what the numerator covers.
- **B. Keep 2021 boundaries. Every chart names the members it biases, and the
  member charts drop the 58 member-years beyond 1%.** It's cheap, but it loses
  2001–08 for Chestermere, 2001–11 for Rocky View and Airdrie, and 2001–18 for
  Leduc County. The Calgary police ring stays 0.7–2.6% low for 2001–11 unless it
  gets its own note.
- **C. Keep the data as it is and add a caveat only.** That fails the bar the
  audit set.

**Dependency:** the open 1997–2000 population item. The 2001 census adjusted six
members' 1996 counts: Beaumont, Leduc, Leduc County, Parkland, Foothills and
Okotoks. Okotoks went from 8,528 to 11,664 in five years, part of it annexation.
Any back-extension inherits the same choice. Sizing it needs the 1996 original
counts and the pre-2001 change lists, which this run did not fetch.

## What this run got wrong

- **I first read 0142-vs-0155 gaps in non-census years as boundary moves.**
  Calgary showed +667 in 2001 with no annexation in 2016–21; Edmonton +1,096
  against an event worth 542. Both are revisions between the two estimate
  vintages. Only the census year (2011) is clean, so the 0142 check uses 2011
  alone. It's the audit's own class: two series that differ in more than the
  one thing being measured.
- **The census chain alone would have counted Chestermere's 442 as an
  annexation.** That puts Chestermere 2001 at about 18% instead of 8.2%. The
  adjusted counts mix legal annexations with StatCan's map corrections, and
  only the 92F0009X change codes separate them. The census windows reconcile to
  the change list *including* corrections, so the reconciliation can't catch
  this; it had to be read off the codes.
- **The queued brief had two dates wrong.** It said Beaumont ← Leduc County was
  2019; it was 2017-01-01. It also said Airdrie ← Rocky View was 2012; legally it
  was 2011-12-31, though FIR 2012 is still the first full year. The brief's
  ranking pointed at Calgary ← Rocky View first. The largest core/ring effect is
  the police-exclusion interaction, which the brief never mentioned.
- **I nearly reported a false parse defect.** My first POPL lookup keyed rows by
  `muni_id` alone, which made Leduc County's population look like 359–530 for
  1999–2009. That was New Sarepta's row overwriting it: absorbed villages are
  filed under their member's `muni_id` with their own `fir_code`. `fir_long.csv`
  is right.
- **Not checked:**
  - changes effective during 2025 (StatCan's next list is due in 2026);
  - the dates in the 2001–06 PDF, which I read from extracted text, not the
    page images;
  - the code-8 reading of Chestermere's 442. It rests on the change code and
    Municipal Affairs' 3,742, not on an annexation order. If it was really a
    late-recorded annexation, Chestermere 2001 is about 18% off, not 8.2%.
