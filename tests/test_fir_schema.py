"""The FIR facts later parsers rely on, pinned against the committed fingerprint
(data/fir_schema.json, from src/fingerprint_fir.py). A re-fetch that changes one
of these turns this file red before any parser reads the new layout blind."""
import csv
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import fetch_fir  # noqa: E402
import fingerprint_fir  # noqa: E402

SCHEMA = json.loads((REPO / "data/fir_schema.json").read_text())
YEARS = range(1994, 2026)


def sheets(year):
    for fname, f in SCHEMA["years"][str(year)].items():
        for sname, s in f.get("sheets", {}).items():
            yield fname, sname, s, SCHEMA["layouts"].get(s.get("layout"), {})


def headers_with_code(year, code):
    return {lay["header"][lay["codes"].index(code)].strip()
            for _, _, _, lay in sheets(year) if code in lay.get("codes", [])}


def test_every_financial_year_has_municipality_rows_for_that_year():
    for y in YEARS:
        assert any(s.get("muni_rows") and str(y) in s["row_years"] for _, _, s, _ in sheets(y)), y


def test_only_the_known_2001_files_carry_another_years_rows():
    stray = {(y, f) for y in YEARS for f, _, s, _ in sheets(y)
             if s.get("row_years") and s["row_years"] != [str(y)]}
    assert stray == {(2001, "2001/EQASSMT 2002.XLS"), (2001, "2001/Mr_col1.XLS"),
                     (2001, "2001/Mr_col2.XLS")}


def test_provincial_transfer_codes_change_meaning_in_2023():
    """Decision 9's lines 1912/1922 (operating/capital) exist only from 2023.
    Before that the split is unconditional (01910) / conditional (01920): a
    different cut, so the two cannot be spliced as one series. 2001's files
    have no code row at all."""
    for y in YEARS:
        if y == 2001:
            assert not headers_with_code(y, "01910") and not headers_with_code(y, "01912")
        elif y >= 2023:
            assert headers_with_code(y, "01912") == {"Provincial Government Operating Transfers"}
            assert headers_with_code(y, "01922") == {"Provincial Government Capital Transfers"}
            assert not headers_with_code(y, "01910") and not headers_with_code(y, "01920")
        else:
            assert headers_with_code(y, "01910") == {"Provincial Government Unconditional Transfers"}
            assert headers_with_code(y, "01920") == {"Provincial Government Conditional Transfers"}
            assert not headers_with_code(y, "01912") and not headers_with_code(y, "01922")


def test_equalized_nr_subtotal_is_published_1997_onward():
    for y in YEARS:
        has = any("Non Residential Subtotal" in lay.get("header", []) for _, _, _, lay in sheets(y))
        assert has == (y >= 1997), y


def test_taxable_assessment_sheet_exists_only_from_2023():
    for y in range(2009, 2026):
        has = any(sname.startswith("MR(2)") for _, sname, _, _ in sheets(y))
        assert has == (y >= 2023), y


def test_every_member_has_a_distinct_fir_code():
    rows = list(csv.DictReader(open(REPO / "data/regions.csv", newline="")))
    codes = [r["fir_code"] for r in rows]
    assert all(fingerprint_fir.MUNI_CODE.match(c) for c in codes)
    assert len(set(codes)) == len(rows)


# --- fetch_fir.classify -----------------------------------------------------

def res(name):
    return {"name": name, "url": f"https://x/{name}"}


def test_classify_names_files_by_kind_and_years():
    out = fetch_fir.classify([res("2025 financial year"), res("2026_Tax_Rates.xlsx"),
                              res("2003-2024 municipal financial data and statistics (ZIP)")])
    assert [e["file"] for e in out] == ["fir_year_2025.xlsx", "fir_tax_rates_2026.xlsx",
                                        "fir_zip_2003_2024.zip"]


def test_classify_fails_on_an_unknown_resource():
    with pytest.raises(fetch_fir.FetchError, match="unrecognised"):
        fetch_fir.classify([res("2025 financial year"), res("FIR manual 2025")])


def test_classify_fails_on_a_year_covered_twice_or_missing():
    with pytest.raises(fetch_fir.FetchError, match="2010"):
        fetch_fir.classify([res("2010 financial year"),
                            res("2009-2016 municipal financial data and statistics (ZIP)")])
    with pytest.raises(fetch_fir.FetchError, match=r"\[2024\]"):
        fetch_fir.classify([res("2023 financial year"), res("2025 financial year")])


# --- fingerprint_fir.fingerprint_sheet --------------------------------------

def test_fingerprint_reads_header_code_row_and_municipality_rows():
    rows = [("Schedule EA", "Equalized Assessment"),
            ("YEAR", "STATUS", "CODE", "MUNICIPALITY", "Linear Subtotal"),
            (None, None, None, "(* Includes AB & SK)", "08265"),
            ("2005", "City", "0003", "AIRDRIE", 1.0),
            ("2005", "City", "0046", "CALGARY", 2.0),
            ("Total", None, None, None, 3.0)]
    assert fingerprint_fir.fingerprint_sheet(rows) == {
        "title": ["Schedule EA | Equalized Assessment"], "header": ["Linear Subtotal"],
        "codes": ["08265"], "muni_rows": 2, "row_years": ["2005"]}


def test_fingerprint_without_a_code_row_does_not_take_a_footer_as_codes():
    rows = [("YEAR", "STATUS", "CODE", "MUNICIPALITY", "GRAND TOTAL"),
            (2001.0, "City", "0003", "AIRDRIE", 1.0),
            ("Total", None, None, None, 1.0)]
    fp = fingerprint_fir.fingerprint_sheet(rows)
    assert fp["codes"] == [] and fp["muni_rows"] == 1 and fp["row_years"] == ["2001"]
