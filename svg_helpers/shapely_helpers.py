def make_path(points, closed=False) -> str:
    """Make an svg path value from a list of (x, y) points."""
    result = []
    iterator = iter(points)
    for x, y in iterator:
        result.append(f"M{x},{y}")
        break
    for x, y in iterator:
        result.append(f"L{x},{y}")
    if closed:
        result.append("Z")
    return "".join(result)


def make_path_from_shapely_polygon(polygon) -> str:
    """Make an svg path value for both the exterior and interior rings
    of a polygon.

    Note: this doesn't check or change the orientation of the
    rings. If the exterior is clockwise and an interior is clockwise,
    that will not show up as a hole in the polygon unless the
    fill-rule is also set to "evenodd".

    If you need to ensure that the polygon is properly oriented, use the [orient method in shapely](https://shapely.readthedocs.io/en/stable/manual.html#shapely.geometry.polygon.orient)

    """
    result = make_path(polygon.exterior.coords, closed=True)
    for interior in polygon.interiors:
        result += make_path(interior.coords, closed=True)
    return result


def make_paths_from_shape(shape) -> list:
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
        return [make_path([(shape.x, shape.y)], closed=True)]
    elif geom_type == "MultiPoint":
        return [make_path([(p.x, p.y)], closed=True) for p in shape.geoms]
    elif geom_type == "LineString":
        return [make_path(shape.coords, closed=False)]
    elif geom_type == "LinearRing":
        return [make_path(shape.coords, closed=True)]
    elif geom_type == "MultiLineString":
        return [make_path(l.coords, closed=False) for l in shape.geoms]
    elif geom_type == "Polygon":
        return [make_path_from_shapely_polygon(shape)]
    elif geom_type == "MultiPolygon":
        return [make_path_from_shapely_polygon(p) for p in shape.geoms]
    elif geom_type == "GeometryCollection":
        result = []
        for sub_shape in shape.geoms:
            result.extend(make_paths_from_shape(sub_shape))
        return result
    else:  # pragma: no cover. Here any case any new geometries get invented?
        raise ValueError(f"{shape} has unknown geom_type {geom_type!r}")
