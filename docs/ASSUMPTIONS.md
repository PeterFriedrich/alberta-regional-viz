# Assumptions log

An index of the premises a published number rests on that no guard proves.
Use it to come back to an assumption, and check it before scoping an audit.
**The evidence lives in the doc each row points to.** A row holds no figures
of its own, so it can't drift from that doc. Only the rough size is kept here,
and only for ranking.

Rules:
- **Add a row when a number starts depending on something unproven.** That
  includes a "looks like" or "probably" inference written in `data/DATA.md`.
- **Update a row in place when its status changes.** A row a test now proves
  becomes `VERIFIED`, with the test ID.
- **Keep the pointer live.** When the evidence moves, move the pointer too.

Status values:
- `SUPPORTED`: the evidence agrees, but doesn't cover every year or member the
  row applies to.
- `UNVERIFIED`: taken on trust.
- `ACCEPTED`: known to be off by a measured amount, and used anyway by decision.
- `VERIFIED`: a guard proves it.

| ID | Assumption | Status | If wrong (rough size) | Evidence and test |
|----|------------|--------|-----------------------|-------------------|
| A1 | `taxation_year = report_year − 1` | SUPPORTED | Every point shifts one year | `data/DATA.md` §"Parsed (2026-10-02)" (FIR vs PDF bullet); `docs/AUDIT_LEDGER.md` 2026-09-28 #3 row; test: TODO "second external anchor" |
| A2 | Equalized assessment has one basis across 1998–2026 (the 1997–1999 reports are printed "capped") | UNVERIFIED | Unmeasured; matters only if capping hit core and ring unevenly | `docs/FINDINGS_quick_audits_2026-09-28.md` §#4; test: `docs/AUDIT_LEDGER.md` "Never audited" #2 |
| A3 | The PDFs are the original equalized assessment; FIR `EA` is a later, revised extract | SUPPORTED (2025 only) | A4's estimate fails with it | `data/DATA.md` §"Parsed (2026-10-02)"; test: `/home/opc/research/alberta-regional-viz/fir_pdf_gap_2026-10-17/join.py` on the next updated year |
| A4 | FIR is close enough to fill report years 2008–2010 | ACCEPTED (Peter, 2026-10-17; not built) | About 0.1–0.3 pp; up to about 1 pp in a downturn year | `data/DATA.md` §"Parsed (2026-10-02)"; `TODO.md` "Fill report years 2008–2010"; test: text-layer 2008–2010 reports (`docs/DATA_ISSUES.md`) |
| A5 | Railway inside NR in 1998–2004 moves the share by ≤0.1 pp | UNVERIFIED for those years | The `nr` headline steps at 2005 | `docs/DECISIONS.md` 2026-09-28 railway row; test: FIR line 08290 for 1998–2004 |
| A6 | FIR 2001's NR column includes railway | SUPPORTED | 2001 FIR-vs-PDF comparisons are off by the railway amount | `data/DATA.md` §"Parsed (2026-10-02)" |
| A7 | Spruce Grove's negative 2015 conditional transfers are a reversal | UNVERIFIED | The `basis_note` text only | `data/DATA.md` §"Transfers per capita"; test: Spruce Grove's 2015 audited statements |
| A8 | Edmonton FCSS before 2007 is on a different basis | SUPPORTED | Six real years dropped | `docs/FINDINGS_spending_jumps_2026-10-10.md`; test: the City's 2005–2007 annual reports |
| A9 | Calgary's 2025 FCSS/housing move is another reclassification | UNVERIFIED (2025) | None while the series is unbuilt | `docs/FINDINGS_spending_jumps_2026-10-10.md`; `docs/DECISIONS.md` 2026-10-10 row |
| A10 | Nominal dollars are acceptable for core-vs-ring comparisons within a year | ACCEPTED (Peter, 2026-10-02) | Growth across years is overstated | `docs/SPEC_phase1.md` (Dollars); `TODO.md` "Inflation adjustment" |
| A11 | The brief's history and fiscal figures | UNVERIFIED (one already found wrong) | Phase 3 captions | `TODO.md` "Phase 3 gate" |
