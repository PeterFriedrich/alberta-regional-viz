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

- [ ] **Phase 1 build (`docs/SPEC_phase1.md`).** In data-flow order:
  `data/regions.csv` (13 EMRB + 8 CMRB, with report-name aliases) →
  `src/fetch_equalized.py` → `src/parse_equalized.py` →
  `src/build_share_series.py`, each with synthetic-fixture tests. First
  resolve the report-year → assessment-year mapping (spec acceptance 3): the
  UPE01548 reproduction test cannot pin a year without it. The spike found the
  City's 72→60% fits NR + linear, excluding M&E (`docs/SCOPE_candidates.md`
  §"Spike"). `CONTRIBUTING.md` puts `docs/ARCHITECTURE.md` between spec and code;
  for three modules the spec's module section may be enough. Decide before
  writing code.

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

- [ ] **Phase 2 — FIR fetch.** Per decision 5: copy `fetch_fir_tax_base.py` +
  `fetch_fir_debt.py`'s `MUNICIPALITIES` idiom from the Edmonton repo, extend
  to the chosen municipality set and the equalized-assessment workbooks.
  Manual, reviewed input (not a scheduled refresh) until there is a reason.

- [ ] **Merge gate deps.** `requirements-ci.txt` is pytest-only. Add
  `openpyxl`/`pandas` etc. only when a test needs them; keep it offline.

## Done

Closed items moved out of `## Open work` live in **`docs/TODO_archive.md`** — one line each below, reasoning there.

- [x] **PETER'S CALL — scope.** — DECIDED 2026-09-26 · `docs/TODO_archive.md`
- [x] **Write `docs/SPEC_phase1.md`** — 2026-09-26 · `docs/TODO_archive.md`
