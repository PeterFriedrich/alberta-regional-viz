# TODO

The source of truth for what's left. Read first every session; update in place.

**Format contract** (`tools/todo_archive.py` depends on it): top-level items are
`- [ ]` / `- [x]` lines directly under `## Open work`; `###` sub-headings may
group them; closed items are moved to `docs/TODO_archive.md` by the tool, which
leaves a one-line stub under `## Done`. An open item can be stale — reproduce the
symptom and re-measure the stated cause before acting on it.

## Open work

- [ ] **PETER'S CALL — scope.** The eleven decisions in `docs/SCOPE_candidates.md`
  §"Decisions that are Peter's": 1–5 as of 2026-09-18 (which track leads;
  municipality set; output form; Edmonton's own numbers reused or recomputed;
  no shared code yet), plus 6–11 from the 2026-09-26 timeline brief (framing;
  Calgary; region definition; transfers basis; normalization; voting overlay).
  Decision 6 sets the scope of the rest. Gates everything below. Done when
  `docs/DECISIONS.md` carries a row per decision.

- [ ] **Write `docs/SPEC_phase1.md`** once scope is decided (`CONTRIBUTING.md`:
  spec before code). Inputs/outputs, acceptance criteria, the comparability
  caveats that every output must carry (municipal-only vs total bill; raw vs
  equalized; lot-acre vs ground-acre).

- [ ] **Re-verify every live figure in `docs/SPIKE_regional_lens.md` and
  `docs/SCOPE_candidates.md` before building on it.** Both are dated 2026-07;
  the St. Albert service names embed the year and will have rolled; Strathcona
  publishes a new snapshot yearly. Record retrieval dates in `data/DATA.md`.

- [ ] **If the timeline framing leads: verify the brief's history from primary
  sources before any of it reaches an output.** The research reports cite by
  name, with no URLs. Checked 2026-09-26 against Wikipedia only: 1979 LAB bid,
  Order 14000, O.C. 538/81, 331.1 → 700.6 km², Nisku retained. Found wrong: the
  Leduc annexation is 2019 / 8,260 ha, not 2017 / ~9,500 ha. Still unchecked:
  the 1981 10-year tax-base-loss reimbursement, the 1995 RPC dissolution,
  Petigara's 72→60%, the CSKA $397/capita, and the Police Funding Model
  figures. Primary sources: the Board Orders (open.alberta.ca has MGB 050/18)
  and the Orders in Council.

- [ ] **Track A gate — St. Albert licensing.** Ask the City whether the
  LandScape ArcGIS service is reusable like its catalogued `data.stalbert.ca`
  datasets or intended for single lookups only. Log the ask and the answer in
  `docs/DATA_ISSUES.md` (status column — "the draft exists" is not sent).
  Until answered: no per-parcel use, never committed.

- [ ] **Track A — Strathcona multi-unit dedup rule.** Whole-building value is
  repeated per unit on some complexes and not others; naive sum $116.8 B,
  strict dedup $21.3 B (slightly under). A build-time data task, independent
  of licensing — and a `DATA_ISSUES.md` row whether or not Track A proceeds.

- [ ] **Track B — first fetch.** If B leads: copy `fetch_fir_tax_base.py` +
  `fetch_fir_debt.py`'s `MUNICIPALITIES` idiom from the Edmonton repo, extend
  to the chosen municipality set and the equalized-assessment workbooks.
  Manual, reviewed input (not a scheduled refresh) until there is a reason.

- [ ] **Merge gate deps.** `requirements-ci.txt` is pytest-only. Add
  `openpyxl`/`pandas` etc. only when a test needs them; keep it offline.

## Done
