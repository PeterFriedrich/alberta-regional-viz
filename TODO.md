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

- [ ] **Pick an audit** from `docs/AUDIT_LEDGER.md` §"Never audited".
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

- [ ] **Explain the systematic FIR-vs-PDF gap before using FIR as a source.**
  The same report year matches exactly on 68% of member values, but where the
  two differ FIR is usually 0.1–5% *lower* (402 lower vs 82 higher). Find out
  why (a later revision? a different inclusion rule?) from the
  EA manual or a publisher question. This blocks the next item.

- [ ] **FIR could fill report years 2008–2010** (the scanned-PDF gap, which holds
  Edmonton's 72% anchor year). It is blocked on the item above: a gap-filler
  must be on the same basis as the series around it, or the chart says so.

- [ ] **PETER'S CALL — what to do with the classification-unstable spending series.**
  (`docs/FINDINGS_spending_jumps_2026-10-10.md` §"Options".) Calgary moves amounts between
  its FCSS, housing, economic development, planning and land & housing rentals lines in
  FIR: 2016, 2020, 2022 and probably 2025. Edmonton FCSS before 2007 is probably on another
  basis, and Edmonton housing 2022 includes a $70.0M non-cash transfer to Homeward Trust.
  A: drop Calgary-core FCSS and housing from charts (recommended); B: combine FCSS + housing
  from 2009 with gaps; C: keep and mark.

- [ ] **Inflation adjustment for the transfers timeline.** `transfers_per_capita.csv` is
  in nominal dollars (Peter, 2026-10-02). That doesn't matter for comparing core and ring in
  the same year, but a 25-year line overstates growth. Decide on a deflator (Alberta CPI?)
  at the chart stage.

- [ ] **Population 1997–2000.** 17-10-0155 starts in 2001, so `per_capita_5yr` starts in 2005,
  although FIR transfers go back to 1994. Look for an older StatCan CSD
  estimate series. Otherwise, propose linking the 1996 census count to the 2001 estimate by
  each member's 2001 estimate-to-census ratio. Until then, per-capita series start in 2001.
  **Use each year's own boundaries** (decided 2026-10-03, audit Q1). The 2001 census adjusted six members'
  1996 counts for boundary changes (Beaumont, Leduc, Leduc County, Parkland, Foothills,
  Okotoks), so any back-extension inherits that choice.

- [ ] **Phase 4 architecture pass: propose "no runtime third-party dependency"**
  as a DECISIONS row — every file the browser needs is static in the repo (no
  third-party APIs or tile CDNs), guarded by a test that scans built pages for
  external URLs. Include the attribution line (OGL-Alberta, StatCan Open
  Licence, and OSM if any OSM-derived layer is used). From the retired claude.ai spec.

- [ ] **Merge gate deps.** `requirements-ci.txt` is pytest-only. Add
  `openpyxl`/`pandas` etc. only when a test needs them; keep it offline.

## Done

Closed items moved out of `## Open work` live in **`docs/TODO_archive.md`** — one line each below, reasoning there.

- [x] **Calgary FCSS swings year to year.** — 2026-10-10 · `docs/TODO_archive.md`
- [x] **Unexplained jumps in the spending series** — 2026-10-10 · `docs/TODO_archive.md`

- [x] **PETER'S CALL — per-capita population on each year's boundaries?** — DECIDED 2026-10-03 · `docs/TODO_archive.md`

- [x] **Next session: run audit Q1** — DONE 2026-10-03 · `docs/TODO_archive.md`

- [x] **Where do rural counties record Police Funding Model payments?** — DONE 2026-10-03 · `docs/TODO_archive.md`

- [x] **Phase 2b module (proposal first: a new module).** — LOCKED 2026-10-02 · `docs/TODO_archive.md`

- [x] **Phase 2 transfers: include the four absorbed villages' FIR rows** — DONE 2026-10-02 · `docs/TODO_archive.md`

- [x] **Population module (proposal first: a new module).** — BUILT 2026-10-02 · `docs/TODO_archive.md`

- [x] **Phase 1 omits four dissolved villages that decision 8 merges into members.** — 2026-10-02 · `docs/TODO_archive.md`

- [x] **CSD crosswalk before Phase 2 population.** · `docs/TODO_archive.md`

- [x] **Apply FIR's values to the four kept-as-printed anomalies** — DONE 2026-10-02 · `docs/TODO_archive.md`

- [x] **Phase 2 — FIR parse** — DONE 2026-10-02 · `docs/TODO_archive.md`

- [x] **Decision 9 needs re-deciding: FIR lines 1912/1922 exist only from 2023.** — DECIDED 2026-10-01 · `docs/TODO_archive.md`

- [x] **Strip the SYNC TEST marker before or with the next real commit.** — 2026-09-30 · `docs/TODO_archive.md`

- [x] **Proposed: a build-time continuity warning** — DONE 2026-09-29 · `docs/TODO_archive.md`

- [x] **Phase 1b — the 1998–2007 reports** — DONE 2026-09-28 · `docs/TODO_archive.md`

- [x] **The reproduction test never runs on the merge gate.** — DONE 2026-09-27 · `docs/TODO_archive.md`

- [x] **Phase 1 build (`docs/SPEC_phase1.md`).** — DONE 2026-09-27 · `docs/TODO_archive.md`

- [x] **PETER'S CALL — scope.** — DECIDED 2026-09-26 · `docs/TODO_archive.md`
- [x] **Write `docs/SPEC_phase1.md`** — 2026-09-26 · `docs/TODO_archive.md`
