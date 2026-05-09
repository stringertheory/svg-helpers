import svg_helpers

width = 150
height = width * 2 / 3
r = height * 3 / 10

svg = svg_helpers.make_svg(width=width, height=height)
svg.add_element(
    "rect", width=width, height=height, fill="white", stroke="#eee"
)
svg.add_element("circle", cx=width / 2, cy=height / 2, r=r, fill="#bc002d")
svg.save("japan.svg")
