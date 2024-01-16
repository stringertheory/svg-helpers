import pytest
import shapely
import svg_helpers


def test_create_tag_from_point():
    svg = svg_helpers.create_svg(width=90, height=90)
    point = shapely.Point(1.5, 1.5)
    svg_helpers.create_tag_from_shape(svg, point)
    assert svg.to_string() == (
        '<svg width="90" height="90"><g><path d="M1.5,1.5Z"/></g></svg>'
    )


def test_create_tag_from_linestring():
    svg = svg_helpers.create_svg(width=90, height=90)
    line = shapely.LineString([(45, 45), (80, 45), (80, 10)])
    svg_helpers.create_tag_from_shape(svg, line)
    assert svg.to_string() == (
        '<svg width="90" height="90">'
        '<g><path d="M45.0,45.0L80.0,45.0L80.0,10.0"/></g>'
        "</svg>"
    )


def test_create_tag_from_linearring():
    svg = svg_helpers.create_svg(width=90, height=90)
    ring = shapely.LinearRing([(45, 45), (80, 45), (80, 10)])
    svg_helpers.create_tag_from_shape(svg, ring)
    assert svg.to_string() == (
        '<svg width="90" height="90">'
        '<g><path d="M45.0,45.0L80.0,45.0L80.0,10.0L45.0,45.0Z"/></g>'
        "</svg>"
    )


def test_create_tag_from_polygon():
    svg = svg_helpers.create_svg(width=90, height=90)
    polygon = shapely.Polygon([(45, 45), (80, 45), (80, 10)])
    svg_helpers.create_tag_from_shape(svg, polygon)
    assert svg.to_string() == (
        '<svg width="90" height="90">'
        '<g><path d="M45.0,45.0L80.0,45.0L80.0,10.0L45.0,45.0Z"/></g>'
        "</svg>"
    )


def test_create_tag_from_multipoint():
    svg = svg_helpers.create_svg(width=90, height=90)
    points = shapely.MultiPoint([[0.0, 0.0], [1.0, 2.0]])
    svg_helpers.create_tag_from_shape(svg, points)
    assert svg.to_string() == (
        '<svg width="90" height="90">'
        '<g><path d="M0.0,0.0Z"/><path d="M1.0,2.0Z"/></g>'
        "</svg>"
    )


def test_create_tag_from_multilinestring():
    svg = svg_helpers.create_svg(width=90, height=90)
    lines = shapely.MultiLineString([[[0, 0], [1, 2]], [[4, 4], [5, 6]]])
    svg_helpers.create_tag_from_shape(svg, lines)
    assert svg.to_string() == (
        '<svg width="90" height="90">'
        '<g><path d="M0.0,0.0L1.0,2.0"/><path d="M4.0,4.0L5.0,6.0"/></g>'
        "</svg>"
    )


def test_create_tag_from_multipolygon():
    svg = svg_helpers.create_svg(width=90, height=90)
    polygons = shapely.MultiPolygon(
        [
            (
                [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)],
                [[(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)]],
            ),
            ([(45, 45), (80, 45), (80, 10)], []),
        ]
    )
    svg_helpers.create_tag_from_shape(svg, polygons)
    assert svg.to_string() == (
        '<svg width="90" height="90">'
        '<g><path d="M0.0,0.0L0.0,1.0L1.0,1.0L1.0,0.0L0.0,0.0Z'
        'M0.1,0.1L0.1,0.2L0.2,0.2L0.2,0.1L0.1,0.1Z"/>'
        '<path d="M45.0,45.0L80.0,45.0L80.0,10.0L45.0,45.0Z"/></g>'
        "</svg>"
    )


def test_create_tag_from_geometry_collection():
    svg = svg_helpers.create_svg(width=90, height=90)
    collection = shapely.GeometryCollection(
        [
            shapely.Point(51, -1),
            shapely.LineString([(52, -1), (49, 2)]),
        ]
    )
    svg_helpers.create_tag_from_shape(svg, collection)
    assert svg.to_string() == (
        '<svg width="90" height="90"><g>'
        '<path d="M51.0,-1.0Z"/>'
        '<path d="M52.0,-1.0L49.0,2.0"/>'
        "</g></svg>"
    )


def test_create_tag_from_non_shapely_geometry():
    svg = svg_helpers.create_svg(width=90, height=90)
    rect = svg_helpers.create_tag("rect", svg, x=0, y=0, width=1, height=1)
    with pytest.raises(TypeError, match=r"(?=.*expected)(?=.*got)"):
        svg_helpers.create_tag_from_shape(svg, rect)


def test_create_tag_from_empty_shapely_geometry():
    svg = svg_helpers.create_svg(width=90, height=90)
    point = shapely.Point()
    svg_helpers.create_tag_from_shape(svg, point)
    assert svg.to_string() == (
        '<svg width="90" height="90"><g><path d=""/></g></svg>'
    )


def test_polygon_with_holes():
    svg = svg_helpers.create_svg(width=500, height=500)
    big = shapely.Point(100, 100).buffer(100)
    small = shapely.Point(125, 100).buffer(50)
    small2 = shapely.Point(50, 150).buffer(20)
    holey_donut = big.difference(small).difference(small2)
    svg_helpers.create_tag_from_shape(svg, holey_donut, fill="red")
