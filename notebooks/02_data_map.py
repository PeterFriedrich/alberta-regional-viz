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
# # Data map: what we hold and how it connects
#
# **Internal working notebook.** Directed graphs of the project's data, drawn by
# `tools/data_map.py` from the repo itself. Nothing here is hand-drawn, so re-running
# picks up a new `src/` step, a new member or a changed exclusion:
# - **Pipeline**: publisher → `src/` step → file, read from each step's argparse defaults.
# - **Region** (Edmonton, Calgary): region → core/ring → member → input dataset → output
#   series, with year coverage read from `data/processed/`.
#
# How to read them:
# - Node colours: blue = publisher or region; tan = `src/` step or input dataset;
#   green = committed file or built series; **amber = built locally only (gitignored)**,
#   or a file not built on this machine; grey dashed = raw downloads (never committed).
# - A dataset's node gives its common year span. A member's edge is labelled only where
#   the member differs from that span (a correction, a gap).
# - **Orange dashed** = member left out of that series: police where the province polices
#   (RCMP) and unexplained zero years, or a classification-unstable series not built
#   (decision 2026-10-10).
# - **Blue dotted** = annexation between two members (loser → gainer), from
#   `data/annexations.csv`.
#
# Rebuild: `.venv/bin/jupytext --sync notebooks/02_data_map.py` then
# `.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_data_map.ipynb`.
# The same graphs as a web page: `.venv/bin/python tools/data_map.py --html <path>`.

# %%
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / "tools"))
import data_map as dm  # noqa: E402

# %% [markdown]
# ## Pipeline
#
# Read left to right: publishers, the fetch steps, raw downloads, parse and build steps,
# processed tables. `equalized_long.csv` and `member_assessment.csv` are gitignored, so a
# fresh clone has to run `fetch_equalized` → `parse_equalized` → `build_share_series`
# to get them; everything else under `processed/` is committed.

# %%
dm.draw(dm.pipeline_graph())
plt.show()

# %% [markdown]
# ## Edmonton region (EMRB 2025 membership, applied to every year)

# %%
dm.draw(dm.region_graph("edmonton"))
plt.show()

# %% [markdown]
# Where each Edmonton member differs from the dataset spans above. "all" = the dataset's
# full span; a blank series column = the member is in every year of that series.

# %%
pd.DataFrame(dm.coverage_table("edmonton")).fillna("").set_index("member")

# %% [markdown]
# ## Calgary region (CMRB 2025 membership, applied to every year)
#
# Calgary's core-vs-ring spending comparison is police and transit only: its FCSS and
# housing lines aren't built in any year (decision 2026-10-10).

# %%
dm.draw(dm.region_graph("calgary"))
plt.show()

# %%
pd.DataFrame(dm.coverage_table("calgary")).fillna("").set_index("member")
