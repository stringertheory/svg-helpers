"""Make an SVG with Inkscape-specific namespaces and layer metadata.

Inkscape uses XML namespaces (`inkscape:` and `sodipodi:`) for layer
info, label names, etc. These attribute names contain colons, so they
can't be passed as Python kwargs — use the `attrib=` dict form (or
`**{...}` unpack).

"""

import svg_helpers

svg = svg_helpers.make_svg(
    width=200,
    height=200,
    **{
        "xmlns:inkscape": "http://www.inkscape.org/namespaces/inkscape",
        "xmlns:sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.0.dtd",
    },
)

# A background layer; Inkscape treats <g> with inkscape:groupmode="layer"
# as a top-level layer in its UI.
background = svg.add_element(
    "g",
    id="layer-bg",
    attrib={
        "inkscape:groupmode": "layer",
        "inkscape:label": "Background",
    },
)
background.add_element(
    "rect", x=0, y=0, width=200, height=200, fill="lightblue"
)

foreground = svg.add_element(
    "g",
    id="layer-fg",
    attrib={
        "inkscape:groupmode": "layer",
        "inkscape:label": "Foreground",
    },
)
foreground.add_element("circle", cx=100, cy=100, r=50, fill="orange")

svg.save("make_for_inkscape.svg")
