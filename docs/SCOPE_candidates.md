# Scope candidates — what this project could be built on, and what blocks each

Written 2026-09-18 when the project was split out of `edmonton-tax-viz`. Nothing
here is decided; the decisions at the bottom are Peter's. Both tracks were
verified against live sources in that repo (dates given); **re-fetch before
building on any figure here.**

## Track A — per-parcel peers via ArcGIS REST (capital region)

Source of truth: `docs/SPIKE_regional_lens.md` (2026-07-17). Two peers, and
they are not symmetric:

| | St. Albert | Strathcona County |
|---|---|---|
| Geometry | parcel **polygons** | **points** (every vintage) |
| Value | assessed value **and actual levy** per parcel | assessed value only |
| Classes | full multi-class roll | residential-improved only; no class field |
| History | 2025 + 2026 only | annual 2012–2026 (2016 absent) |
| Licence | **UNRESOLVED — likely not open data** (a lookup tool's backend, not a catalogued dataset) | clean: OGL-Alberta, catalogued |
| Known defect | — | whole-building value repeated on every unit record; truth ≈ $21–22 B vs naive $116.8 B |

What it supports: a citywide value-per-acre / levy-per-acre comparison on the
**lot-acre** basis (Strathcona cannot do ground acres). St. Albert alone could
support a full parallel per-parcel pipeline — the only peer with polygons +
class + levy — and that is exactly what its licence question gates.

**Blocked on (unchanged since 2026-07-17):**
1. St. Albert licensing — ask the City whether the LandScape service is
   reusable like its catalogued portal datasets. Until answered: **no raw
   per-parcel use, never committed anywhere.** Fallback: citywide aggregates
   via `outStatistics` (no bulk download) or published tax-rate-bylaw totals.
2. Strathcona dedup rule — a build-time task, independent of licensing.
3. Valuation-lag convention across the three municipalities — unchecked.

## Track B — province-wide aggregates via Alberta Municipal Affairs (OGL-Alberta)

Source of truth: `edmonton-tax-viz/docs/SPEC_industrial.md` §"Track B"
(2026-07-18; not copied here — the Edmonton repo owns that spec). The FIR
workbooks cover **every Alberta municipality, 2003–2025** (older zips to 1994),
one file per year; `2026_Tax_Rates.xlsx` carries every municipality's rates in
one file; the **equalized assessment report** (XLSX, 2024–2026) is the valid
instrument for cross-municipality *level* comparison — raw FIR values are not
revaluation-adjusted, so raw-FIR levels across municipalities are invalid and
only within-year shares are usable with care.

The fetch idiom exists in the Edmonton repo (`scripts/fetch_fir_debt.py`,
`scripts/fetch_fir_tax_base.py`: manual, reviewed input; anchor cross-checks;
a `MUNICIPALITIES` stable-code dict). Candidate municipalities named there:
Edmonton, Strathcona County, Sturgeon County, Parkland County, City of Leduc,
Leduc County — but the source is province-wide, so the set is a choice.

What it supports: multi-year series per municipality of taxable assessment by
class, levy, mill rates, non-residential share. No licence question, no
per-parcel data, no geometry beyond a municipal-boundary layer (provincially
published; licence to verify).

Known open analytical question: two published series for Edmonton's regional
non-residential assessment share (76% → 72% over 15 years; 72% in 2008-09 →
60% in 2022) do not reconcile — rebuild from primary data before citing either.

**Blocked on:** nothing in the data. The blocker is the output decision — all
Track B outputs are charts/tables, not maps.

## Decisions that are Peter's

1. **Which track leads.** B is unblocked and province-wide; A is the richer
   story and licence-gated. They are not exclusive — B can carry A's citywide
   aggregates as two more rows.
2. **Municipality set** for Track B (capital region only, or all Alberta cities
   above some population?).
3. **Output form** — a chart/table surface (which neither repo has), a map, or
   a static report.
4. **Whether Edmonton's own numbers come from `edmonton-tax-viz`'s outputs or
   are recomputed here from the same provincial source as every peer.** The
   second is the only like-for-like basis; the first reuses verified work.
5. **Shared code with the Edmonton repo.** Nothing is shared yet, by the 3+
   call-sites rule: when Track B starts, copy `fetch_fir_*.py` in and let it
   diverge; extract a library only if a third consumer appears.
