# SVG helpers

Tools to help make [SVG](https://en.wikipedia.org/wiki/SVG) graphics
with python.

## Install

```bash
pip install svg-helpers
```

## Getting started

The goal is to be as close as is practical to writing
[SVG](https://developer.mozilla.org/en-US/docs/Web/SVG) directly in
python.

Start with `make_svg` then add elements with `add_element`. All
elements have the `add_element` method so they can be nested.
  
<!-- [[[cog
def example(name, alt):
    cog.outl("```python")
    cog.outl(open(f"examples/{name}.py").read().strip())
    cog.outl("```")
    cog.outl("")
    cog.outl(
        f"![{alt}](https://raw.githubusercontent.com/"
        f"stringertheory/svg-helpers/main/examples/{name}.svg)"
    )
]]] -->
<!-- [[[end]]] -->

<!-- [[[cog example("japan", "Japan flag") ]]] -->
```python
import svg_helpers

width = 150
height = width * 2 / 3
r = height * 3 / 10

svg = svg_helpers.make_svg(width=width, height=height)
group = svg.add_element("g")
group.add_element(
    "rect", width=width, height=height, fill="white", stroke="#eee"
)
group.add_element("circle", cx=width / 2, cy=height / 2, r=r, fill="#bc002d")
svg.save("japan.svg")
```

![Japan flag](https://raw.githubusercontent.com/stringertheory/svg-helpers/main/examples/japan.svg)
<!-- [[[end]]] -->

Though with something as simple as this, consider just using f-string
formatting. It can sometimes be difficult to get the quotes right,
though.

```python
print(f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <g>
    <rect width="{width}" height="{height}" fill="white" stroke="#eee" />
    <circle cx="{width/2}" cy="{height/2}" r="{r}" fill="#bc002d" />
  </g>
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

<!-- [[[cog example("banana", "Banana text example") ]]] -->
```python
from svg_helpers import make_svg

width = 500
height = 100
noun = "banana"

svg = make_svg(width=width, height=height)
svg.add_from_string("""
<style>
  .small {
    font: italic 24px serif;
  }
  .small > tspan {
    font: bold 20px sans-serif;
    fill: red;
  }
</style>
""")
svg.add_element(
    "rect", width=width, height=height, fill="white", stroke="#eee"
)
svg.add_from_string(
    f'<text x="{width / 2}" y="{height / 2}" text-anchor="middle" class="small">'
    f"You are <tspan>not</tspan> a {noun}!"
    "</text>"
)
svg.save("banana.svg")
```

![Banana text example](https://raw.githubusercontent.com/stringertheory/svg-helpers/main/examples/banana.svg)
<!-- [[[end]]] -->

## Shapes from shapely

If you have [shapely](https://shapely.readthedocs.io) installed, you
can pass any geometry directly to `add_shape` and it'll be drawn as
a `<path>` (or a group of paths for compound shapes):

<!-- [[[cog example("circle", "Circle from shapely") ]]] -->
```python
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
```

![Circle from shapely](https://raw.githubusercontent.com/stringertheory/svg-helpers/main/examples/circle.svg)
<!-- [[[end]]] -->

For shapes with many points, pass `precision=N` to round coordinates
and strip trailing zeros:

```python
svg.add_shape(big_polygon, precision=2, fill="red")
```

## Multi-line text

`add_text` is a convenience for laying out multi-line text using
`<tspan>` children, with `vertical_align` of `"top"`, `"middle"`, or
`"bottom"`:

<!-- [[[cog example("text", "Multi-line text example") ]]] -->
```python
from svg_helpers import make_svg

svg = make_svg(width=300, height=200)
svg.add_element("rect", width=300, height=200, fill="white", stroke="#eee")
svg.add_text(
    "first line\nsecond line\nthird line",
    x=150,
    y=100,
    vertical_align="middle",
    text_anchor="middle",
    font_family="sans-serif",
    font_size=20,
)
svg.save("text.svg")
```

![Multi-line text example](https://raw.githubusercontent.com/stringertheory/svg-helpers/main/examples/text.svg)
<!-- [[[end]]] -->

## Alternatives

This library is really just a few functions that wrap the standard
library `xml.etree`. It doesn't check that what you produce is
actually valid SVG.

If you want something more fully-featured:

- [svg.py](https://github.com/orsinium-labs/svg.py)
- [drawsvg](https://github.com/cduck/drawsvg)
- [svg_ultralight](https://github.com/ShayHill/svg_ultralight)
- [svgwrite](https://github.com/mozman/svgwrite/)
- [vsketch](https://github.com/abey79/vsketch)

## Goals

- Friendly syntax that's as close as is practical to writing SVG
  directly.
- No dependencies. Can import just about anywhere, and other projects
  can import it without importing fifteen billion other packages.

## License

[MIT](LICENSE).
