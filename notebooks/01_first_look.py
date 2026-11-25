# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # First look: core vs ring, Edmonton and Calgary regions
#
# **Internal working notebook — not for publication.** It charts the three committed
# outputs as they stand, so we can see the shapes before any Phase 4 chart text is
# written. Several figures here are still under open TODO items (noted at each chart).
#
# Bases that hold for every chart below:
# - **Region = 2025 board membership applied to all years** (13 EMRB members, 8 CMRB
#   members; decision 8). Core = the city; ring = the other members.
# - **Equalized assessment** for the tax-base split, never raw FIR assessment.
# - **Nominal dollars** for per-capita series (no deflator yet — TODO).
# - **Per-capita population** = StatCan 17-10-0155 July 1 estimates moved onto each
#   year's boundaries (`population_asof`, decision 2026-10-03).
#
# Rebuild: `.venv/bin/jupytext --sync notebooks/01_first_look.py` then
# `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/01_first_look.ipynb`.

# %%
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
PROC = ROOT / "data" / "processed"
share = pd.read_csv(PROC / "core_ring_share.csv")
members = pd.read_csv(PROC / "member_assessment.csv")  # gitignored: rebuild with src/ first
transfers = pd.read_csv(PROC / "transfers_per_capita.csv")
spending = pd.read_csv(PROC / "spending_per_capita.csv")
annex = pd.read_csv(ROOT / "data" / "annexations.csv", parse_dates=["effective"])

# Reference palette (dataviz skill, light mode): slot 1 = core, slot 2 = ring.
CORE, RING = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
REGIONS = ["edmonton", "calgary"]
TITLE = {"edmonton": "Edmonton region (EMRB, 13)", "calgary": "Calgary region (CMRB, 8)"}

plt.rcParams.update({
    "figure.dpi": 110, "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "lines.linewidth": 2, "legend.frameon": False,
})

# Only annexations between the core and a ring member move value across the
# core/ring line; ring-to-ring ones cancel inside the ring total.
core_annex = annex[annex.gainer.isin(REGIONS)]
core_annex[["effective", "gainer", "loser", "people"]]


# %%
def mark(ax, x, label, y=0.98):
    ax.axvline(x, color=MUTED, lw=0.8, ls=":", zorder=1)
    right = x > 2015  # late markers would run off the panel's right edge
    ax.text(x, y, f" {label} ", transform=ax.get_xaxis_transform(), fontsize=7,
            color=MUTED, va="top", ha="right" if right else "left")


def mark_core_annexations(ax, region, y=0.10):
    events = core_annex[core_annex.gainer == region].groupby("effective").loser.agg(list)
    for k, (date, losers) in enumerate(events.items()):
        names = " + ".join(l.replace("_", " ").title() for l in losers)
        mark(ax, date.year + (date.dayofyear - 1) / 365, f"annex. from {names}", y=y + 0.07 * k)


# %% [markdown]
# ## 1. The tax-base split: core share of equalized non-residential assessment
#
# Headline basis `nr` (non-residential; 1998–2004 reports print railway inside it).
# **The headline starts at taxation 1999** (DECISIONS 2026-11-25): taxation 1997–1998
# come from reports printed "capped", which understate the core against the ring
# (`docs/ASSUMPTIONS.md` A2). They are drawn as hollow points left of a break line.
# `nr_linear` adds regulated linear property; `nr_all` adds machinery & equipment too.
# x-axis is **taxation year** (= report year − 1). Taxation years 2007–2009 (scanned
# PDFs) come from FIR's EA schedule, a revised vintage within ~0.2 pp of the PDFs at the
# seams (`source == "fir_ea"`; shaded and marked). Across those years Edmonton's
# `nr_linear` rises while `nr` barely moves — a composition effect (market NR more than
# doubled, regulated linear grew ~25%), not a data break (TODO: caption it in Phase 4).

# %%
# The capped years must be exactly the ones before the headline start.
HEAD = 1999
capped = share[share.basis_note.str.contains("capped (1998-1999 reports)", regex=False)]
assert set(capped.taxation_year) == set(range(1997, HEAD)), sorted(set(capped.taxation_year))
# Share-chart caveat (audit #1, docs/FINDINGS_headline_share_2026-11-13.md §Recommendation;
# wording recorded in docs/SPEC_phase1.md §"Chart text"). Its figures are computed here.
lv = share[share.basis == "nr"].set_index(["region", "taxation_year"])
chg = {r: f"{lv.loc[(r, 2025), 'core_value'] / lv.loc[(r, 2015), 'core_value'] - 1:+.0%}".replace("-", "−")
       for r in REGIONS}
CAVEAT = ("Share of assessed value, not of buildings or businesses. It falls when ring property "
          "gains value faster than core property, through new construction or through revaluation. "
          "Most of the fall came after 2015, when the core's non-residential assessment fell in "
          f"dollar terms in both cities (Edmonton {chg['edmonton']}, Calgary "
          f"{chg['calgary']}, 2015–2025) while the ring's rose.")
STYLE = {"nr": ("-", 2.0, "nr (headline)"), "nr_linear": ("--", 1.4, "nr + linear"),
         "nr_all": (":", 1.4, "nr + linear + M&E")}
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
for ax, region in zip(axes, REGIONS):
    d = share[share.region == region]
    for basis, (ls, lw, label) in STYLE.items():
        s = d[d.basis == basis].set_index("taxation_year").core_share.reindex(range(1997, 2026))
        ax.plot(s.loc[HEAD:].index, s.loc[HEAD:] * 100, color=CORE, ls=ls, lw=lw, label=label)
        ax.plot(s.loc[:HEAD - 1].index, s.loc[:HEAD - 1] * 100, "o", ms=3.5, mfc="white",
                mec=CORE, alpha=0.7)
    ax.axvline(HEAD - 0.5, color=MUTED, lw=1, zorder=1)
    ax.text(HEAD - 0.6, 0.02, "capped ", transform=ax.get_xaxis_transform(), fontsize=7,
            color=MUTED, ha="right", va="bottom")
    fir = d[(d.source == "fir_ea") & (d.basis == "nr")]
    ax.axvspan(fir.taxation_year.min() - 0.5, fir.taxation_year.max() + 0.5, color=GRID, alpha=0.6, lw=0)
    ax.plot(fir.taxation_year, fir.core_share * 100, "o", ms=3, color=CORE)
    ax.text(fir.taxation_year.mean(), 0.5, "from FIR (scanned PDFs)", transform=ax.get_xaxis_transform(),
            fontsize=7, color=MUTED, ha="center", va="center", rotation=90)
    mark_core_annexations(ax, region)
    ax.set_title(TITLE[region], loc="left", color=INK, fontsize=10)
    ax.set_xlim(1996, 2026)
axes[0].set_ylabel("core share of regional base (%)")
axes[1].legend(loc="center left", fontsize=8, title="core share on basis", title_fontsize=8)
fig.suptitle(f"Core city's share of the region's equalized non-residential assessment, {HEAD}–2025",
             x=0.01, ha="left", color=INK, fontsize=11)
fig.text(0.01, -0.04, "Basis: equalized assessment (Municipal Affairs reports); 2025 board "
         "membership applied to all years; six printed values corrected from FIR EA "
         "(DECISIONS 2026-10-02); 2007–2009 from FIR EA, revised vintage (DECISIONS 2026-10-19); "
         "1997–1998 capped, not on the later basis (DECISIONS 2026-11-25).", fontsize=7, color=MUTED)
fig.text(0.01, -0.09, CAVEAT, fontsize=7, color=MUTED, wrap=True)
fig.text(0.01, -0.17, "nr + linear + M&E: the Industrial Heartland's Strathcona and Sturgeon "
         "carry most of Edmonton's fall on this basis (section 1c).", fontsize=7, color=MUTED)
fig.tight_layout()

# %% [markdown]
# ## 1b. Which side moved: core and ring levels
#
# The share hides whether the core shrank or the ring grew. Core and ring `nr` value,
# indexed to taxation 1999 = 100. **Nominal dollars** (no deflator chosen yet — TODO
# "Inflation adjustment"), so the index includes inflation on both sides.

# %%
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
for ax, region in zip(axes, REGIONS):
    d = share[(share.region == region) & (share.basis == "nr")].set_index("taxation_year").loc[HEAD:]
    for col, color, label in [("core_value", CORE, "core"), ("ring_value", RING, "ring")]:
        ax.plot(d.index, d[col] / d[col].iloc[0] * 100, color=color, label=label)
    ax.axhline(100, color=MUTED, lw=0.8)
    ax.set_title(TITLE[region], loc="left", color=INK, fontsize=10)
    ax.set_xlim(HEAD - 1, 2026)
    ax.legend(loc="upper left", fontsize=8)
axes[0].set_ylabel(f"nr value, index ({HEAD} = 100)")
fig.suptitle(f"Equalized non-residential assessment, core and ring, indexed to {HEAD} (nominal)",
             x=0.01, ha="left", color=INK, fontsize=11)
fig.text(0.01, -0.04, "Basis: equalized assessment, nr; nominal dollars; 2025 board membership "
         "applied to all years; 2007–2009 from FIR EA.", fontsize=7, color=MUTED)
fig.tight_layout()

# %% [markdown]
# ## 1c. Where the fall came from: per-member contribution
#
# A member's contribution is the change in its share of the regional total,
# 1999 → 2025, in percentage points; the ring members' contributions sum to the fall
# in the core share. Replaces the Industrial Heartland guess with the measured split
# (`docs/FINDINGS_headline_share_2026-11-13.md` §L1, which measured from 1997).

# %%
MEMBER_BASES = {"nr": ["nr", "nr_incl_railway"],
                "nr_all": ["nr", "nr_incl_railway", "nr_linear", "nr_railway", "nr_cogen_me", "me"]}
fig, axes = plt.subplots(2, 2, figsize=(10, 7))
for i, (basis, classes) in enumerate(MEMBER_BASES.items()):
    v = members[members["class"].isin(classes)].groupby(["region", "muni_id", "taxation_year"]).value.sum()
    for j, region in enumerate(REGIONS):
        x = v.loc[region].unstack()[[HEAD, 2025]]
        pp = (x / x.sum()).diff(axis=1)[2025] * 100
        fall = -pp[region]
        ref = share[(share.region == region) & (share.basis == basis)].set_index("taxation_year").core_share
        assert abs(fall - (ref[HEAD] - ref[2025]) * 100) < 1e-3  # core_share is rounded to 6 dp, (region, basis, fall)
        ring = pp.drop(region).sort_values()
        ax = axes[i, j]
        ax.barh([m.replace("_", " ").title() for m in ring.index], ring,
                color=[RING if c >= 0 else MUTED for c in ring])
        ax.axvline(0, color=MUTED, lw=0.8)
        ax.set_title(f"{TITLE[region]} — {basis}: core fell {fall:.1f} pp", loc="left",
                     color=INK, fontsize=9)
        ax.tick_params(axis="y", labelsize=7)
    axes[i, 0].set_xlabel("contribution to the core's fall (pp)")
fig.suptitle(f"Change in each ring member's share of the regional total, {HEAD}–2025",
             x=0.01, ha="left", color=INK, fontsize=11)
fig.text(0.01, -0.02, "Basis: equalized assessment; 2025 board membership applied to all years; "
         "nr_all = nr + linear + railway + co-gen M&E + M&E. Grey bars: grew slower than the region.",
         fontsize=7, color=MUTED)
fig.tight_layout()

# %%
# Corrected cells, as the series records them (no silent substitutions).
corr = share[share.basis_note.str.contains("corrected from FIR")]
corr[["region", "taxation_year", "basis", "core_share", "basis_note"]].assign(
    basis_note=lambda d: d.basis_note.str.extract(r"corrected from FIR EA: (.*)")[0])

# %% [markdown]
# ## 2. Provincial transfers per capita, core vs ring
#
# Total provincial transfers (operating + capital), 5-year rolling average per capita
# (bold; starts 2005 because population starts 2001) over the annual value (thin).
# x-axis is the FIR year. From 2023 FIR splits the lines (01910+01920 → 01912+01922):
# a reclassification, marked.

# %%
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
for ax, region in zip(axes, REGIONS):
    d = transfers[(transfers.region == region) & (transfers.level == "side")]
    for role, color in [("core", CORE), ("ring", RING)]:
        s = d[d.role == role].set_index("year")
        ax.plot(s.index, s.per_capita, color=color, lw=0.8, alpha=0.45)
        ax.plot(s.index, s.per_capita_5yr, color=color, lw=2, label=role)
    mark(ax, 2022.5, "2023 line split")
    mark_core_annexations(ax, region)
    ax.set_title(TITLE[region], loc="left", color=INK, fontsize=10)
    ax.set_xlim(2000, 2028)
    ax.legend(loc="upper left", fontsize=8)
axes[0].set_ylabel("$ per person (nominal)")
fig.suptitle("Provincial transfers per capita: 5-year average (bold) and annual (thin)",
             x=0.01, ha="left", color=INK, fontsize=11)
fig.text(0.01, -0.04, "Basis: FIR 01910+01920 to 2022, 01912+01922 from 2023; nominal dollars; "
         "population on each year's boundaries; 2025 board membership applied to all years.",
         fontsize=7, color=MUTED)
fig.tight_layout()

# %% [markdown]
# ## 3. Operating spending per capita by function, core vs ring
#
# Gross operating cost per capita. FIR switches to accrual in 2009 (expense minus
# amortization from then); the step was measured on restated 2008 and is ≤3% for police,
# transit and FCSS, so those run through it. Public housing changes scope at 2009 and
# starts there.
#
# - **Police ring excludes** members that report no police spending (rural RCMP costs
#   aren't in that line): Parkland and Sturgeon (Edmonton), Foothills and Rocky View
#   (Calgary), every year; plus the unexplained zeros Devon 2021 and Cochrane 2022.
# - **Not built (decided 2026-10-10):** Calgary-core FCSS and housing, and Edmonton-core FCSS
#   before 2007. Calgary moves amounts between FIR function lines from year to year (2016,
#   2020, 2022, probably 2025), and Edmonton's FCSS line doubles in 2007 while its own
#   "Community and family" spending grows 9%. So Calgary's core-vs-ring comparison is police
#   and transit. Edmonton-core housing 2021–2023 is real, and 2022 includes a one-time
#   non-cash transfer to Homeward Trust of about $70.0M (marked).
#   `docs/FINDINGS_spending_jumps_2026-10-10.md`.

# %%
FUNCS = ["police", "transit", "fcss", "housing"]
fig, axes = plt.subplots(len(FUNCS), 2, figsize=(10, 11), sharex=True, sharey="row")
for i, func in enumerate(FUNCS):
    for j, region in enumerate(REGIONS):
        ax = axes[i, j]
        d = spending[(spending.region == region) & (spending.level == "side")
                     & (spending.function == func)]
        for role, color in [("core", CORE), ("ring", RING)]:
            s = d[d.role == role].set_index("year").gross_per_capita
            ax.plot(s.index, s, color=color, label=role)
        if d[d.role == "core"].empty:
            ax.text(0.02, 0.88, "core not built: FIR line not comparable year to year",
                    transform=ax.transAxes, fontsize=8, color=MUTED, va="center")
        if (func, region) == ("housing", "edmonton"):
            mark(ax, 2022, "Homeward Trust\ntransfer (non-cash)", y=0.98)
        mark(ax, 2008.5, "2009 accrual")
        ax.set_title(f"{func.upper() if func == 'fcss' else func.title()} — {TITLE[region]}",
                     loc="left", color=INK, fontsize=9)
        ax.set_xlim(2000, 2028)
    axes[i, 0].set_ylabel("$ per person")
# After both panels of a row are drawn, or the shared row limit freezes on the first.
for ax in axes.flat:
    ax.set_ylim(bottom=0)
axes[0, 0].legend(loc="upper left", fontsize=8)
fig.suptitle("Gross operating spending per capita by function (nominal $)",
             x=0.01, ha="left", color=INK, fontsize=11)
fig.text(0.01, -0.01, "Basis: FIR Schedule C operating expenditure to 2008, Schedule C expense − "
         "Schedule E amortization from 2009; nominal dollars; police ring excludes members "
         "reporting no police spending; population on each year's boundaries; 2025 board "
         "membership applied to all years.", fontsize=7, color=MUTED, wrap=True)
fig.tight_layout()

# %% [markdown]
# ## 4. Core-to-ring ratio, latest year
#
# Same bases as above. Police ring = reporting members only. Ratio left blank where the
# ring spends under $1 per person (Edmonton-ring housing).

# %%
last = spending.year.max()
side = spending[(spending.level == "side") & (spending.year == last)]
t = side.pivot_table(index=["function", "region"], columns="role", values="gross_per_capita")
t["core / ring"] = t.core / t.ring
tr = transfers[(transfers.level == "side") & (transfers.year == last)].pivot_table(
    index="region", columns="role", values="per_capita_5yr")
tr["core / ring"] = tr.core / tr.ring
print(f"Gross operating $ per capita, {last} (nominal)")
display(t.round({"core": 0, "ring": 0, "core / ring": 1}).assign(
    **{"core / ring": lambda d: d["core / ring"].where(d.ring >= 1)}))
print(f"Provincial transfers $ per capita, 5-year average ending {last} (nominal)")
display(tr.round({"core": 0, "ring": 0, "core / ring": 2}))
