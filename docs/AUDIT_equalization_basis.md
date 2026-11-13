# Audit brief: is equalized assessment on one basis across 1997–2025?

An instrument, not findings: read cold, run, write the output to
`docs/FINDINGS_equalization_basis_<date>.md`, add a row to
`docs/AUDIT_LEDGER.md`, and update `docs/ASSUMPTIONS.md` A2's status.
Ledger "Never audited" #2. Written 2026-11-13 (S14) for a fresh session.
Run after `docs/AUDIT_headline_share.md`, unless that one is blocked.

## The premise under audit

A2 (UNVERIFIED): the series joins two report layouts (the 1998–2004 reports'
class set and the later one), the FIR-filled report years 2008–2010 (A4, accepted), and 28 years of
equalization practice, and the shares treat it as one basis. The lead
(`docs/FINDINGS_quick_audits_2026-09-28.md` §#4, `data/DATA.md` "Capped"
bullet): the 2000 report marks the 1997–1999 totals "capped" and 2000
"uncapped" (+18.25% provincially), and its preface says "the 2000 equalized
assessment is not capped". The 1998 and 1999 prefaces don't describe the cap.

## Grounding order

1. `docs/ASSUMPTIONS.md` A1–A5 (A4 and A5 are separate; don't re-report).
2. The prefaces of `data/raw/equalized/equalized_1998.pdf` to `_2003.pdf`
   (gitignored; `src/fetch_equalized.py` refetches). Extract text with
   `pdfplumber` (the parser's library); read pages as images only if text fails.
3. `docs/SPEC_phase1.md` §"Phase 1b" for the two class-set families.

## Questions, in order

1. **What was the cap?** Find the rule: which classes, what limit, applied
   to what (a province-wide total, or per municipality). Primary sources:
   the report prefaces, the Municipal Government Act / equalized assessment
   regulation of the time, Municipal Affairs bulletins or the Minister's
   Guidelines. Record each source's URL and retrieval date.
2. **Did it hit core and ring unevenly?** A uniform cap leaves shares alone.
   Measure: each member's growth from report 1999 → 2000 against the
   provincial +18.25%, and the core share's step at that boundary vs its
   year-to-year spread (size against the distribution; memory
   `size-remedies-against-the-distribution`). If FIR 1997–1999 has an
   uncapped figure, compare.
3. **Any other method change inside 1997–2025?** Scan every preface for
   method wording (linear, M&E, regulated property, base year, market value
   standard). Separately list provincial-total steps beyond the normal range
   and check each against a stated cause. The class-set switch after the
   2004 report is known; check only that no rule change hides inside it.
4. **Verdict and remedy, sized.** PASS (one basis, or a uniform change),
   WARN (uneven but under the year-to-year noise; caption), FAIL (uneven
   and material; propose starting the headline at taxation 1999, or a
   marked break). Propose; Peter decides.

## Required closing section

`What this run got wrong`, non-empty (`.claude/skills/project-audit/SKILL.md`
Step 4).
