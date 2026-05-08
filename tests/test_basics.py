import pytest

import svg_helpers


def test_create():
    svg = svg_helpers.make_svg(width=10, height=10)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" />'
    )


def test_add_element():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect", x=0, y=0, width=1, height=1)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<rect x="0" y="0" width="1" height="1" />'
        "</svg>"
    )


def test_add_element_from_string():
    svg = svg_helpers.make_svg(viewBox="0 0 240 40")
    svg.add_from_string(
        '<text x="1" y="3" class="hi">I <tspan>ain\'t</tspan> a cat!</text>'
    )
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 40">'
        """<text x="1" y="3" class="hi">I <tspan>ain't</tspan> a cat!</text>"""
        "</svg>"
    )


def test_add_element_dashed_attributes():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("circle", cx=0, cy=0, r=1, stroke_width=1)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<circle cx="0" cy="0" r="1" stroke-width="1" />'
        "</svg>"
    )


def test_add_element_keyword_attributes():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("line", x1=0, y1=0, x2=1, y2=1, class_="hi")
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<line x1="0" y1="0" x2="1" y2="1" class="hi" />'
        "</svg>"
    )


def test_add_element_namespaced_attributes():
    svg = svg_helpers.make_svg(
        width=10,
        height=10,
        **{
            "xmlns:inkscape": "http://www.inkscape.org/namespaces/inkscape",
        },
    )
    svg.add_element(
        "g",
        **{
            "inkscape:groupmode": "layer",
        },
    )
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" '
        'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">'
        '<g inkscape:groupmode="layer" />'
        "</svg>"
    )


def test_to_string_from_subelement():
    svg = svg_helpers.make_svg(width=10, height=10)
    rect = svg.add_element("rect", x=0, y=0, width=1, height=1)
    assert rect.to_string() == '<rect x="0" y="0" width="1" height="1" />'


def test_add_element_from_subelement():
    svg = svg_helpers.make_svg(width=10, height=10)
    group = svg.add_element("g")
    group.add_element("rect", x=0, y=0, width=1, height=1)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><g>'
        '<rect x="0" y="0" width="1" height="1" />'
        "</g></svg>"
    )


def test_str_method():
    svg = svg_helpers.make_svg(width=10, height=10)
    assert str(svg) == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" />'
    )


def test_to_string_options():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect", x=0, y=0, width=1, height=1)

    expected = """
<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">
  <rect x="0" y="0" width="1" height="1" />
</svg>
    """.strip()
    assert svg.to_string(pretty=True) == expected

    expected = """
<?xml version='1.0' encoding='utf-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">
  <rect x="0" y="0" width="1" height="1" />
</svg>
    """.strip()
    assert svg.to_string(xml_declaration=True, pretty=True) == expected

    expected = """
<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">
  <rect x="0" y="0" width="1" height="1"></rect>
</svg>
    """.strip()
    assert svg.to_string(short_empty_elements=False, pretty=True) == expected


def test_to_string_pretty_is_idempotent():
    svg = svg_helpers.make_svg(width=10, height=10)
    g = svg.add_element("g")
    g.add_element("rect", x=0, y=0, width=1, height=1)

    first = svg.to_string(pretty=True)
    second = svg.to_string(pretty=True)
    third = svg.to_string(pretty=True)
    assert first == second == third


def test_class_keyword_escape():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("g", class_="layer")
    g = svg.find("g")
    assert g.get("class") == "layer"
    assert "class_" not in g.attrib


def test_from_string_raises_value_error_with_hint():
    with pytest.raises(ValueError, match="quotes"):
        svg_helpers.Element.from_string("<text x=10>hi</text>")


def test_from_string_chains_underlying_parse_error():
    from xml.etree.ElementTree import ParseError

    with pytest.raises(ValueError) as info:
        svg_helpers.Element.from_string("<not-closed>")
    assert isinstance(info.value.__cause__, ParseError)


def test_namespaced_parsing_uses_clark_notation():
    # Document a limitation: when xmlns is declared, ElementTree's parser
    # converts namespaced tags to Clark notation ({uri}localname). The
    # original prefix is not preserved on round-trip — re-serialization
    # generates a fresh prefix (ns0, ns1, ...).
    markup = (
        '<root xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">'
        "<inkscape:layer />"
        "</root>"
    )
    parsed = svg_helpers.Element.from_string(markup)
    layer = list(parsed)[0]
    assert layer.tag == "{http://www.inkscape.org/namespaces/inkscape}layer"
    out = parsed.to_string()
    assert "{http://" not in out  # Clark notation gets resolved on output
    assert "inkscape:layer" not in out  # original prefix not preserved
    assert "layer" in out  # local name survives
