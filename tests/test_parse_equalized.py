"""parse_equalized on synthetic word lists: placement by x-position, not order."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import parse_equalized as pe  # noqa: E402

# Right edges of the 7-class + total columns, railway layout (as in 2014).
EDGES_RAIL = [259, 328, 407, 481, 541, 609, 683, 762]
EDGES_NO_RAIL = [369, 430, 499, 564, 628, 693, 763]


def w(text, x1, top, width=None):
    width = width or 6 * len(text)
    return {"text": text, "x0": x1 - width, "x1": x1, "top": top}


def header(top, rail=True):
    words = [w("Municipality", 160, top), w("Residential", 242, top), w("Equipment", 668, top)]
    if rail:
        words.append(w("Railway", 528, top - 10))
    return words


def data_row(name, values, top, edges, name_x0=98, type_word=None):
    """values: {column_index: int}; missing columns are printed blank."""
    words = []
    if type_word:
        words.append({"text": type_word, "x0": 22, "x1": 40, "top": top})
    x = name_x0
    for part in name.split():
        words.append({"text": part, "x0": x, "x1": x + 6 * len(part), "top": top})
        x += 6 * len(part) + 3
    for i, v in values.items():
        words.append(w(f"{v:,}", edges[i], top))
    return words


def full(vals, n_classes):
    """Complete a {col: value} dict with the grand total in the last column."""
    out = dict(vals)
    out[n_classes] = sum(vals.values())
    return out


def subtotal_row(rows_vals, top, edges, shift=0):
    n = len(edges)
    cols = {i: sum(r.get(i, 0) for r in rows_vals) for i in range(n)}
    return [w(f"{v:,}", edges[i] - shift, top) for i, v in cols.items() if v or i == n - 1] + \
        [{"text": "SUB", "x0": 34, "x1": 50, "top": top},
         {"text": "TOTAL", "x0": 53, "x1": 79, "top": top}]


def page(rows_vals, names, edges, rail=True, extra=()):
    words = header(100, rail)
    top = 130
    for name, vals in zip(names, rows_vals):
        words += data_row(name, vals, top, edges)
        top += 18
    words += subtotal_row(rows_vals, top, edges, shift=4)
    return words + list(extra)


def test_blank_cells_are_placed_by_position_not_order():
    # Beaumont 2014: 6 numbers for 8 columns — farmland and railway present,
    # co-gen and M&E blank. Order-based parsing would shift M&E into co-gen.
    a = full({0: 2_027_302_739, 1: 526_800, 2: 102_582_798, 3: 14_147_840, 6: 78_700}, 7)
    b = full({0: 100, 1: 5, 2: 50, 3: 7, 4: 1, 5: 2, 6: 3}, 7)
    rows, stats = pe.parse_pages([page([a, b], ["Beaumont", "Other"], EDGES_RAIL)], 2014)
    got = {r["class"]: (r["value"], r["was_blank"]) for r in rows if r["muni_name_raw"] == "Beaumont"}
    assert got["me"] == (78_700, False)
    assert got["nr_cogen_me"] == (0, True)
    assert got["nr_railway"] == (0, True)
    assert stats["railway_column"] and stats["rows"] == 2
    assert {r["taxation_year"] for r in rows} == {2013}


def test_layout_without_railway_column():
    a = full({0: 10, 1: 1, 2: 4, 3: 2, 4: 0, 5: 3}, 6)
    b = full({0: 20, 1: 2, 2: 8, 3: 4, 4: 1, 5: 6}, 6)
    rows, stats = pe.parse_pages([page([a, b], ["AIRDRIE", "BEAUMONT"], EDGES_NO_RAIL, rail=False)], 2022)
    assert not stats["railway_column"]
    assert "nr_railway" not in {r["class"] for r in rows}


def test_row_that_does_not_reconcile_fails():
    a = full({0: 10, 1: 1, 2: 4, 3: 2, 4: 1, 5: 1, 6: 3}, 7)
    a[7] += 1
    b = full({0: 10, 1: 1, 2: 4, 3: 2, 4: 1, 5: 1, 6: 3}, 7)
    with pytest.raises(pe.ParseError, match="sum to"):
        pe.parse_pages([page([a, b], ["Edmonton", "Devon"], EDGES_RAIL)], 2014)


def test_value_off_every_column_fails():
    a = full({0: 10, 1: 1, 2: 4, 3: 2, 4: 1, 5: 1, 6: 3}, 7)
    b = full({0: 10, 1: 1, 2: 4, 3: 2, 4: 1, 5: 1, 6: 3}, 7)
    words = page([a, b], ["Edmonton", "Devon"], EDGES_RAIL)
    # one extra named row whose value sits between two columns
    stray = data_row("Leduc", {}, 400, EDGES_RAIL) + [w("5", 450, 400), w("5", 762, 400)]
    with pytest.raises(pe.ParseError):
        pe.parse_pages([words + stray], 2014)


def test_subtotal_that_disagrees_with_its_rows_fails():
    a = full({0: 10, 1: 1, 2: 4, 3: 2, 4: 1, 5: 1, 6: 3}, 7)
    words = header(100) + data_row("Edmonton", a, 130, EDGES_RAIL)
    wrong = dict(a)
    wrong[0] += 5
    wrong[7] += 5
    words += subtotal_row([wrong], 150, EDGES_RAIL)
    with pytest.raises(pe.ParseError, match="reconciles neither"):
        pe.parse_pages([words], 2014)


def test_known_defect_is_corrected_only_in_a_subtotal(monkeypatch):
    a = full({0: 10, 1: 1, 2: 4, 3: 2, 4: 1, 5: 1, 6: 3}, 7)
    words = header(100) + data_row("Edmonton", a, 130, EDGES_RAIL)
    printed = dict(a)
    printed[3] = 99  # the publisher's typo; the row total stays right
    words += subtotal_row([printed], 150, EDGES_RAIL)
    with pytest.raises(pe.ParseError):
        pe.parse_pages([words], 2014)
    monkeypatch.setitem(pe.KNOWN_DEFECTS, (2014, "nr_linear", 99), 2)
    rows, _ = pe.parse_pages([words], 2014)
    assert {r["value"] for r in rows if r["class"] == "nr_linear"} == {2}


def test_wrapped_names_join_below_and_above():
    a = full({0: 10, 1: 1, 2: 4, 3: 2, 4: 1, 5: 1, 6: 3}, 7)
    b = full({0: 20, 1: 2, 2: 8, 3: 4, 4: 2, 5: 2, 6: 6}, 7)
    words = header(100)
    words += data_row("Wood Buffalo,", a, 130, EDGES_RAIL)
    words += data_row("Regional Municipality", {}, 140, EDGES_RAIL)
    words += data_row("Of", {}, 149, EDGES_RAIL)
    words += data_row("Redwood Meadows", {}, 175, EDGES_RAIL)   # wraps ABOVE its numbers
    words += data_row("Townsite", b, 200, EDGES_RAIL)
    words += subtotal_row([a, b], 230, EDGES_RAIL)
    rows, _ = pe.parse_pages([words], 2013)
    names = {r["muni_name_raw"] for r in rows}
    assert names == {"Wood Buffalo, Regional Municipality Of", "Redwood Meadows Townsite"}


def test_numbers_inside_names_are_not_values():
    a = full({0: 10, 1: 1, 2: 4, 3: 2, 4: 1, 5: 1, 6: 3}, 7)
    words = header(100) + data_row("Foothills No. 31, M.D. Of", a, 130, EDGES_RAIL)
    words += data_row("I.D. No. 9", a, 148, EDGES_RAIL)
    words += subtotal_row([a, a], 170, EDGES_RAIL)
    rows, _ = pe.parse_pages([words], 2014)
    assert {r["muni_name_raw"] for r in rows} == {"Foothills No. 31, M.D. Of",
                                                  "I.D. No. 9"}


def test_image_only_document_is_an_error_not_an_empty_result():
    with pytest.raises(pe.ParseError, match="image-only"):
        pe.parse_pages([[], []], 2009)
