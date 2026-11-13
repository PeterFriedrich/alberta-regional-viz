# Audit brief: does the headline core share measure what the argument claims?

An instrument, not findings: read cold, run, write the output to
`docs/FINDINGS_headline_share_<date>.md`, add a row to `docs/AUDIT_LEDGER.md`.
Ledger "Never audited" #1. Written 2026-11-13 (S14) for a fresh session.

## The claim under audit

`core_ring_share.csv`, basis `nr` (decision 10, fixed 2025 membership,
decision 8): Edmonton's core share falls from 0.770 (taxation 1997) to 0.609
(2025); Calgary's from 0.949 to 0.829, most of it after 2015 (0.927 → 0.829).
The project's backbone (DECISIONS 2026-09-30) reads this as the regional tax
base splitting between core and ring. Re-read the numbers from the committed
file before quoting them; these are as of `4282e70`.

## Grounding order

1. `docs/DECISIONS.md`: the bodies, untruncated, of the 2026-09-26 rows
   (decisions 6, 8, 10), 2026-09-28 railway, 2026-10-02 corrections,
   2026-10-19 FIR fill and UPE01548.
2. `docs/SPEC_phase1.md` §"The backbone" and the basis table; `docs/ASSUMPTIONS.md`
   (A1–A5 are known; don't re-report them).
3. `data/regions.csv`; `data/processed/member_assessment.csv` (gitignored;
   rebuild per the latest handoff's restoration block). Summarize it with
   pandas, never `Read` it.

## Decision stack (evaluate top-down; an UNSOUND level moots those below)

- **L0. Is a core share of equalized NR the right quantity for "base moving
  to the ring"?** A share falls when the ring grows faster, whatever the
  reason. The sharpest counter: Strathcona and Sturgeon hold the Industrial
  Heartland, heavy industry Edmonton never had land or zoning for. If their
  growth is most of the decline, the chart shows industrial geography, not
  a shift of base. Decide what result would make the share misleading
  *before* decomposing.
- **L1. Decomposition.** Split the change in core share 1997 → 2025 (and
  sub-periods: 1997–2007, 2007–2015, 2015–2025) into member contributions
  from `member_assessment.csv`, class `nr` (with `nr_incl_railway` for
  1998–2004 per the railway row). Report each ring member's pp contribution,
  and the core's own growth rate vs the ring's. Rank by numerator (memory
  `audit-categories-by-members-not-names`).
- **L2. Composition inside NR.** Is NR in the leading members industrial or
  commercial? The equalized reports don't split it; look for what can
  (FIR assessment schedules, municipal annual reports). If no source splits
  it, say so and size what the answer would change.
- **L3. Calgary since 2015.** Same decomposition. Candidates to test, not
  assume: Rocky View industrial/logistics growth, the 2015–2017 downtown
  office-value collapse shrinking the core (a fall in the numerator's
  complement, not a gain in the ring), Airdrie/Chestermere growth.
- **L4. Fixed membership (decision 8).** Does the 2025 membership applied to
  1997 change the story, e.g. members that were rural then? Size only;
  the decision is locked, so a finding here is a caption, not a reopen.

## Verdicts

Per level: SOUND / CONDITIONAL / UNSOUND, the sharpest counter-argument, and
what evidence would change it. The run ends with a recommendation Peter can
take: keep the headline as is, keep it with a stated caveat (draft the
wording), or add a companion series (e.g. core vs ring excluding the
Heartland members), proposed, not built.

## Out of scope

Reopening decisions 8 or 10; the A2 capping question (its own brief,
`docs/AUDIT_equalization_basis.md`); the per-capita series.

## Required closing section

`What this run got wrong`, non-empty (`.claude/skills/project-audit/SKILL.md`
Step 4).
