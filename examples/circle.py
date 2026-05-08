from pathlib import Path

import shapely

from svg_helpers import make_svg

svg = make_svg(width=200, height=200)
svg.add_element("rect", width=200, height=200, fill="white")

# any shapely geometry: Point, LineString, Polygon, MultiPolygon, ...
circle = shapely.Point(100, 100).buffer(50)
svg.add_shape(circle, fill="none", stroke="black", stroke_width=2)

svg.save(Path(__file__).parent / "circle.svg")
