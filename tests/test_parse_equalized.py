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
    words = [w("Municipality", 160, top), w("Residential", 242, top), w("Equipment", 668, top),
             w("Linear", 470, top - 10), w("Co-generating", 600, top - 10)]
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
    # A data row that genuinely prints the typo'd value is left alone.
    b = full({0: 10, 1: 1, 2: 4, 3: 99, 4: 1, 5: 1, 6: 3}, 7)
    words = (header(100) + data_row("Edmonton", a, 130, EDGES_RAIL)
             + data_row("Leduc", b, 140, EDGES_RAIL) + subtotal_row([a, b], 160, EDGES_RAIL))
    rows, _ = pe.parse_pages([words], 2014)
    assert sorted(r["value"] for r in rows if r["class"] == "nr_linear") == [2, 99]


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


# 1998–2004 layout: 4 classes + total, M&E printed LEFT of linear.
EDGES_OLD = [267, 347, 421, 496, 576]


def old_header(top):
    return [w("Municipality", 140, top), w("Residential", 259, top), w("Non", 298, top),
            w("Residential", 348, top), w("Machinery", 409, top - 6), w("Linear", 480, top),
            w("Grand", 545, top), w("Total", 569, top), w("Equipment", 413, top + 6)]


def old_row(name, vals, top):
    """vals: 5 ints (4 classes + total); None prints "-" left of the edge."""
    words = data_row(name, {}, top, EDGES_OLD, name_x0=32)
    for e, v in zip(EDGES_OLD, vals):
        words.append(w("-", e - 10, top, width=3) if v is None else w(f"{v:,}", e, top))
    return words


def test_old_layout_classes_headings_dashes_and_loose_rows():
    # Special Areas sits outside every section (1998); only the grand total covers it.
    sa = [5, 3, 2, 1, 11]
    ed = [100, 60, 20, 10, 190]
    ai = [10, 5, None, 1, 16]
    ei = [1, 1, 0, 1, 3]
    words = old_header(100)
    words += old_row("Special Areas", sa, 130)
    words += data_row("CITIES", {}, 150, EDGES_OLD, name_x0=32)              # a heading
    words += old_row("City of Edmonton", ed, 170)
    words += old_row("City of Airdrie", ai, 180)
    words += data_row("Improvement District No. 13 - Elk", {}, 189, EDGES_OLD, name_x0=32)
    words += old_row("Island", ei, 199)                                        # values on the LAST line
    cities = [e + (a or 0) + i for e, a, i in zip(ed, ai, ei)]
    words += old_row("Total Cities", cities, 220)
    grand = [s + c for s, c in zip(sa, cities)]
    words += old_row("2003 GRAND TOTAL EQUALIZED", grand, 240)
    rows, stats = pe.parse_pages([words], 2003)
    got = {(r["muni_name_raw"], r["class"]): r["value"] for r in rows}
    assert stats["layout"] == "1998-2004" and stats["rows"] == 4
    assert got[("City of Edmonton", "me")] == 20 and got[("City of Edmonton", "nr_linear")] == 10
    assert got[("City of Edmonton", "nr_incl_railway")] == 60
    assert got[("City of Airdrie", "me")] == 0
    assert ("Improvement District No. 13 - Elk Island", "me") in got
    types = {r["muni_name_raw"]: r["muni_type"] for r in rows}
    assert types["City of Edmonton"] == "CITIES" and types["Special Areas"] is None


def test_old_layout_row_outside_every_total_fails():
    words = old_header(100) + old_row("Stray", [1, 1, 1, 1, 4], 130)
    words += old_row("City of Edmonton", [1, 1, 1, 1, 4], 150)
    words += old_row("Total Cities", [1, 1, 1, 1, 4], 170)
    with pytest.raises(pe.ParseError, match="never reconciled"):
        pe.parse_pages([words], 2003)


def test_number_split_into_two_words_is_rejoined():
    # 1999: "7" + "32,059,142" printed as two words with no gap.
    row = [{"text": "7", "x0": 507.0, "x1": 512.0, "top": 1}, {"text": "32,059,142", "x0": 512.2, "x1": 553.0, "top": 1}]
    assert [x["text"] for x in pe._join_split_numbers(row)] == ["732,059,142"]
    apart = [{"text": "7", "x0": 490.0, "x1": 495.0, "top": 1}, row[1]]
    assert len(pe._join_split_numbers(apart)) == 2


def test_old_column_order_is_read_from_the_header_not_assumed():
    # Swap where Linear and Machinery print: the classes must follow.
    hdr = old_header(100)
    for x in hdr:
        if x["text"] == "Linear":
            x["x0"], x["x1"] = 363, 390
        elif x["text"] in ("Machinery", "Equipment"):
            x["x0"], x["x1"] = 451, 490
    rows = pe._rows(hdr)
    assert pe._old_classes(rows, pe._header_bottom(rows)) == [
        "residential_incl_farmland", "nr_incl_railway", "nr_linear", "me", "grand_total"]
