import math
import random

import shapely

from svg_helpers import make_svg

random.seed(0)

n = 7
r = 50
r2 = math.pi * r / n
svg = make_svg(width=200, height=200, viewBox="-100 -100 200 200")
circles = [shapely.Point(0, 0).buffer(r)]
for i in range(n):
    angle = 2 * math.pi * (i / n)
    x = r * math.cos(angle)
    y = r * math.sin(angle)
    circles.append(shapely.Point(x, y).buffer(r2 * (0.5 + random.random())))

union = shapely.unary_union(circles)
shape = union.exterior.buffer(10)
svg.add_shape(shape, fill_opacity=0.5, stroke="black", precision=1)
svg.save("cloud.svg")
