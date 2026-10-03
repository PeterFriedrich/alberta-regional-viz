# TODO — archive of CLOSED items

Closed work moved out of `TODO.md` so the file that is read at the start of **every** session carries only live work. **Nothing here is a to-do.**

`TODO.md`'s `## Done` section keeps a one-line entry for each of these, so the *never redo a closed item without asking* rule still works by grepping there; this file holds the reasoning behind each one.

Items are verbatim as they were closed, newest-moved first in the order they appeared in `TODO.md`. Line numbers and "next up" markers inside them are historical — do not act on them.

---

- [x] **PETER'S CALL — per-capita population on each year's boundaries?** — DECIDED A and BUILT 2026-10-03: `population_asof`, `data/annexations.csv`, DECISIONS row. (audit Q1, 2026-10-03,
  `docs/FINDINGS_per_capita_boundaries_2026-10-03.md` §"Remedy, sized"). On 2021 boundaries:
  - 58 of 525 member-years are off by more than 1%. Worst: Chestermere −8.2%, Rocky View
    +7.0%, and Leduc County +5.1% for 2001–18.
  - Calgary's police ring is −2.6% in 2001 and −0.7% in 2011, because about 1,560 people
    annexed out of the police-excluded counties already sit in the ring's denominator.
  - Edmonton's core and ring are within 0.21%.

  Options:
  - **A (recommended):** commit the 29-row annexation table (StatCan 92F0009X) and derive
    `population_asof` for both builds. This changes the `population.csv` contract, so
    propose it first.
  - **B:** keep 2021 boundaries, drop the 58 member-years from member charts, and note
    the bias on charts.

  Don't build either without a yes. The choice also governs the 1997–2000 item below.

- [x] **Next session: run audit Q1** — DONE 2026-10-03 (S9). It FAILs the brief's bar:
  `docs/FINDINGS_per_capita_boundaries_2026-10-03.md`; the remedy is the next item.
  (`docs/AUDIT_LEDGER.md` §"Queued"): whether the per-capita
  numerators (FIR, each year's own boundaries) and denominators (StatCan, back-cast to 2021
  boundaries) cover the same people, across every annexation 2001–2025 involving a member.
  Queued 2026-10-03.


- [x] **Where do rural counties record Police Funding Model payments?** Parkland, Rocky View
  and Sturgeon report $0 police in every year 2017–2023, including after the model started
  in 2020, and no protective-services line shows a matching step. Ask Municipal Affairs, or
  check a county's audited statements. Also check the single-year zeros: Cochrane 2022,
  Devon 2021.
  **Done 2026-10-03 (S8):** the Police Funding Model is a provincial requisition on the tax
  bill, not a municipal expense (Parkland County). Cochrane 2022 booked police under bylaw;
  Devon 2021 booked all protective services as "other". Exclusions unchanged
  (`data/DATA.md` §"Spending per capita").


- [x] **Phase 2b module (proposal first: a new module).** Spec locked 2026-10-02
  (`docs/SPEC_phase1.md` §"Phase 2b basis"). Parse Schedule C (Operating ≤2008; accrual
  2009+), Schedule E amortization (2009+) and Schedule E sales and user charges for the
  four functions, absorbed villages included. Build gross and net-of-user-charges per
  capita for members and core/ring. Tests: an independent recompute, and no common step at 2009.
  **Done 2026-10-02 (S8):** `parse_fir` schedules C_OP/C/E_AMORT/E_UC, `src/build_spending.py`
  → `spending_per_capita.csv`. The 2009 step is measured on the cities' restated 2008
  (≤3% for police, transit and FCSS), and housing starts in 2009 (DECISIONS 2026-10-02).


- [x] **Phase 2 transfers: include the four absorbed villages' FIR rows** Done 2026-10-02: `absorbed_fir_codes` in `regions.csv`; `src/build_transfers.py`. (Blackie,
  Entwistle, New Sarepta, Wabamun) in their members' totals, as Phase 1 now does.
  `fir_long.csv` holds member codes only; look up the villages' FIR codes in
  `data/fir_schema.json`.


- [x] **Population module (proposal first: a new module).** Built 2026-10-02: `src/fetch_population.py`, `tests/test_population.py`. Fetch StatCan table 17-10-0155
  (decision 2026-10-02; `docs/SPEC_phase1.md` §"Population basis"), keep the 21 members
  through `data/csd_crosswalk.csv` (2021 rows), and write a per-member, per-year population
  file that records the release date. Its test should pin the table ID, the 2001 start, and
  one member per region against values checked by hand. That test replaces the decision row's
  `[unverifiable]`.


- [x] **Phase 1 omits four dissolved villages that decision 8 merges into members.**
  Fixed 2026-10-02: `+part` aliases in `regions.csv`, with `member_values` able to sum several
  parts per member per year. Guarded by `test_every_vanished_municipality_is_classified`.
  Edmonton `nr` −0.22 pp (1998) to −0.01 pp (2021).


- [x] **CSD crosswalk before Phase 2 population.** Built as
  `data/csd_crosswalk.csv` (one row per member per census year, plus rows for the
  four absorbed villages), pinned by `tests/test_csd_crosswalk.py`; sources in
  `data/DATA.md`.


- [x] **Apply FIR's values to the four kept-as-printed anomalies** DONE 2026-10-02: six cells in `data/corrections.csv` (DECISIONS row 2026-10-02). (the DECISIONS
  row of 2026-09-28 pre-decides "a flagged correction, with the printed value
  kept alongside"; FIR now supports all four). This changes
  `core_ring_share.csv`, so **propose the mechanism first**: where corrections
  live (a committed corrections table read by `build_share_series.py`?), how
  the printed value is kept, and how `KNOWN_ANOMALIES` /
  `test_suspect_printed_values_are_kept_until_verified` change in the same
  commit. Open question for Peter: replace only the flagged cell, or the whole
  row? Devon 1999 differs in NR, linear and M&E alike.


- [x] **Phase 2 — FIR parse** DONE 2026-10-02: `src/parse_fir.py` → `data/processed/fir_long.csv`; year mapping, full EA cross-check, the four anomalies and the transfers continuity are in `tests/test_parse_fir.py`; findings in `data/DATA.md` §"Parsed (2026-10-02)".
 (the fetch and the schema pin are done,
  2026-10-01: `src/fetch_fir.py`, `src/fingerprint_fir.py`,
  `data/fir_schema.json`). The next module, `src/parse_fir.py`, reads by
  `regions.csv` → `fir_code` and the row's own YEAR, not the folder name.
  **Then verify the four printed anomalies** (DECISIONS row of 2026-09-28):
  Airdrie NR 2016, Sturgeon NR 2000, Devon 1998 and Calgary linear 2002. The
  plan was to check against FIR *taxable* assessment, but `MR(2)` exists only
  from 2023. Use FIR's `EA` schedule instead: the same equalized metric, a
  second publication, covering 1997–2025. A disagreement is evidence of a print
  or parse slip. Agreement means the publisher printed the same number twice,
  which does not show it is right. **Extend the check from the four anomalies to
  every member-year, 1997–2025** (CW reply 2026-10-02): a full FIR-EA vs PDF
  diff is cheap once both are parsed, and it catches parse slips anywhere.
  Settle the year mapping first (does FIR financial year Y carry report year
  Y or Y+1?). A confirmed error gets a flagged correction,
  and the guard test is updated in the same commit. Then check year alignment
  (FIR financial year Y vs equalized taxation year) on non-anomalous years
  before trusting it.
  **Transfers** (decision as amended 2026-10-01): sum 01910+01920 through 2022
  and 01912+01922 from 2023, and add a test that no member's total steps at
  2022→2023 beyond its normal year-to-year variation. The DECISIONS row cites it
  as owed.


- [x] **Decision 9 needs re-deciding: FIR lines 1912/1922 exist only from 2023.**
  DECIDED 2026-10-01: total provincial transfers (DECISIONS row 2026-10-01).
  For 1994–2022 the provincial transfer lines are 01910 *Unconditional* / 01920
  *Conditional*, which is a different cut from operating/capital
  (`data/DATA.md` §"Fetched into this repo";
  `tests/test_fir_schema.py::test_provincial_transfer_codes_change_meaning_in_2023`).
  Options: the conditional/unconditional pair through 2022 with a 2023 break
  marker; total provincial transfers (01910+01920 → 01912+01922) as one series;
  or 2023+ only. Peter's call, and it comes before the transfer parse.


- [x] **Strip the SYNC TEST marker before or with the next real commit.** The last
  bullet of `docs/SCOPE.md` (the "SYNC TEST 2026-09-30" one, padded to about 8 KB
  so the claude.ai Project's file size visibly changes). Delete it, run
  `.venv/bin/python scripts/make_brief.py --write`, and commit `docs/BRIEF.md` with it.
  Then close this item.


- [x] **Proposed: a build-time continuity warning** in `build_share_series.py`. It
  would log any member whose basis value jumps and reverts, or drops to zero.
  `test_reproduces_upe01548` can't see a zeroed small member. The thresholds need
  sizing against the year-on-year distribution first. This is a new behaviour, so it
  needs Peter's OK before it is built.
  **Done 2026-09-29:** built as a failing check with `KNOWN_ANOMALIES` (`check_continuity`; DECISIONS 2026-09-29).


- [x] **Phase 1b — the 1998–2007 reports** — DONE 2026-09-28: the series now covers taxation
  years 1997–2006 and 2010–2025; railway sits inside the old NR (the `nr` basis is flagged);
  2009–2026 output is byte-identical. Spec §"Phase 1b (built 2026-09-28)". (Publication
  `1844032`, text layer.) This extends the series back to taxation year 1997. It is a different layout and class set
  (residential incl. farmland / NR / M&E / linear), so check whether NR includes
  railway there. Spec §"Out of scope".


- [x] **The reproduction test never runs on the merge gate.** — DONE 2026-09-27: `core_ring_share.csv` committed, skip removed. `data/processed/` is
  gitignored, so `test_reproduces_upe01548` skips in CI. Option: commit
  `core_ring_share.csv` (96 rows, derived from OGL-Alberta data) so CI checks it.
  This changes the output contract, so propose it before doing it.


- [x] **Phase 1 build (`docs/SPEC_phase1.md`).** Done 2026-09-27: fetch → parse →
  build for 2011–2026, 21 members found in every year, `test_reproduces_upe01548`
  passes (Edmonton NR+linear 59.6% for taxation year 2022, against the City's 60%).


- [x] **PETER'S CALL — scope.** (All 11 decided 2026-09-26; see `docs/DECISIONS.md`.) The eleven decisions in `docs/SCOPE_candidates.md`
  §"Decisions that are Peter's": 1–5 as of 2026-09-18 (which track leads;
  municipality set; output form; Edmonton's own numbers reused or recomputed;
  no shared code yet), plus 6–11 from the 2026-09-26 timeline brief (framing;
  Calgary; region definition; transfers basis; normalization; voting overlay).
  **6, 7 and 11 were decided 2026-09-26** (timeline is the main scope; Calgary as
  a split-screen snapshot; voting deferred). 8–10 went out for research: the prompt
  is `/home/opc/research/alberta-regional-viz/region_transfers_normalization_prompt.md`;
  **8–10 were decided 2026-09-26** as the reply recommended. Still open: 1–5,
  most of which 6–10 now answer (track: B's FIR/equalized data is the spine; municipality
  set = decision 8; output form = map + timeline + split screen). Confirm those,
  plus 4 (Edmonton recomputed from the provincial source, like every peer?) and 5.
  Gates everything below. Done when
  `docs/DECISIONS.md` carries a row per decision.


- [x] **Write `docs/SPEC_phase1.md`** (written 2026-09-26: the core-vs-ring assessment-share series.) once scope is decided (`CONTRIBUTING.md`:
  spec before code). Inputs/outputs, acceptance criteria, the comparability
  caveats that every output must carry (municipal-only vs total bill; raw vs
  equalized; lot-acre vs ground-acre).
