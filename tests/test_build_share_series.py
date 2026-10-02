"""build_share_series and fetch_equalized on synthetic inputs, plus the
UPE01548 reproduction check on the real processed file when it exists."""
import csv
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import build_share_series as bss  # noqa: E402
import fetch_equalized as fe  # noqa: E402


def regions(tmp_path, rows):
    p = tmp_path / "regions.csv"
    with p.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["muni_id", "name", "region", "role", "eq_aliases",
                                          "member_basis", "notes"])
        w.writeheader()
        for r in rows:
            w.writerow({"name": r[0], "member_basis": "test", "notes": "",
                        "muni_id": r[0], "region": r[1], "role": r[2], "eq_aliases": r[3]})
    return bss.load_regions(p)


def long(year, name, **vals):
    return [{"report_year": str(year), "muni_name_raw": name, "class": c, "value": str(v),
             "page": "1"} for c, v in vals.items()]


REGION = [("core", "r", "core", "CORE CITY"),
          ("ring", "r", "ring", "RING COUNTY|RING NO. 31 M.D. OF")]


def test_shares_per_basis_and_old_alias(tmp_path):
    reg = regions(tmp_path, REGION)
    rows = (long(2014, "Core City", nr=60, nr_linear=10, nr_railway=0, me=0)
            + long(2014, "Ring No. 31, M.D. Of", nr=40, nr_linear=10, nr_railway=0, me=100))
    found, years = bss.member_values(rows, reg)
    s = {r["basis"]: r["core_share"] for r in bss.shares(found, years, reg)}
    assert s == {"nr": 0.6, "nr_linear": round(70 / 120, 6), "nr_all": round(70 / 220, 6)}


def test_old_class_set_uses_old_bases(tmp_path):
    reg = regions(tmp_path, REGION)
    rows = (long(2003, "Core City", nr_incl_railway=60, nr_linear=10, me=0, residential_incl_farmland=5)
            + long(2003, "Ring County", nr_incl_railway=40, nr_linear=10, me=100, residential_incl_farmland=5))
    found, years = bss.member_values(rows, reg)
    out = {r["basis"]: r for r in bss.shares(found, years, reg)}
    assert out["nr"]["core_share"] == 0.6 and "railway" in out["nr"]["basis_note"]
    assert out["nr_all"]["core_share"] == round(70 / 220, 6)
    assert "railway" not in out["nr_linear"]["basis_note"]


def test_mixed_class_sets_in_one_year_fail(tmp_path):
    reg = regions(tmp_path, REGION)
    rows = long(2003, "Core City", nr_incl_railway=1) + long(2003, "Ring County", nr=1)
    found, years = bss.member_values(rows, reg)
    with pytest.raises(bss.BuildError, match="mix"):
        bss.shares(found, years, reg)


def test_part_alias_is_summed_and_a_plain_duplicate_still_fails(tmp_path):
    reg = regions(tmp_path, [("core", "r", "core", "CORE CITY|+CORE CITY (PART II)"),
                             ("ring", "r", "ring", "RING COUNTY")])
    rows = (long(1998, "Core City", nr_incl_railway=60) + long(1998, "Core City (Part II)", nr_incl_railway=5)
            + long(1998, "Ring County", nr_incl_railway=35))
    found, _ = bss.member_values(rows, reg)
    assert found[(1998, "core")]["nr_incl_railway"] == 65
    twice = rows + [{**r, "page": "2"} for r in long(1998, "Core City (Part II)", nr_incl_railway=5)]
    with pytest.raises(bss.BuildError, match="matched twice"):
        bss.member_values(twice, reg)


def test_two_parts_in_one_year_are_summed_but_two_spellings_of_one_part_fail(tmp_path):
    reg = regions(tmp_path, [("core", "r", "core", "CORE CITY"),
                             ("ring", "r", "ring", "RING COUNTY|+VILLAGE OF A|+A|+VILLAGE OF B")])
    rows = (long(1998, "Core City", nr_incl_railway=60) + long(1998, "Ring County", nr_incl_railway=30)
            + long(1998, "Village of A", nr_incl_railway=4) + long(1998, "Village of B", nr_incl_railway=6))
    found, _ = bss.member_values(rows, reg)
    assert found[(1998, "ring")]["nr_incl_railway"] == 40
    with pytest.raises(bss.BuildError, match="matched twice"):
        bss.member_values(rows + long(1998, "A", nr_incl_railway=4), reg)


def test_missing_member_fails(tmp_path):
    reg = regions(tmp_path, REGION)
    rows = long(2014, "Core City", nr=1) + long(2015, "Core City", nr=1) + long(2015, "Ring County", nr=1)
    with pytest.raises(bss.BuildError, match=r"\(2014, 'ring'\)"):
        bss.member_values(rows, reg)


def test_alias_matching_two_rows_fails(tmp_path):
    reg = regions(tmp_path, [("core", "r", "core", "CORE CITY"),
                             ("ring", "r", "ring", "RING COUNTY|RING")])
    rows = long(2014, "Core City", nr=1) + long(2014, "Ring County", nr=1) + long(2014, "Ring", nr=2)
    with pytest.raises(bss.BuildError, match="matched twice"):
        bss.member_values(rows, reg)


def test_alias_shared_by_two_members_fails(tmp_path):
    with pytest.raises(bss.BuildError, match="used by both"):
        regions(tmp_path, [("a", "r", "core", "X"), ("b", "r", "ring", "Y|X")])


def test_fetch_duplicate_year_and_vanished_year():
    pkg = {"resources": [{"name": "Provincial 2020 equalized assessment report "},
                         {"name": "Something else"},
                         {"name": "Provincial 2021 Equalized Assessment Report"}]}
    new = fe.PACKAGES["2368-657x"]
    assert sorted(fe.report_resources(pkg, new)) == [2020, 2021]
    old = {"resources": [{"name": "2008 equalized assessment report"}]}
    assert sorted(fe.report_resources(old, fe.PACKAGES["1844032"])) == [2008]
    with pytest.raises(fe.FetchError, match="2021"):
        fe.report_resources({"resources": [{"name": "2021 equalized assessment report"}]},
                            fe.PACKAGES["1844032"], fe.report_resources(pkg, new))
    with pytest.raises(fe.FetchError, match="two resources"):
        fe.report_resources({"resources": pkg["resources"] * 2}, new)
    with pytest.raises(fe.FetchError, match="no longer listed"):
        fe.check_no_year_vanished({2021: {}}, {"files": [{"report_year": 2020}, {"report_year": 2021}]})


SERIES = REPO / "data/processed/core_ring_share.csv"


def test_reproduces_upe01548():
    """City of Edmonton UPE01548 (2024-06-19, p. 5): Edmonton's share of the
    region's non-residential assessment fell from 72% (2008) to 60% (2022),
    13 EMRB members. Fits the NR + linear basis (docs/SCOPE_candidates.md §"Spike")."""
    with SERIES.open() as f:
        s = {(r["region"], int(r["taxation_year"]), r["basis"]): float(r["core_share"])
             for r in csv.DictReader(f)}
    assert abs(s[("edmonton", 2022, "nr_linear")] - 0.60) <= 0.01
    assert s[("edmonton", 2010, "nr_linear")] <= 0.72


def test_fir_corrections_are_in_the_committed_series():
    """The four kept-as-printed anomalies are corrected from FIR's EA schedule
    (DECISIONS 2026-10-02, superseding 2026-09-28's "kept as printed"): Airdrie
    NR (taxation 2016) moves Calgary nr by -1.9 pp, Sturgeon NR (2000) moves
    Edmonton nr by +2.4 pp. Each corrected row names what was printed."""
    with SERIES.open() as f:
        rows = {(r["region"], int(r["taxation_year"]), r["basis"]): r for r in csv.DictReader(f)}
    assert abs(float(rows[("calgary", 2016, "nr")]["core_share"]) - 0.9187) <= 0.0005
    # 0.7619 until 2026-10-02, when Entwistle and Wabamun were summed into Parkland.
    assert abs(float(rows[("edmonton", 2000, "nr")]["core_share"]) - 0.7601) <= 0.0005
    assert "airdrie nr (printed 0)" in rows[("calgary", 2016, "nr")]["basis_note"]
    assert "sturgeon nr_incl_railway (printed 647,603,090)" in rows[("edmonton", 2000, "nr")]["basis_note"]
    assert "corrected" not in rows[("edmonton", 2001, "nr")]["basis_note"]


def test_corrections_table_carries_firs_values():
    """data/corrections.csv holds FIR's value for each class, from the committed
    fir_long.csv, and keeps a different printed value alongside."""
    fir = {}
    for r in csv.DictReader(open(REPO / "data/processed/fir_long.csv", newline="")):
        fir[(int(r["fir_year"]), r["muni_id"], r["line_code"])] = int(float(r["value"] or 0))
    rows = list(csv.DictReader(open(REPO / "data/corrections.csv", newline="")))
    assert len(rows) == 6
    for c in rows:
        y = int(c["report_year"])
        assert int(c["corrected_value"]) == sum(fir[(y, c["muni_id"], line)]
                                                for line in c["fir_lines"].split("+"))
        assert int(c["corrected_value"]) != int(c["printed_value"]) and c["evidence"]


def test_apply_corrections_replaces_and_refuses_a_stale_printed_value(tmp_path):
    reg = regions(tmp_path, REGION)
    found, _ = bss.member_values(long(2014, "Core City", nr=60) + long(2014, "Ring County", nr=0), reg)
    fix = [{"report_year": "2014", "muni_id": "ring", "class": "nr",
            "printed_value": "0", "corrected_value": "40"}]
    assert bss.apply_corrections(found, fix) == {(2014, "ring", "nr"): 0}
    assert found[(2014, "ring")]["nr"] == 40
    with pytest.raises(bss.BuildError, match="expects printed"):
        bss.apply_corrections(found, fix)  # the value is now 40, not the printed 0


CONT = [("core", "r", "core", "CORE CITY"), ("ring", "r", "ring", "RING COUNTY"),
        ("other", "r", "ring", "OTHER TOWN")]


def cont_rows(ring_nr, other_nr=100):
    """One report year per ring value; core 1000, zero linear/railway/M&E."""
    rows = []
    for i, v in enumerate(ring_nr):
        y = 2011 + i
        for name, nr in (("Core City", 1000), ("Ring County", v), ("Other Town", other_nr)):
            rows += long(y, name, nr=nr, nr_linear=0, nr_railway=0, nr_cogen_me=0, me=0)
    return rows


@pytest.mark.parametrize("ring_nr, year, why", [
    ([100, 250, 105, 110], 2012, "spiked and reverted"),
    ([100, 0, 105, 110], 2012, "dropped to zero"),
    ([100, 105, 110, 250], 2014, "jumped in the newest year"),
])
def test_continuity_flags_an_anomaly(tmp_path, monkeypatch, ring_nr, year, why):
    reg = regions(tmp_path, CONT)
    found, years = bss.member_values(cont_rows(ring_nr), reg)
    monkeypatch.setattr(bss, "KNOWN_ANOMALIES", set())
    with pytest.raises(bss.BuildError, match=f"\\({year}, 'ring'\\).*{why}"):
        bss.check_continuity(found, years, reg)
    monkeypatch.setattr(bss, "KNOWN_ANOMALIES", {(year, "ring")})
    bss.check_continuity(found, years, reg)   # known: logged, not raised


def test_continuity_passes_steady_growth_and_small_members(tmp_path, monkeypatch):
    reg = regions(tmp_path, CONT)
    monkeypatch.setattr(bss, "KNOWN_ANOMALIES", set())
    # +30% a year stays under SPIKE_DEV; a step up that holds is not a revert.
    for ring in ([100, 130, 169, 220], [100, 100, 250, 260]):
        found, years = bss.member_values(cont_rows(ring), reg)
        bss.check_continuity(found, years, reg)
    # A 1-unit member tripling moves the share far less than MIN_SHARE_PP.
    found, years = bss.member_values(cont_rows([100, 100, 100, 100], other_nr=1), reg)
    found[(2012, "other")]["nr"] = 3
    bss.check_continuity(found, years, reg)
    # The core is never flagged: its movement is what the share measures.
    found, years = bss.member_values(cont_rows([100, 100, 100, 100]), reg)
    found[(2012, "core")]["nr"] = 2000
    bss.check_continuity(found, years, reg)


def test_continuity_fails_on_a_known_anomaly_that_no_longer_fires(tmp_path, monkeypatch):
    reg = regions(tmp_path, CONT)
    found, years = bss.member_values(cont_rows([100, 105, 110, 115]), reg)
    monkeypatch.setattr(bss, "KNOWN_ANOMALIES", {(2012, "ring")})
    with pytest.raises(bss.BuildError, match="no longer fire.*2012, 'ring'"):
        bss.check_continuity(found, years, reg)


LONG = REPO / "data/processed/equalized_long.csv"
# Absorbed: dissolved into a member, summed in as a part (decision 8).
# NOT_MEMBER: every other municipality that stops appearing before the newest
# report, as vanished_names() normalizes it (dissolved into, or renamed to, a
# non-member).
ABSORBED = {"BLACKIE": "foothills", "ENTWISTLE": "parkland", "WABAMUN": "parkland",
            "NEW SAREPTA": "leduc_county"}
NOT_MEMBER = {
    "BADLANDS", "BARON", "BIRCH HILL", "BLACK DIAMOND", "BOTHA", "BURDETT", "CAROLINE",
    "CEREAL", "CROWSNEST PAS", "DERWENT", "DEWBERRY", "EAST PEACE", "EDMONTON BEACH",
    "EVANSBURG", "FERINTOSH", "GADSBY", "GALAHAD", "GLEICHEN", "GRANDE CACHE", "GRANUM",
    "HALKIRK", "HILLSPRING", "HYTHE", "JASPER MUNCIPALITY", "JASPER PARK", "JASPER TOWNSITE",
    "KINUSO", "LAKELAND", "LAVOY", "MIRROR", "NAKAMUM PARK", "NEW NORWAY", "NEW RAINBOW LAKE",
    "NOT REDWOOD MEADOWS INCORPORATED TOWNSITE REDWOOD MEADOWS ADMIN SOC", "PLAMOND",
    "PLAMONDON", "REDWOOD MEADOWS", "REG MUN WOOD BUFFALO", "SANGUDO", "STROME", "TILLEY",
    "TORRINGTON", "TOWNSITE REDWOOD MEADOWS", "TURNER VALLEY", "WAKATENAU", "WANHAM",
    "WARSPITE", "WHITE GULL", "WILLINGDON", "YOUNGSTON",
    "",  # Improvement District No. 349 (dissolved into the M.D. of Bonnyville, 2021)
}


def vanished_names(rows, regions):
    """Names last printed before the newest report, minus rows a member's
    alias or part already matches. Type words are stripped so "Village of X" and "X" are one name."""
    def key(s):
        s = re.sub(r"\b(CITY|TOWN|VILLAGE|SUMMER VILLAGE|S V|SV|COUNTY|MUNICIPAL DISTRICT|M D|MD|"
                   r"SPECIAL AREAS?|IMPROVEMENT DISTRICT|I D|OF|NO|THE|REG MUN|"
                   r"REGIONAL MUNICIPALITY|MUNICIPALITY|AND)\b", " ", s.upper().replace(".", " "))
        return " ".join(re.sub(r"[^A-Z ]", " ", s).split())
    aliases = {a for r in regions for a in r["aliases"]}
    last = {}
    for r in rows:
        if bss.norm(r["muni_name_raw"]) in aliases:
            continue
        k = key(r["muni_name_raw"])
        last[k] = max(last.get(k, 0), int(r["report_year"]))
    newest = max(last.values())
    return {k for k, y in last.items() if y < newest}


def test_every_vanished_municipality_is_classified():
    """A municipality that dissolves into a member must be summed into it
    (decision 8). Phase 1 missed four until 2026-10-02 (Edmonton nr -0.22 pp in
    1998). A new report year that drops a municipality fails here until it is
    classified."""
    if not LONG.exists():
        # Gitignored (4 MB); it is rebuilt only locally, which is where this can fire.
        pytest.skip("no data/processed/equalized_long.csv (run src/parse_equalized.py)")
    regions = bss.load_regions(REPO / "data/regions.csv")
    rows = list(csv.DictReader(LONG.open()))
    assert vanished_names(rows, regions) == NOT_MEMBER


def test_absorbed_villages_are_parts_of_their_member_and_in_the_crosswalk():
    regions = bss.load_regions(REPO / "data/regions.csv")
    by_id = {r["muni_id"]: r for r in regions}
    for village, mid in ABSORBED.items():
        assert any(village in p for p in by_id[mid]["parts"]), (village, mid)
    xw = {(r["muni_id"], r["csd_name"].upper()) for r in csv.DictReader((REPO / "data/csd_crosswalk.csv").open())
          if r["relation"] == "absorbed"}
    assert xw == {(m, v) for v, m in ABSORBED.items()}
