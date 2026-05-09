import shapely

from svg_helpers import make_svg

svg = make_svg(width=500, height=100)
svg.add_element("rect", width=500, height=100, fill="white")

# any shapely geometry: Point, LineString, Polygon, MultiPolygon, ...
circle_a = shapely.Point(225, 50).buffer(30)
circle_b = shapely.Point(275, 50).buffer(30)
shape = circle_a.union(circle_b)
svg.add_shape(
    shape, fill="aqua", stroke="navy", stroke_width=5, stroke_linejoin="round"
)

svg.save("circle.svg")
