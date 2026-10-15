"""Directed graphs of what data the project holds and how it connects.

Two graphs, both derived from the repo so they don't drift from it:

- pipeline: external source → src/ step → file. Read from each src/*.py's argparse
  defaults (`default=REPO / "..."`) and its http(s) constants; a file is a step's
  output when its argument is `--out*`, or a fetch step's under data/raw.
- region (edmonton | calgary): region → core/ring → member → input dataset → output
  series. Coverage comes from data/processed; a member whose years differ from the
  rest gets its own edge label, a member left out of a series gets a dashed edge.
  Annexations between members are dotted edges.

Usage:
    python tools/data_map.py [--json] [--mermaid] [--html out.html]
"""
import argparse
import ast
import csv
import html
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROCESSED = REPO / "data/processed"


# ── pipeline ────────────────────────────────────────────────────────────────

def _path_default(node: ast.AST) -> str | None:
    """`REPO / "a/b"` → "a/b"."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div) and isinstance(node.right, ast.Constant):
        return node.right.value
    return None


def _module_io(path: Path) -> dict:
    tree = ast.parse(path.read_text())
    args, urls = {}, []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "add_argument" and n.args:
            flag = n.args[0].value if isinstance(n.args[0], ast.Constant) else None
            default = next((_path_default(k.value) for k in n.keywords if k.arg == "default"), None)
            if flag and default:
                args[flag.lstrip("-").replace("-", "_")] = default
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and re.match(r"https?://", n.value):
            urls.append(n.value)
        if isinstance(n, ast.JoinedStr):
            head = n.values[0] if n.values else None
            if isinstance(head, ast.Constant) and re.match(r"https?://", str(head.value)):
                urls.append(head.value)
    # A directory argument joined to a literal (`args.out_dir / "x.csv"`) names the real files.
    joined = defaultdict(list)
    for n in ast.walk(tree):
        if (isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div) and isinstance(n.right, ast.Constant)
                and isinstance(n.left, ast.Attribute) and isinstance(n.left.value, ast.Name)
                and n.left.value.id == "args" and n.left.attr in args):
            if n.right.value != "manifest.json":  # bookkeeping inside a raw dir, not a dataset
                joined[n.left.attr].append(n.right.value)
    fetch = path.stem.startswith("fetch_")
    inputs, outputs = [], []
    for name, rel in args.items():
        files = [f"{rel}/{f}" for f in joined[name]] or [rel]
        is_out = name.startswith("out") or (fetch and rel.startswith("data/raw"))
        (outputs if is_out else inputs).extend(files)
    first_para = " ".join((ast.get_docstring(tree) or "").split("\n\n")[0].split())
    doc = re.split(r"(?<=[a-z0-9)])\. ", first_para)[0].rstrip(".")
    return {"inputs": inputs, "outputs": outputs, "urls": urls, "doc": doc}


def _tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files", "data"], cwd=REPO, capture_output=True, text=True).stdout
    return set(out.split())


def pipeline_graph() -> dict:
    tracked = _tracked()
    nodes, edges = {}, []
    produced = set()
    for py in sorted((REPO / "src").glob("*.py")):
        io = _module_io(py)
        if not (io["inputs"] or io["outputs"]):
            continue
        step = f"src/{py.name}"
        nodes[step] = {"kind": "step", "label": py.name, "detail": io["doc"]}
        for url in io["urls"]:
            host = re.match(r"https?://([^/]+)", url).group(1)
            sid = f"source:{py.stem}"
            pkg = re.search(r"[?&]id=([\w-]+)", url)
            nodes[sid] = {"kind": "source", "label": host, "detail": f"package {pkg.group(1)}" if pkg else ""}
            edges.append({"src": sid, "dst": step})
            break  # one source node per fetch step; its other URLs are the same publisher
        for f in io["inputs"]:
            nodes.setdefault(f, {})
            edges.append({"src": f, "dst": step})
        for f in io["outputs"]:
            nodes.setdefault(f, {})
            produced.add(f)
            edges.append({"src": step, "dst": f})
    for f, attrs in nodes.items():
        if attrs.get("kind"):
            continue
        is_dir = f.startswith("data/raw")
        attrs.update({
            "label": f.removeprefix("data/"),
            # raw/ is never committed; a processed file is either tracked or local-only
            "kind": "raw" if is_dir else ("output" if f in produced else "reference"),
            "tracked": is_dir is False and f in tracked,
            "exists": (REPO / f).exists(),
        })
    return {"nodes": nodes, "edges": _dedupe(edges)}


def _dedupe(edges: list[dict]) -> list[dict]:
    seen, out = set(), []
    for e in edges:
        key = (e["src"], e["dst"], e.get("style"), e.get("label"))
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


# ── region ──────────────────────────────────────────────────────────────────

def _read(name: str) -> list[dict] | None:
    p = PROCESSED / name
    if not p.exists():
        return None
    with p.open(newline="") as f:
        return list(csv.DictReader(f))


def year_spans(years) -> str:
    """{1997,…,2006,2010,…,2025} → "1997–2006, 2010–2025"."""
    ys = sorted({int(y) for y in years})
    if not ys:
        return "none"
    spans, start = [], ys[0]
    for a, b in zip(ys, ys[1:] + [None]):
        if b != a + 1:
            spans.append(str(start) if start == a else f"{start}–{a}")
            start = b
    return ", ".join(spans)


def _coverage_edges(members, years_by_member, src_of, dst, dataset) -> tuple[str, list[dict]]:
    """Edges member → dataset. The common span goes on the dataset node; a member
    whose span differs gets it on its edge, and one with no rows gets none (flagged)."""
    spans = {m: year_spans(years_by_member.get(m, ())) for m in members}
    common = max(set(spans.values()), key=list(spans.values()).count)
    edges = []
    for m in members:
        e = {"src": src_of(m), "dst": dst}
        if spans[m] == "none":
            e.update(style="missing", label=f"no {dataset} rows")
        elif spans[m] != common:
            e["label"] = spans[m]
        edges.append(e)
    return common, edges


def region_graph(region: str) -> dict:
    with (REPO / "data/regions.csv").open(newline="") as f:
        reg = [r for r in csv.DictReader(f) if r["region"] == region]
    members = [r["muni_id"] for r in reg]
    role = {r["muni_id"]: r["role"] for r in reg}
    nodes, edges = {}, []
    rid = f"region:{region}"  # the core member shares the region's name
    nodes[rid] = {"kind": "region", "label": f"{region.title()} region", "detail": reg[0]["member_basis"]}
    for side in ("core", "ring"):
        n = sum(1 for m in members if role[m] == side)
        nodes[side] = {"kind": "side", "label": side, "detail": f"{n} member{'s' * (n != 1)}"}
        edges.append({"src": rid, "dst": side})
    for r in reg:
        # "+" aliases are rows summed into the member: dissolved villages, and Calgary's
        # 1998 "Part II" row (not a separate place, so not named here)
        absorbed = list(dict.fromkeys(
            a.lstrip("+").removeprefix("VILLAGE OF ").title() for a in r["eq_aliases"].split("|")
            if a.startswith("+") and "CITY OF" not in a))
        nodes[r["muni_id"]] = {"kind": "member", "label": r["name"],
                               "detail": f"+ {', '.join(absorbed)} summed in" if absorbed else ""}
        edges.append({"src": r["role"], "dst": r["muni_id"]})

    # inputs: one node per processed member-level table
    inputs = [
        ("member_assessment.csv", "Equalized assessment", "Municipal Affairs PDFs", "taxation_year", "muni_id"),
        ("fir_long.csv", "FIR", "Financial Information Returns", "fir_year", "muni_id"),
        ("population.csv", "Population", "StatCan 17-10-0155", "year", "muni_id"),
    ]
    for fname, label, detail, ycol, mcol in inputs:
        rows = _read(fname)
        nid = f"in:{fname}"
        if rows is None:
            nodes[nid] = {"kind": "input", "label": label, "detail": f"{detail}; {fname} not built locally",
                          "missing_file": True}
            edges.extend({"src": m, "dst": nid} for m in members)
            continue
        by_m = defaultdict(set)
        for r in rows:
            if r[mcol] in role:
                by_m[r[mcol]].add(r[ycol])
        common, es = _coverage_edges(members, by_m, lambda m: m, nid, label)
        nodes[nid] = {"kind": "input", "label": label, "detail": f"{detail}; {common}"}
        edges.extend(es)

    corrections = defaultdict(int)
    with (REPO / "data/corrections.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            corrections[r["muni_id"]] += 1
    for e in edges:
        if e["dst"] == "in:member_assessment.csv" and corrections.get(e["src"]):
            n = corrections[e["src"]]
            e["label"] = "; ".join(filter(None, [e.get("label"), f"{n} value{'s' * (n != 1)} corrected from FIR"]))

    # outputs
    share = _read("core_ring_share.csv") or []
    bases = sorted({r["basis"] for r in share if r["region"] == region})
    nid = "out:share"
    yrs = year_spans(r["taxation_year"] for r in share if r["region"] == region)
    nodes[nid] = {"kind": "output", "label": "Core share of equalized NR",
                  "detail": f"bases {', '.join(bases)}; {yrs}"}
    edges.append({"src": "in:member_assessment.csv", "dst": nid})

    transfers = [r for r in _read("transfers_per_capita.csv") or [] if r["region"] == region]
    nodes["out:transfers"] = {"kind": "output", "label": "Transfers per capita",
                              "detail": year_spans(r["year"] for r in transfers if r["level"] == "side")}
    edges += [{"src": "in:fir_long.csv", "dst": "out:transfers"}, {"src": "in:population.csv", "dst": "out:transfers"}]

    spending = [r for r in _read("spending_per_capita.csv") or [] if r["region"] == region]
    for fn in sorted({r["function"] for r in spending}, key=["police", "transit", "fcss", "housing"].index):
        nid = f"out:spending:{fn}"
        side_rows = [r for r in spending if r["function"] == fn and r["level"] == "side"]
        nodes[nid] = {"kind": "output", "label": f"Spending per capita: {fn}",
                      "detail": year_spans(r["year"] for r in side_rows)}
        edges += [{"src": "in:fir_long.csv", "dst": nid}, {"src": "in:population.csv", "dst": nid}]
        member_rows = [r for r in spending if r["function"] == fn and r["level"] == "member"]
        all_years = {r["year"] for r in side_rows}
        for m in members:
            got = {r["year"] for r in member_rows if r["unit"] == m}
            excluded = {r["year"] for r in side_rows if m in r["excluded"].split("|")}
            if excluded:
                edges.append({"src": m, "dst": nid, "style": "excluded",
                              "label": f"left out {year_spans(excluded)}"})
            elif all_years - got:
                # no row for the member's own unit; the side keeps other members (NOT_COMPARABLE)
                gap = year_spans(all_years - got)
                edges.append({"src": m, "dst": nid, "style": "excluded", "label": f"not built {gap}"})

    with (REPO / "data/annexations.csv").open(newline="") as f:
        ann = defaultdict(list)
        for r in csv.DictReader(f):
            if r["gainer"] in role and r["loser"] in role:
                ann[(r["loser"], r["gainer"])].append(r["effective"][:4])
    for (loser, gainer), years in sorted(ann.items()):
        n = len(years)
        edges.append({"src": loser, "dst": gainer, "style": "annexation",
                      "label": f"{n} annexation{'s' * (n != 1)} {year_spans(years)}"})
    return {"nodes": nodes, "edges": _dedupe(edges)}


def coverage_table(region: str) -> list[dict]:
    """Member × dataset year spans, for a table beside the region graph."""
    g = region_graph(region)
    rows = []
    for m, a in g["nodes"].items():
        if a["kind"] != "member":
            continue
        row = {"member": a["label"]}
        for e in g["edges"]:
            if e["src"] != m or e["dst"] not in g["nodes"] or g["nodes"][e["dst"]]["kind"] not in ("input", "output"):
                continue
            dst = g["nodes"][e["dst"]]
            if dst["kind"] == "input":
                row[dst["label"]] = e.get("label") or ("not built locally" if dst.get("missing_file") else "all")
            else:
                row[dst["label"]] = e["label"]
        rows.append(row)
    return rows


# ── renderers ───────────────────────────────────────────────────────────────

def _short(s: str, n: int = 80) -> str:
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + " …"


def _mid(s: str) -> str:
    return re.sub(r"\W", "_", s)


def _mtext(s: str) -> str:
    return s.replace('"', "#quot;")


def to_mermaid(g: dict, direction: str = "LR") -> str:
    lines = [f"flowchart {direction}"]
    for nid, a in g["nodes"].items():
        text = f"<b>{_mtext(a['label'])}</b>"
        if a.get("detail"):
            text += f"<br/><small>{_mtext(_short(a['detail']))}</small>"
        shape = {"source": ('[("', '")]'), "step": ('[["', '"]]'), "region": ('(["', '"])'),
                 "side": ('(["', '"])')}.get(a["kind"], ('["', '"]'))
        lines.append(f"  {_mid(nid)}{shape[0]}{text}{shape[1]}")
        cls = a["kind"] + ("_local" if a["kind"] in ("output", "reference") and a.get("tracked") is False else "")
        cls += "_missing" if a.get("missing_file") else ""
        lines.append(f"  class {_mid(nid)} {cls}")
    for e in g["edges"]:
        arrow = {"excluded": "-.-x", "missing": "-.-x", "annexation": "-.->"}.get(e.get("style"), "-->")
        label = f'|"{_mtext(e["label"])}"|' if e.get("label") else ""
        lines.append(f"  {_mid(e['src'])} {arrow}{label} {_mid(e['dst'])}")
    lines += [
        "  classDef source fill:#e7eef7,stroke:#3b5f8a,color:#1d2b3a",
        "  classDef step fill:#f2ede4,stroke:#7a6a4f,color:#2b2418",
        "  classDef raw fill:#f4f4f2,stroke:#9a9a92,color:#3a3a36,stroke-dasharray:4 3",
        "  classDef reference fill:#eef3ea,stroke:#5d7a4f,color:#1f2b19",
        "  classDef output fill:#eef3ea,stroke:#5d7a4f,color:#1f2b19",
        "  classDef output_local fill:#fbf4e6,stroke:#b07d1e,color:#33270d,stroke-dasharray:4 3",
        "  classDef region fill:#3b5f8a,stroke:#3b5f8a,color:#ffffff",
        "  classDef side fill:#e7eef7,stroke:#3b5f8a,color:#1d2b3a",
        "  classDef member fill:#ffffff,stroke:#8892a0,color:#1d2b3a",
        "  classDef input fill:#f2ede4,stroke:#7a6a4f,color:#2b2418",
        "  classDef input_missing fill:#fbf4e6,stroke:#b07d1e,color:#33270d,stroke-dasharray:4 3",
    ]
    return "\n".join(lines)


COLORS = {  # (fill, edge) per node kind; matches the Mermaid classDefs
    "source": ("#e7eef7", "#3b5f8a"), "step": ("#f2ede4", "#7a6a4f"), "raw": ("#f4f4f2", "#9a9a92"),
    "reference": ("#eef3ea", "#5d7a4f"), "output": ("#eef3ea", "#5d7a4f"), "region": ("#3b5f8a", "#3b5f8a"),
    "side": ("#e7eef7", "#3b5f8a"), "member": ("#ffffff", "#8892a0"), "input": ("#f2ede4", "#7a6a4f"),
}
LOCAL = ("#fbf4e6", "#b07d1e")  # built locally only (gitignored) or not built here
EDGE_STYLE = {None: ("#8892a0", "-"), "excluded": ("#b5651d", "--"), "missing": ("#b5651d", "--"),
              "annexation": ("#3b5f8a", ":")}


def layers(g: dict) -> dict[str, int]:
    """Longest-path layering over the feed edges (annexations are drawn within a layer)."""
    preds = defaultdict(list)
    for e in g["edges"]:
        if e.get("style") != "annexation":
            preds[e["dst"]].append(e["src"])
    memo = {}

    def depth(n):
        if n not in memo:
            memo[n] = 1 + max((depth(p) for p in preds[n]), default=-1)
        return memo[n]
    return {n: depth(n) for n in g["nodes"]}


def draw(g: dict, ax=None, width: float = 18, wrap: int = 30):
    """Draw a graph left to right with matplotlib; returns the axes."""
    import textwrap
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch

    lay = layers(g)
    cols = defaultdict(list)
    for n in g["nodes"]:
        cols[lay[n]].append(n)
    # barycentre sweeps, forward then back: order each layer by the mean position of its neighbours
    pos = {n: i for c in cols.values() for i, n in enumerate(c)}
    preds, succs = defaultdict(list), defaultdict(list)
    for e in g["edges"]:
        if e.get("style") is None:
            preds[e["dst"]].append(e["src"])
            succs[e["src"]].append(e["dst"])
    tall = max(map(len, cols.values()))

    def sweep(ks, nbrs):
        for k in ks:
            cols[k].sort(key=lambda n: sum(pos[p] for p in nbrs[n]) / len(nbrs[n]) if nbrs[n] else pos[n])
            pos.update({n: (i + 0.5) * tall / len(cols[k]) for i, n in enumerate(cols[k])})
    for _ in range(2):
        sweep(sorted(cols)[1:], preds)
        sweep(sorted(cols, reverse=True)[1:], succs)
    xy = {}
    for k, c in cols.items():
        step = tall / len(c)
        for i, n in enumerate(c):
            xy[n] = (k, -(i + 0.5) * step)
    if ax is None:
        _, ax = plt.subplots(figsize=(width, max(6, tall * 0.62)))
    ax.set_xlim(-0.5, max(cols) + 0.5)
    ax.set_ylim(-tall - 0.2, 0.2)
    boxes = {}
    for n, a in g["nodes"].items():
        fill, edge = COLORS[a["kind"]]
        if a.get("missing_file") or (a["kind"] == "output" and a.get("tracked") is False):
            fill, edge = LOCAL
        text = "\n".join(textwrap.wrap(a["label"], wrap))
        if a.get("detail"):
            text += "\n" + "\n".join(textwrap.wrap(_short(a["detail"], 70), wrap))
        boxes[n] = ax.text(*xy[n], text, ha="center", va="center", fontsize=7.5, zorder=2,
                           color="white" if a["kind"] == "region" else "#1d2b3a",
                           bbox=dict(boxstyle="round,pad=0.4", fc=fill, ec=edge, lw=1))
    # Anchor edges on the drawn boxes: measure them in data units once rendered.
    fig = ax.figure
    fig.canvas.draw()
    inv = ax.transData.inverted()
    side = {}
    for n, t in boxes.items():
        (l, _), (r, _) = inv.transform(t.get_bbox_patch().get_window_extent(fig.canvas.get_renderer()).get_points())
        side[n] = (l, r)
    ys_per_unit = abs(ax.transData.transform((0, 1))[1] - ax.transData.transform((0, 0))[1])
    xs_per_unit = abs(ax.transData.transform((1, 0))[0] - ax.transData.transform((0, 0))[0])
    n_ann, used_y, used_exc = 0, [], []
    for e in g["edges"]:
        color, ls = EDGE_STYLE[e.get("style")]
        (_, y0), (_, y1) = xy[e["src"]], xy[e["dst"]]
        if e.get("style") == "annexation":
            # same layer: leave and enter on the left, bulging left
            a, b = (side[e["src"]][0], y0), (side[e["dst"]][0], y1)
            # constant bulge in pixels, staggered so arcs between near neighbours don't overlap
            bulge = 20 + 5 * (n_ann := n_ann + 1)
            rad = min(1.0, bulge / (abs(y1 - y0) * ys_per_unit)) * (1 if y1 < y0 else -1)
            # labels in one right-aligned column left of the arcs, nudged apart vertically
            ly = (y0 + y1) / 2
            while any(abs(ly - u) < 0.3 for u in used_y):
                ly -= 0.3
            used_y.append(ly)
            label_at = (min(side[m][0] for m in cols[lay[e["src"]]]) - 0.08, ly)
        else:
            a, b = (side[e["src"]][1], y0), (side[e["dst"]][0], y1)
            rad = 0.0
            # coverage notes near the member; exclusions near the series, nudged apart where they converge
            t = 0.3 if e.get("style") is None else 0.9
            lx, ly = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
            if e.get("style"):
                while any(abs(ly - u) < 0.22 and abs(lx - v) < 0.3 for v, u in used_exc):
                    ly -= 0.22
                used_exc.append((lx, ly))
            label_at = (lx, ly)
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=9, color=color, linestyle=ls,
                                     lw=0.7 if e.get("style") is None else 1.3, shrinkA=1, shrinkB=1,
                                     connectionstyle=f"arc3,rad={rad}", zorder=1))
        if e.get("label"):
            ha = "right" if e.get("style") == "annexation" else "center"
            if ha == "right":
                ax.plot([label_at[0] + 0.01, a[0] - bulge / 2 / xs_per_unit], [label_at[1], (y0 + y1) / 2],
                        color=color, lw=0.4, zorder=1)  # leader line to the arc
            text = e["label"]
            if ha == "right":
                short = lambda n: re.sub(r"^(City|Town) of | County$", "", g["nodes"][n]["label"])  # noqa: E731
                text = f"{short(e['src'])} → {short(e['dst'])}: {text.split(' ', 2)[2]}"
            ax.text(*label_at, text, fontsize=6.5, color=color, ha=ha, va="center", zorder=3,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    ax.axis("off")
    return ax


HTML = """<title>Regional Data Map</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono&display=swap">
<style>
/* layout: one reading column; each graph in its own sideways-scrolling panel */
:root {{ --bg:#fafaf7; --fg:#1d2b3a; --muted:#5b6673; --rule:#d9dcd6; --panel:#ffffff; --accent:#3b5f8a;
  --sans:"IBM Plex Sans",system-ui,sans-serif; --mono:"IBM Plex Mono",ui-monospace,monospace }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#14181d; --fg:#e4e8ec; --muted:#9aa4af;
  --rule:#2c333b; --panel:#f4f5f2; --accent:#8fb2dc; color-scheme:dark }} }}
:root[data-theme="dark"] {{ --bg:#14181d; --fg:#e4e8ec; --muted:#9aa4af; --rule:#2c333b; --panel:#f4f5f2;
  --accent:#8fb2dc; color-scheme:dark }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.55 var(--sans);
  padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:24px 48px }}
main {{ max-width:1200px; margin:0 auto; display:grid; gap:28px }}
h1 {{ font-size:1.6rem; margin:0; text-wrap:balance }}
h2 {{ font-size:1.15rem; margin:0 0 4px; text-wrap:balance }}
p {{ margin:0; max-width:70ch; color:var(--muted) }}
nav {{ display:flex; flex-wrap:wrap; gap:8px }}
nav a {{ color:var(--accent); font-weight:600; text-decoration:none; border:1px solid var(--rule); border-radius:4px; padding:4px 10px }}
nav a:focus-visible, nav a:hover {{ outline:2px solid var(--accent) }}
section {{ display:grid; gap:10px; min-width:0 }}
.graph {{ overflow-x:auto; background:var(--panel); border:1px solid var(--rule); border-radius:6px; padding:12px }}
.legend {{ font-family:var(--mono); font-size:12px; color:var(--muted) }}
.tablewrap {{ overflow-x:auto }}
table {{ border-collapse:collapse; font-size:13px; font-variant-numeric:tabular-nums }}
th, td {{ text-align:left; padding:4px 10px; border-bottom:1px solid var(--rule); white-space:nowrap }}
th {{ font-weight:600; font-size:12px; letter-spacing:.03em; text-transform:uppercase; color:var(--muted) }}
td.flag {{ color:#b5651d }}
footer {{ font-family:var(--mono); font-size:12px; color:var(--muted) }}
</style>
<main>
<header style="display:grid;gap:8px">
<h1>Regional Data Map</h1>
<p>What data the Alberta regional lens holds and how it connects: the pipeline from publishers to files,
then for each region the members, the datasets each feeds, and the series built from them. Generated from
the repo by <code>tools/data_map.py</code> at commit {commit}.</p>
<nav><a href="#pipeline">Pipeline</a>{nav}</nav>
</header>
{sections}
<footer>Regenerate: .venv/bin/python tools/data_map.py --html &lt;path&gt;, then republish.</footer>
</main>
"""

LEGEND_PIPE = ("cylinder = publisher · double box = src/ step · green = committed file · "
               "amber dashed = built locally, gitignored · grey dashed = raw downloads (never committed)")
LEGEND_REGION = ("solid = feeds · edge label = years where a member differs from the dataset's span · "
                 "x-dashed = member left out of that series · dotted = annexation (loser → gainer)")


def to_html(commit: str) -> str:
    sections = [f'<section id="pipeline"><h2>Pipeline</h2><p class="legend">{LEGEND_PIPE}</p>'
                f'<div class="graph"><pre class="mermaid">{html.escape(to_mermaid(pipeline_graph()))}</pre></div></section>']
    nav = []
    for region in ("edmonton", "calgary"):
        rows = coverage_table(region)
        cols = list(dict.fromkeys(k for r in rows for k in r))
        head = "".join(f"<th>{html.escape(c)}</th>" for c in cols)
        body = "".join("<tr>" + "".join(
            f'<td class="{"" if r.get(c, "") in ("all", "") else "flag"}">{html.escape(r.get(c, ""))}</td>'
            for c in cols) + "</tr>" for r in rows)
        sections.append(
            f'<section id="{region}"><h2>{region.title()} region</h2><p class="legend">{LEGEND_REGION}</p>'
            f'<div class="graph"><pre class="mermaid">{html.escape(to_mermaid(region_graph(region)))}</pre></div>'
            f'<p>Where each member differs. "all" = the dataset\'s full span; blank = in every year of that series.</p>'
            f'<div class="tablewrap"><table><tr>{head}</tr>{body}</table></div></section>')
        nav.append(f'<a href="#{region}">{region.title()}</a>')
    return HTML.format(commit=commit, nav="".join(nav), sections="\n".join(sections))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="print all graphs as JSON")
    ap.add_argument("--mermaid", action="store_true", help="print all graphs as Mermaid")
    ap.add_argument("--html", type=Path, help="write the HTML page here")
    args = ap.parse_args()
    graphs = {"pipeline": pipeline_graph(), "edmonton": region_graph("edmonton"), "calgary": region_graph("calgary")}
    if args.json:
        print(json.dumps(graphs, indent=1))
    if args.mermaid:
        for name, g in graphs.items():
            print(f"%% {name}\n{to_mermaid(g)}\n")
    if args.html:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                                capture_output=True, text=True).stdout.strip()
        args.html.write_text(to_html(commit))
        print(f"wrote {args.html}")


if __name__ == "__main__":
    main()
