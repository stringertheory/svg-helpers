import svg_helpers

width = 600
height = 60
n_shapes = 10

svg = svg_helpers.make_svg(width=width, height=height)
defs = svg.add_element("defs")

# Orange to pink gradient
grad = defs.add_element(
    "linearGradient", id="grad", x1="0%", y1="0%", x2="100%", y2="0%"
)
grad.add_element("stop", offset="0%", stop_color="#ff8a3d")
grad.add_element("stop", offset="100%", stop_color="#ff3d96")

# Drop shadow
shadow = defs.add_element(
    "filter", id="shadow", x="-50%", y="-50%", width="200%", height="200%"
)
shadow.add_element(
    "feGaussianBlur", in_="SourceAlpha", stdDeviation=2, result="blur"
)
shadow.add_element("feOffset", in_="blur", dx=2, dy=2, result="offset")
merge = shadow.add_element("feMerge")
merge.add_element("feMergeNode", in_="offset")
merge.add_element("feMergeNode", in_="SourceGraphic")

# Reusable element
exemplar = defs.add_element("g", id="exemplar")
exemplar.add_element(
    "rect",
    x=-12,
    y=-12,
    width=24,
    height=24,
    fill="url(#grad)",
    filter="url(#shadow)",
)
exemplar.add_element(
    "animateTransform",
    attributeName="transform",
    type="rotate",
    from_="0",
    to="360",
    dur="6s",
    repeatCount="indefinite",
)

svg.add_element("rect", fill="#82c8e5", width="600", height=60)

# Use "use" to tile exemplar
for i in range(n_shapes):
    svg.add_element(
        "use",
        href="#exemplar",
        x=30 + i * (width - 60) / (n_shapes - 1),
        y=height / 2,
    )

svg.save("banner.svg")
