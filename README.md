# SVG helpers

Tools to help make [SVG](https://en.wikipedia.org/wiki/SVG) graphics
with python.

```bash
pip install svg-helpers
```

```python
import svg_helpers

width = 150
height = width * 2 / 3
r = height * 3 / 10

# this will make a japanese flag:
svg = svg_helpers.make_svg(width=width, height=height)
svg.add_element("rect", width=width, height=height, fill="white", stroke="#eee")
svg.add_element("circle", cx=width/2, cy=height/2, r=r, fill="#bc002d")
print(svg)
```

Though with something as simple as this, consider just using f-string
formatting. It can sometimes be difficult to get the quotes right,
though.

```python
print(f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" fill="white" stroke="#eee" />
  <circle cx="{width/2}" cy="{height/2}" r="{r}" fill="#bc002d" />
</svg>
""")
```

Names always match the SVG names. For example, svg `rect` elements
have an `x` and `y` property, so use `x` and `y` to make a rect.
Underscores in attribute names become dashes (`stroke_width=1` →
`stroke-width="1"`), and a trailing underscore is stripped so you can
escape Python keywords (`class_="hi"` → `class="hi"`).

## Adding raw markup

Adding elements from strings can be helpful for text, especially when
it has `<tspan>` elements in it:

```python
from svg_helpers import make_svg

size = 400
noun = "banana"

svg = make_svg(width=size, height=size)
svg.add_from_string("""
<style>
  .small {
    font: italic 12px serif;
  }
  .small > tspan {
    font: bold 10px sans-serif;
    fill: red;
  }
</style>
""")
svg.add_element("rect", width=size, height=size, fill="white", stroke="#eee")
svg.add_from_string(
    f'<text x="{size/2}" y="{size/2}" class="small">'
    f'You are <tspan>not</tspan> a {noun}!'
    '</text>'
)
print(svg)
```

## Shapes from shapely

If you have [shapely](https://shapely.readthedocs.io) installed, you
can pass any geometry directly to `add_shape` and it'll be drawn as
a `<path>` (or a group of paths for compound shapes):

```python
import shapely
from svg_helpers import make_svg

svg = make_svg(width=200, height=200)
svg.add_element("rect", width=200, height=200, fill="white")

# any shapely geometry: Point, LineString, Polygon, MultiPolygon, ...
circle = shapely.Point(100, 100).buffer(50)
svg.add_shape(circle, fill="none", stroke="black", stroke_width=2)

print(svg)
```

For shapes with many points, pass `precision=N` to round coordinates
and strip trailing zeros:

```python
svg.add_shape(big_polygon, precision=2, fill="red")
```

## Multi-line text

`add_text` is a convenience for laying out multi-line text using
`<tspan>` children, with `vertical_align` of `"top"`, `"middle"`, or
`"bottom"`:

```python
svg.add_text(
    "first line\nsecond line\nthird line",
    x=100, y=100,
    vertical_align="middle",
    font_family="sans-serif",
)
```

## Alternatives

This is really just a few small functions. If you want something more
comprehensive:

- [svg.py](https://github.com/orsinium-labs/svg.py)
- [drawsvg](https://github.com/cduck/drawsvg)
- [svg_ultralight](https://github.com/ShayHill/svg_ultralight)
- [svgwrite](https://github.com/mozman/svgwrite/)
- [vsketch](https://github.com/abey79/vsketch)

## Goals

- friendly syntax that's easy to read and remember. Trying to be as
  close as is practical to simply writing SVG directly.
- no baggage. no dependencies. can import just about anywhere, and
  other projects can import without importing fifteen billion other
  packages.
- low maintenance.

## Anti-goals

- comprehensive: it's ok if there are things missing.
- opinionated: it should not coerce using in a particular way.

## License

[MIT](LICENSE).
