from lxml import etree


class svg(etree.ElementBase):
    def to_string(self, encoding="unicode", pretty=False):
        return etree.tostring(self, encoding=encoding, pretty_print=pretty)


def format_item(key, value):
    return (key.rstrip("_").replace("_", "-"), str(value))


def format_attributes(attributes):
    return dict(format_item(k, v) for k, v in attributes.items())


def make_svg(**attributes):
    return svg(**format_attributes(attributes))


def add_element(tag_name, parent, **attributes):
    return etree.SubElement(parent, tag_name, **format_attributes(attributes))


def make_path(points, closed=False):
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


def make_path_from_shapely_polygon(polygon):
    result = make_path(polygon.exterior.coords, closed=True)
    for interior in polygon.interiors:
        result += make_path(interior.coords, closed=True)
    return result


def make_paths_from_shape(shape):
    try:
        geom_type = shape.geom_type
    except AttributeError:
        raise TypeError(f"expected a Shapely geometry, got {type(shape)}")

    if shape.is_empty:
        return [""]
    elif geom_type == "Point":
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
        for shape in shape.geoms:
            result.extend(make_paths_from_shape(shape))
        return result
    else:  # pragma: no cover. Here any case any new geometries get invented?
        raise ValueError(f"{shape} has unknown geom_type {geom_type!r}")


def add_shape(parent, shape, **attributes):
    group = add_element("g", parent, **attributes)
    for path in make_paths_from_shape(shape):
        add_element("path", group, d=path)
    return group
