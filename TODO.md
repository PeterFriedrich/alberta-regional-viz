# TODO

The source of truth for what's left. Read first every session; update in place.

**Format contract** (`tools/todo_archive.py` depends on it): top-level items are
`- [ ]` / `- [x]` lines directly under `## Open work`; `###` sub-headings may
group them; closed items are moved to `docs/TODO_archive.md` by the tool, which
leaves a one-line stub under `## Done`. An open item can be stale — reproduce the
symptom and re-measure the stated cause before acting on it.

## Open work

- [ ] **Re-verify every live figure in `docs/SPIKE_regional_lens.md` and
  `docs/SCOPE_candidates.md` before building on it.** Both are dated 2026-07;
  the St. Albert service names embed the year and will have rolled; Strathcona
  publishes a new snapshot yearly. Record retrieval dates in `data/DATA.md`.

- [ ] **Phase 3 gate: verify the brief's history from primary sources before any
  of it reaches an output.** The research reports cite by
  name, with no URLs. Checked 2026-09-26 against Wikipedia only: 1979 LAB bid,
  Order 14000, O.C. 538/81, 331.1 → 700.6 km², Nisku retained. Found wrong: the
  Leduc annexation is 2019 / 8,260 ha, not 2017 / ~9,500 ha. 72→60% is now
  sourced (UPE01548, 13 EMRB members). Still unchecked: LAB 14000 and O.C.
  538/81 in primary documents, the 1981 10-year tax-base-loss reimbursement,
  the **1995 RPC dissolution** (no primary source; one source conflicts), the
  CSKA $397/capita, and the Police Funding Model figures. Primary sources: the
  Board Orders (open.alberta.ca has MGB 050/18) and the Orders in Council.
  **Fiscal figures from the same reports, also unchecked** (carried over from the
  retired claude.ai spec, 2026-10-01). Check any of these before a chart or
  caption quotes it: the police municipal cost share (one report: 10% → 30% from
  2020, effectively 19% on 2018 costs, reset to 22% for 2026-27; another: "rose to
  30% in 2024"); the LGFF opening envelope ($722M vs $724.2M) and the 2026
  ($800M) / 2027 ($895.3M) envelopes; Calgary's $1.05B downloaded costs and
  $145M 2027 gap (EC2026-0284); the Paquette ledger (about $718M, mostly not
  reconciling to FCS02218; only the 32% non-resident road-use share corroborated).

- [ ] **Next session: pick an audit** from `docs/AUDIT_LEDGER.md` §"Never audited".
  Candidates #3, #4, #6 and #7 ran on 2026-09-28 (`docs/FINDINGS_quick_audits_2026-09-28.md`).
  #2 now has a concrete lead: the pre-2000 reports are "capped".

- [ ] **Find a second external anchor at another year** for the share series. The
  UPE01548 test passes for any of taxation years 2021–2024, so it doesn't pin
  `taxation_year = report_year − 1`.

- [ ] **Send the `docs/DATA_ISSUES.md` rows to Municipal Affairs**: the 2026
  subtotal typo, and a request for text-layer versions of the 2008–2010 reports
  (which would close the gap holding the City's 2008 anchor). Mention the 1999
  subtotal rounding and the 2006 row totals (rows added 2026-09-28) in the same
  message; they aren't worth a message of their own. Status stays NOT SENT until
  one is actually sent.

- [ ] **Caption the NR+linear rise across the 2007–2009 gap.** Edmonton's `nr_linear`
  share is 67.2% for taxation year 2006 and 71.1% for 2010, while `nr` barely moves
  (75.3% → 76.2%). Market NR more than doubled in those years, while regulated linear
  grew about 25%, and linear is a larger share of the ring's base. It is a
  composition effect, not a data break, but a chart spanning the gap reads as a jump.
  This belongs to the Phase 4 chart text.

- [ ] **Track A gate — St. Albert licensing.** *(Track A is not in the plan, per
  decision 1 on 2026-09-26: the ask is still worth sending, but nothing waits on it.)* Ask the City whether the
  LandScape ArcGIS service is reusable like its catalogued `data.stalbert.ca`
  datasets or intended for single lookups only. Log the ask and the answer in
  `docs/DATA_ISSUES.md` (status column — "the draft exists" is not sent).
  Until answered: no per-parcel use, never committed.

- [ ] **Track A — Strathcona multi-unit dedup rule.** Whole-building value is
  repeated per unit on some complexes and not others; naive sum $116.8 B,
  strict dedup $21.3 B (slightly under). A build-time data task, independent
  of licensing — and a `DATA_ISSUES.md` row whether or not Track A proceeds.

- [ ] **Phase 2 — FIR parse** (the fetch and the schema pin are done,
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

- [ ] **Phase 2b — FIR spending by function, core vs ring, per capita** (decision
  2026-09-30; `docs/SPEC_phase1.md` §"The backbone"). Police, Public Transit,
  Family and Community Support + Public Housing Operations, from the Phase 2
  fetch. Needs its own short spec first: gross vs net of own revenue, and the
  per-year line-code dictionary (only the 2024 workbook has been checked;
  every year's code rows are now in `data/fir_schema.json`, so derive it from there).

- [ ] **CSD crosswalk before Phase 2 population.** `data/regions.csv` has no
  StatCan CSD key and no official Alberta-code ↔ CSD concordance exists
  (`docs/SCOPE_candidates.md`). Hand-build it, one CSD code per `muni_id`, and
  flag dissolved/renamed members explicitly.

- [ ] **Phase 4 architecture pass: propose "no runtime third-party dependency"**
  as a DECISIONS row — every file the browser needs is static in the repo (no
  third-party APIs or tile CDNs), guarded by a test that scans built pages for
  external URLs. Include the attribution line (OGL-Alberta, StatCan Open
  Licence, and OSM if any OSM-derived layer is used). From the retired claude.ai spec.

- [ ] **Merge gate deps.** `requirements-ci.txt` is pytest-only. Add
  `openpyxl`/`pandas` etc. only when a test needs them; keep it offline.

## Done

Closed items moved out of `## Open work` live in **`docs/TODO_archive.md`** — one line each below, reasoning there.

- [x] **Decision 9 needs re-deciding: FIR lines 1912/1922 exist only from 2023.** — DECIDED 2026-10-01 · `docs/TODO_archive.md`

- [x] **Strip the SYNC TEST marker before or with the next real commit.** — 2026-09-30 · `docs/TODO_archive.md`

- [x] **Proposed: a build-time continuity warning** — DONE 2026-09-29 · `docs/TODO_archive.md`

- [x] **Phase 1b — the 1998–2007 reports** — DONE 2026-09-28 · `docs/TODO_archive.md`

- [x] **The reproduction test never runs on the merge gate.** — DONE 2026-09-27 · `docs/TODO_archive.md`

- [x] **Phase 1 build (`docs/SPEC_phase1.md`).** — DONE 2026-09-27 · `docs/TODO_archive.md`

- [x] **PETER'S CALL — scope.** — DECIDED 2026-09-26 · `docs/TODO_archive.md`
- [x] **Write `docs/SPEC_phase1.md`** — 2026-09-26 · `docs/TODO_archive.md`
