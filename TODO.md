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

- [ ] **Next session: pick an audit** from `docs/AUDIT_LEDGER.md` §"Never audited
  (candidates, roughly ranked)" (13 candidates listed 2026-09-28, top-down). Run it
  with the `project-audit` skill and add a ledger row.

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

- [ ] **Phase 2 — FIR fetch.** Per decision 5: copy `fetch_fir_tax_base.py` +
  `fetch_fir_debt.py`'s `MUNICIPALITIES` idiom from the Edmonton repo, extend
  to the chosen municipality set and the equalized-assessment workbooks.
  Manual, reviewed input (not a scheduled refresh) until there is a reason.

- [ ] **Merge gate deps.** `requirements-ci.txt` is pytest-only. Add
  `openpyxl`/`pandas` etc. only when a test needs them; keep it offline.

## Done

Closed items moved out of `## Open work` live in **`docs/TODO_archive.md`** — one line each below, reasoning there.

- [x] **Phase 1b — the 1998–2007 reports** — DONE 2026-09-28 · `docs/TODO_archive.md`

- [x] **The reproduction test never runs on the merge gate.** — DONE 2026-09-27 · `docs/TODO_archive.md`

- [x] **Phase 1 build (`docs/SPEC_phase1.md`).** — DONE 2026-09-27 · `docs/TODO_archive.md`

- [x] **PETER'S CALL — scope.** — DECIDED 2026-09-26 · `docs/TODO_archive.md`
- [x] **Write `docs/SPEC_phase1.md`** — 2026-09-26 · `docs/TODO_archive.md`
