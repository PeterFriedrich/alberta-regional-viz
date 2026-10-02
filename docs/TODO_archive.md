# TODO — archive of CLOSED items

Closed work moved out of `TODO.md` so the file that is read at the start of **every** session carries only live work. **Nothing here is a to-do.**

`TODO.md`'s `## Done` section keeps a one-line entry for each of these, so the *never redo a closed item without asking* rule still works by grepping there; this file holds the reasoning behind each one.

Items are verbatim as they were closed, newest-moved first in the order they appeared in `TODO.md`. Line numbers and "next up" markers inside them are historical — do not act on them.

---

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
