import pytest

import svg_helpers


def parse_em(s):
    """Strip the 'em' suffix from a tspan dy attribute and parse as float."""
    return float(s.removesuffix("em"))


def test_add_text_returns_text_element():
    svg = svg_helpers.make_svg(width=100, height=100)
    text = svg.add_text("hi", x=10, y=20)
    assert text.tag == "text"
    assert text.get("x") == "10"
    assert text.get("y") == "20"


def test_add_text_single_line_creates_one_tspan():
    svg = svg_helpers.make_svg(width=100, height=100)
    svg.add_text("hello", x=0, y=10, vertical_align="top")
    text = svg.find("text")
    tspans = text.findall("tspan")
    assert len(tspans) == 1
    assert tspans[0].text == "hello"


def test_add_text_multi_line_creates_one_tspan_per_line():
    svg = svg_helpers.make_svg(width=100, height=100)
    svg.add_text("first\nsecond\nthird", x=0, y=50, vertical_align="top")
    tspans = svg.find("text").findall("tspan")
    assert [t.text for t in tspans] == ["first", "second", "third"]


def test_add_text_x_appears_on_each_tspan():
    # Multi-line text needs x on every tspan to reset the X position;
    # without it, lines would flow left-to-right within the parent <text>.
    svg = svg_helpers.make_svg(width=100, height=100)
    svg.add_text("a\nb\nc", x=42, y=10, vertical_align="top")
    text = svg.find("text")
    assert text.get("x") == "42"
    assert all(tspan.get("x") == "42" for tspan in text.findall("tspan"))


def test_add_text_default_x_is_zero_on_tspans():
    svg = svg_helpers.make_svg(width=100, height=100)
    svg.add_text("hi", y=10, vertical_align="top")
    text = svg.find("text")
    # User didn't pass x, so the <text> has no x attribute,
    # but each tspan still gets x="0" to fix the line starting position.
    assert text.get("x") is None
    assert text.find("tspan").get("x") == "0"


def test_add_text_vertical_align_top_first_dy():
    svg = svg_helpers.make_svg(width=100, height=100)
    svg.add_text("hi", y=10, vertical_align="top")
    first = svg.find("text").find("tspan")
    assert parse_em(first.get("dy")) == pytest.approx(0.75)


def test_add_text_vertical_align_middle_first_dy():
    # For 1 line, total_height=1, so dy = -0.5 + 0.85 = 0.35
    svg = svg_helpers.make_svg(width=100, height=100)
    svg.add_text("hi", y=10, vertical_align="middle")
    first = svg.find("text").find("tspan")
    assert parse_em(first.get("dy")) == pytest.approx(0.35)


def test_add_text_vertical_align_bottom_first_dy_single_line():
    # For 1 line, total_height=1, so dy = -1 + 1 = 0
    svg = svg_helpers.make_svg(width=100, height=100)
    svg.add_text("hi", y=10, vertical_align="bottom")
    first = svg.find("text").find("tspan")
    assert parse_em(first.get("dy")) == pytest.approx(0)


def test_add_text_subsequent_lines_use_line_height():
    svg = svg_helpers.make_svg(width=100, height=100)
    svg.add_text("a\nb\nc", y=10, vertical_align="top", line_height=1.5)
    tspans = svg.find("text").findall("tspan")
    # First line uses the calculated dy (0.75 for top); rest use line_height.
    assert parse_em(tspans[1].get("dy")) == pytest.approx(1.5)
    assert parse_em(tspans[2].get("dy")) == pytest.approx(1.5)


def test_add_text_invalid_vertical_align_raises():
    svg = svg_helpers.make_svg(width=100, height=100)
    with pytest.raises(ValueError, match="vertical_align"):
        svg.add_text("hi", vertical_align="middlish")


def test_add_text_extra_attributes_appear_on_text_element():
    svg = svg_helpers.make_svg(width=100, height=100)
    svg.add_text(
        "hi", x=10, y=20, font_family="serif", fill="red", class_="big"
    )
    text = svg.find("text")
    assert text.get("font-family") == "serif"
    assert text.get("fill") == "red"
    assert text.get("class") == "big"


def test_add_text_escapes_ampersand():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_text("Joe & Jane", x=10, y=20)
    assert svg.find("text").find("tspan").text == "Joe & Jane"
    assert "&amp;" in svg.to_string()


def test_add_text_escapes_lt_gt():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_text("a < b > c", x=0, y=0)
    out = svg.to_string()
    assert "&lt;" in out
    assert "&gt;" in out


def test_add_text_escapes_quotes():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_text('say "hi"', x=0, y=0)
    assert svg.find("text").find("tspan").text == 'say "hi"'


def test_add_text_handles_special_chars_with_newlines():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_text("line1\nline2 with <strong>")
    tspans = svg.find("text").findall("tspan")
    assert len(tspans) == 2
    assert tspans[1].text == "line2 with <strong>"


def test_add_text_trailing_newline_does_not_emit_empty_tspan():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_text("hi\n", x=0, y=0)
    tspans = svg.find("text").findall("tspan")
    assert len(tspans) == 1
    assert tspans[0].text == "hi"


def test_add_text_carriage_return_line_feed():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_text("a\r\nb", x=0, y=0)
    tspans = svg.find("text").findall("tspan")
    assert [t.text for t in tspans] == ["a", "b"]


def test_add_text_blank_line_in_middle_preserved():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_text("a\n\nb", x=0, y=0)
    tspans = svg.find("text").findall("tspan")
    assert [t.text for t in tspans] == ["a", "", "b"]


def test_add_text_has_docstring():
    assert svg_helpers.Element.add_text.__doc__ is not None
    assert len(svg_helpers.Element.add_text.__doc__.strip()) > 20


def test_add_text_dy_does_not_have_float_artifacts():
    # Without rounding, default vertical_align produces a dy of
    # "-1.2000000000000002em" — full float-precision noise.
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_text("a\nb")
    first = svg.find("text").find("tspan")
    assert "0000000000" not in first.get("dy")
