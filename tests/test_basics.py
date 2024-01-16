import svg_helpers


def test_create():
    svg = svg_helpers.create_svg(width=10, height=10)
    assert svg.to_string() == '<svg width="10" height="10"/>'


def test_create_tag():
    svg = svg_helpers.create_svg(width=10, height=10)
    svg_helpers.create_tag("rect", svg, x=0, y=0, width=1, height=1)
    assert svg.to_string() == (
        '<svg width="10" height="10">'
        '<rect x="0" y="0" width="1" height="1"/>'
        "</svg>"
    )


def test_create_tag_dashed_attributes():
    svg = svg_helpers.create_svg(width=10, height=10)
    svg_helpers.create_tag("circle", svg, cx=0, cy=0, r=1, stroke_width=1)
    assert svg.to_string() == (
        '<svg width="10" height="10">'
        '<circle cx="0" cy="0" r="1" stroke-width="1"/>'
        "</svg>"
    )


def test_create_tag_keyword_attributes():
    svg = svg_helpers.create_svg(width=10, height=10)
    svg_helpers.create_tag("line", svg, x1=0, y1=0, x2=1, y2=1, class_="hi")
    assert svg.to_string() == (
        '<svg width="10" height="10">'
        '<line x1="0" y1="0" x2="1" y2="1" class="hi"/>'
        "</svg>"
    )
