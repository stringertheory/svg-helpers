import pytest
import shapely
import svg_helpers


def test_add_element_from_point():
    svg = svg_helpers.make_svg(width=90, height=90)
    point = shapely.Point(1.5, 1.5)
    svg.add_shape(point)
    assert svg.to_string() == (
        '<svg width="90" height="90"><g><path d="M1.5,1.5Z" /></g></svg>'
    )


def test_add_element_from_linestring():
    svg = svg_helpers.make_svg(width=90, height=90)
    line = shapely.LineString([(45, 45), (80, 45), (80, 10)])
    svg.add_shape(line)
    assert svg.to_string() == (
        '<svg width="90" height="90">'
        '<g><path d="M45.0,45.0L80.0,45.0L80.0,10.0" /></g>'
        "</svg>"
    )


def test_add_element_from_linearring():
    svg = svg_helpers.make_svg(width=90, height=90)
    ring = shapely.LinearRing([(45, 45), (80, 45), (80, 10)])
    svg.add_shape(ring)
    assert svg.to_string() == (
        '<svg width="90" height="90">'
        '<g><path d="M45.0,45.0L80.0,45.0L80.0,10.0L45.0,45.0Z" /></g>'
        "</svg>"
    )


def test_add_element_from_polygon():
    svg = svg_helpers.make_svg(width=90, height=90)
    polygon = shapely.Polygon([(45, 45), (80, 45), (80, 10)])
    svg.add_shape(polygon)
    assert svg.to_string() == (
        '<svg width="90" height="90">'
        '<g><path d="M45.0,45.0L80.0,45.0L80.0,10.0L45.0,45.0Z" /></g>'
        "</svg>"
    )


def test_add_element_from_multipoint():
    svg = svg_helpers.make_svg(width=90, height=90)
    points = shapely.MultiPoint([[0.0, 0.0], [1.0, 2.0]])
    svg.add_shape(points)
    assert svg.to_string() == (
        '<svg width="90" height="90"><g>'
        '<path d="M0.0,0.0Z" />'
        '<path d="M1.0,2.0Z" />'
        "</g></svg>"
    )


def test_add_element_from_multilinestring():
    svg = svg_helpers.make_svg(width=90, height=90)
    lines = shapely.MultiLineString([[[0, 0], [1, 2]], [[4, 4], [5, 6]]])
    svg.add_shape(lines)
    assert svg.to_string() == (
        '<svg width="90" height="90"><g>'
        '<path d="M0.0,0.0L1.0,2.0" />'
        '<path d="M4.0,4.0L5.0,6.0" />'
        "</g></svg>"
    )


def test_add_element_from_multipolygon():
    svg = svg_helpers.make_svg(width=90, height=90)
    polygons = shapely.MultiPolygon(
        [
            (
                [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)],
                [[(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)]],
            ),
            ([(45, 45), (80, 45), (80, 10)], []),
        ]
    )
    svg.add_shape(polygons)
    assert svg.to_string() == (
        '<svg width="90" height="90"><g>'
        '<path d="M0.0,0.0L0.0,1.0L1.0,1.0L1.0,0.0L0.0,0.0Z'
        'M0.1,0.1L0.1,0.2L0.2,0.2L0.2,0.1L0.1,0.1Z" />'
        '<path d="M45.0,45.0L80.0,45.0L80.0,10.0L45.0,45.0Z" />'
        "</g></svg>"
    )


def test_add_element_from_geometry_collection():
    svg = svg_helpers.make_svg(width=90, height=90)
    collection = shapely.GeometryCollection(
        [
            shapely.Point(51, -1),
            shapely.LineString([(52, -1), (49, 2)]),
        ]
    )
    svg.add_shape(collection)
    assert svg.to_string() == (
        '<svg width="90" height="90"><g>'
        '<path d="M51.0,-1.0Z" />'
        '<path d="M52.0,-1.0L49.0,2.0" />'
        "</g></svg>"
    )


def test_add_element_from_non_shapely_geometry():
    svg = svg_helpers.make_svg(width=90, height=90)
    rect = svg.add_element("rect", x=0, y=0, width=1, height=1)
    with pytest.raises(TypeError, match=r"(?=.*expected)(?=.*got)"):
        svg.add_shape(rect)


def test_add_element_from_empty_shapely_geometry():
    svg = svg_helpers.make_svg(width=90, height=90)
    point = shapely.Point()
    svg.add_shape(point)
    assert svg.to_string() == (
        '<svg width="90" height="90"><g><path d="" /></g></svg>'
    )


def test_polygon_with_holes():
    svg = svg_helpers.make_svg(width=500, height=500)
    big = shapely.Point(100, 100).buffer(100)
    small = shapely.Point(125, 100).buffer(50)
    small2 = shapely.Point(50, 150).buffer(20)
    holey_donut = big.difference(small).difference(small2)
    svg.add_shape(holey_donut, fill="red")
