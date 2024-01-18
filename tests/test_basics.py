import svg_helpers


def test_create():
    svg = svg_helpers.make_svg(width=10, height=10)
    assert svg.to_string() == '<svg width="10" height="10" />'


def test_add_element():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect", x=0, y=0, width=1, height=1)
    assert svg.to_string() == (
        '<svg width="10" height="10">'
        '<rect x="0" y="0" width="1" height="1" />'
        "</svg>"
    )


def test_add_element_from_string():
    svg = svg_helpers.make_svg(viewBox="0 0 240 40")
    svg.add_from_string(
        '<text x="1" y="3" class="hi">'
        "I <tspan>ain't</tspan> a cat!"
        "</text>"
    )
    assert svg.to_string() == (
        '<svg viewBox="0 0 240 40">'
        """<text x="1" y="3" class="hi">I <tspan>ain't</tspan> a cat!</text>"""
        "</svg>"
    )


def test_add_element_dashed_attributes():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("circle", cx=0, cy=0, r=1, stroke_width=1)
    assert svg.to_string() == (
        '<svg width="10" height="10">'
        '<circle cx="0" cy="0" r="1" stroke-width="1" />'
        "</svg>"
    )


def test_add_element_keyword_attributes():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("line", x1=0, y1=0, x2=1, y2=1, class_="hi")
    assert svg.to_string() == (
        '<svg width="10" height="10">'
        '<line x1="0" y1="0" x2="1" y2="1" class="hi" />'
        "</svg>"
    )


def test_add_element_namespaced_attributes():
    svg = svg_helpers.make_svg(
        width=10,
        height=10,
        **{
            "xmlns:inkscape": "http://www.inkscape.org/namespaces/inkscape",
        }
    )
    svg.add_element(
        "g",
        **{
            "inkscape:groupmode": "layer",
        }
    )
    assert svg.to_string() == (
        '<svg width="10" height="10" '
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
    rect = group.add_element("rect", x=0, y=0, width=1, height=1)
    assert svg.to_string() == (
        '<svg width="10" height="10"><g>'
        '<rect x="0" y="0" width="1" height="1" />'
        "</g></svg>"
    )
