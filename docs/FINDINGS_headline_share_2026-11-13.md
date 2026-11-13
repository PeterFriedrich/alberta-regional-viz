# Findings: does the headline core share measure "base moving to the ring"?

Run 2026-11-13 (S14) from `docs/AUDIT_headline_share.md`, ledger "Never
audited" #1. A decision audit, top-down. Remedies are proposed, not built.

## Criteria fixed before the decomposition

Committed before any per-member number was computed. At this point the run had
seen only the region-level shares in `core_ring_share.csv`.

The headline `nr` share is **misleading as "base moving to the ring"** if any
of these holds:

- **A (Edmonton, Heartland).** The three EMRB members inside Alberta's
  Industrial Heartland (Strathcona County, Sturgeon County, Fort
  Saskatchewan) account for half or more of the fall in Edmonton's core `nr`
  share, taxation 1997 → 2025.
- **B (Edmonton, without them).** With those three removed from the region,
  the core share falls by less than a third of the headline fall.
- **C (Calgary, shrinking core).** Calgary's core `nr` value is lower in 2025
  than in 2015, and holding the ring at its 2015 value still reproduces half
  or more of the 2015 → 2025 fall in share. The share would then be measuring
  a devaluation of the core, not growth in the ring.

If none holds, L0 is SOUND or CONDITIONAL, depending on what the per-member
split shows.
