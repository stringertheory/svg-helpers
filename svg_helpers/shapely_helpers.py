def make_path(points, closed=False, precision=None) -> str:
    """Make an svg path value from a list of (x, y) points.

    If `precision` is given, coordinates are rounded to that many decimal
    places and trailing zeros are stripped (so 80.0 with precision=2 prints
    as "80", not "80.00").

    """
    if precision is None:
        result = []
        iterator = iter(points)
        for x, y in iterator:
            result.append(f"M{x},{y}")
            break
        for x, y in iterator:
            result.append(f"L{x},{y}")
    else:

        def f(v):
            s = f"{v:.{precision}f}"
            return s.rstrip("0").rstrip(".") if "." in s else s

        result = []
        iterator = iter(points)
        for x, y in iterator:
            result.append(f"M{f(x)},{f(y)}")
            break
        for x, y in iterator:
            result.append(f"L{f(x)},{f(y)}")
    if closed:
        result.append("Z")
    return "".join(result)


def make_path_from_shapely_polygon(polygon, precision=None) -> str:
    """Make an svg path value for both the exterior and interior rings
    of a polygon.

    Note: this doesn't check or change the orientation of the
    rings. If the exterior is clockwise and an interior is clockwise,
    that will not show up as a hole in the polygon unless the
    fill-rule is also set to "evenodd".

    If you need to ensure that the polygon is properly oriented, use the [orient method in shapely](https://shapely.readthedocs.io/en/stable/manual.html#shapely.geometry.polygon.orient)

    """
    result = make_path(
        polygon.exterior.coords, closed=True, precision=precision
    )
    for interior in polygon.interiors:
        result += make_path(interior.coords, closed=True, precision=precision)
    return result


def make_paths_from_shape(shape, precision=None) -> list:
    """Make a list of svg path values that will draw a geometry."""
    try:
        geom_type = shape.geom_type
    except AttributeError as exc:
        raise TypeError(
            f"expected a Shapely geometry, got {type(shape)}"
        ) from exc

    if shape.is_empty:
        return [""]

    if geom_type == "Point":
        return [
            make_path([(shape.x, shape.y)], closed=True, precision=precision)
        ]
    elif geom_type == "MultiPoint":
        return [
            make_path([(p.x, p.y)], closed=True, precision=precision)
            for p in shape.geoms
        ]
    elif geom_type == "LineString":
        return [make_path(shape.coords, closed=False, precision=precision)]
    elif geom_type == "LinearRing":
        return [make_path(shape.coords, closed=True, precision=precision)]
    elif geom_type == "MultiLineString":
        return [
            make_path(line.coords, closed=False, precision=precision)
            for line in shape.geoms
        ]
    elif geom_type == "Polygon":
        return [make_path_from_shapely_polygon(shape, precision=precision)]
    elif geom_type == "MultiPolygon":
        return [
            make_path_from_shapely_polygon(p, precision=precision)
            for p in shape.geoms
        ]
    elif geom_type == "GeometryCollection":
        result = []
        for sub_shape in shape.geoms:
            result.extend(
                make_paths_from_shape(sub_shape, precision=precision)
            )
        return result
    else:  # pragma: no cover. Here any case any new geometries get invented?
        raise ValueError(f"{shape} has unknown geom_type {geom_type!r}")
