# TODO — archive of CLOSED items

Closed work moved out of `TODO.md` so the file that is read at the start of **every** session carries only live work. **Nothing here is a to-do.**

`TODO.md`'s `## Done` section keeps a one-line entry for each of these, so the *never redo a closed item without asking* rule still works by grepping there; this file holds the reasoning behind each one.

Items are verbatim as they were closed, newest-moved first in the order they appeared in `TODO.md`. Line numbers and "next up" markers inside them are historical — do not act on them.

---

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
