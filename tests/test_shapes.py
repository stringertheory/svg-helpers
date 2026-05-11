import pytest
import shapely

import svg_helpers
from svg_helpers.shapely_helpers import make_path


def test_add_element_from_point():
    svg = svg_helpers.make_svg(width=90, height=90)
    point = shapely.Point(1.5, 1.5)
    svg.add_shape(point)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90">'
        '<g><path d="M1.5,1.5Z" /></g>'
        "</svg>"
    )


def test_add_element_from_linestring():
    svg = svg_helpers.make_svg(width=90, height=90)
    line = shapely.LineString([(45, 45), (80, 45), (80, 10)])
    svg.add_shape(line)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90">'
        '<g><path d="M45.0,45.0L80.0,45.0L80.0,10.0" /></g>'
        "</svg>"
    )


def test_add_element_from_linearring():
    svg = svg_helpers.make_svg(width=90, height=90)
    ring = shapely.LinearRing([(45, 45), (80, 45), (80, 10)])
    svg.add_shape(ring)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90">'
        '<g><path d="M45.0,45.0L80.0,45.0L80.0,10.0L45.0,45.0Z" /></g>'
        "</svg>"
    )


def test_add_element_from_polygon():
    svg = svg_helpers.make_svg(width=90, height=90)
    polygon = shapely.Polygon([(45, 45), (80, 45), (80, 10)])
    svg.add_shape(polygon)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90">'
        '<g><path d="M45.0,45.0L80.0,45.0L80.0,10.0L45.0,45.0Z" /></g>'
        "</svg>"
    )


def test_add_element_from_multipoint():
    svg = svg_helpers.make_svg(width=90, height=90)
    points = shapely.MultiPoint([[0.0, 0.0], [1.0, 2.0]])
    svg.add_shape(points)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90"><g>'
        '<path d="M0.0,0.0Z" />'
        '<path d="M1.0,2.0Z" />'
        "</g></svg>"
    )


def test_add_element_from_multilinestring():
    svg = svg_helpers.make_svg(width=90, height=90)
    lines = shapely.MultiLineString([[[0, 0], [1, 2]], [[4, 4], [5, 6]]])
    svg.add_shape(lines)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90"><g>'
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
        '<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90"><g>'
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
        '<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90"><g>'
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
        '<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90">'
        '<g><path d="" /></g>'
        "</svg>"
    )


def test_polygon_with_holes():
    svg = svg_helpers.make_svg(width=500, height=500)
    big = shapely.Point(100, 100).buffer(100)
    small = shapely.Point(125, 100).buffer(50)
    small2 = shapely.Point(50, 150).buffer(20)
    holey_donut = big.difference(small).difference(small2)
    g = svg.add_shape(holey_donut, fill="red")
    paths = g.findall("path")
    assert len(paths) == 1
    d = paths[0].get("d")
    assert d.startswith("M") and d.endswith("Z")
    assert d.count("M") == 3  # exterior + two holes


def test_precision_rounding():
    svg = svg_helpers.make_svg(width=10, height=10)
    line = shapely.LineString([(1.123456, 2.987654), (3.111, 4.0)])
    svg.add_shape(line, precision=2)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<g><path d="M1.12,2.99L3.11,4" /></g>'
        "</svg>"
    )


def test_precision_strips_trailing_zeros():
    svg = svg_helpers.make_svg(width=10, height=10)
    line = shapely.LineString([(1.0, 2.0), (3.0, 4.0)])
    svg.add_shape(line, precision=2)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<g><path d="M1,2L3,4" /></g>'
        "</svg>"
    )


def test_no_precision_preserves_full_floats():
    svg = svg_helpers.make_svg(width=10, height=10)
    line = shapely.LineString([(1.5, 2.5), (3.5, 4.5)])
    svg.add_shape(line)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<g><path d="M1.5,2.5L3.5,4.5" /></g>'
        "</svg>"
    )


def test_3d_polygon_via_add_shape():
    svg = svg_helpers.make_svg(width=10, height=10)
    poly = shapely.Polygon([(0, 0, 1), (10, 0, 1), (10, 10, 1), (0, 10, 1)])
    svg.add_shape(poly)
    out = svg.to_string()
    assert "0.0,0.0" in out
    assert "10.0,10.0" in out


def test_3d_linestring_via_add_shape():
    svg = svg_helpers.make_svg(width=10, height=10)
    line = shapely.LineString([(1, 2, 3), (4, 5, 6)])
    svg.add_shape(line)
    out = svg.to_string()
    assert "1.0,2.0" in out
    assert "4.0,5.0" in out


def test_3d_geometry_collection_via_add_shape():
    svg = svg_helpers.make_svg(width=10, height=10)
    poly = shapely.Polygon([(0, 0, 1), (10, 0, 1), (10, 10, 1)])
    gc = shapely.GeometryCollection([poly])
    svg.add_shape(gc)
    assert "0.0,0.0" in svg.to_string()


def test_precision_negative_raises_clear_error():
    svg = svg_helpers.make_svg(width=10, height=10)
    line = shapely.LineString([(1.5, 2.5), (3.5, 4.5)])
    with pytest.raises(ValueError, match="precision"):
        svg.add_shape(line, precision=-1)


def test_precision_float_raises_clear_error():
    svg = svg_helpers.make_svg(width=10, height=10)
    line = shapely.LineString([(1.5, 2.5), (3.5, 4.5)])
    with pytest.raises((ValueError, TypeError), match="precision"):
        svg.add_shape(line, precision=2.5)


def test_precision_string_raises_clear_error():
    svg = svg_helpers.make_svg(width=10, height=10)
    line = shapely.LineString([(1.5, 2.5), (3.5, 4.5)])
    with pytest.raises((ValueError, TypeError), match="precision"):
        svg.add_shape(line, precision="2")


def test_make_path_empty_closed_does_not_emit_lone_z():
    # A bare "Z" with no preceding "M" is invalid SVG path syntax.
    result = make_path([], closed=True)
    assert "Z" not in result


def test_multipolygon_with_empty_part_skips_empty():
    # Mixing empty and real shapes inside a collection should not leave
    # empty <path d=""/> nodes for the empty parts.
    svg = svg_helpers.make_svg(width=10, height=10)
    gc = shapely.GeometryCollection(
        [
            shapely.LineString(),
            shapely.Point(1, 2),
            shapely.Polygon(),
        ]
    )
    svg.add_shape(gc)
    paths = svg.find("g").findall("path")
    assert len(paths) == 1
    assert paths[0].get("d") == "M1.0,2.0Z"


def test_subclass_format_propagates_to_from_shape_children():
    class CustomElement(svg_helpers.Element):
        pass

    g = CustomElement._from_shape(shapely.Point(1, 2))
    for child in g:
        assert isinstance(child, CustomElement)


def test_add_shape_shape_as_attribute():
    # The `shape` parameter is positional-only, so passing shape="..."
    # as a kwarg becomes an attribute on the wrapping <g>.
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_shape(shapely.Point(1, 2), shape="circle")
    assert svg.find("g").get("shape") == "circle"


def test_from_shape_shape_as_attribute():
    g = svg_helpers.Element._from_shape(shapely.Point(1, 2), shape="circle")
    assert g.get("shape") == "circle"
