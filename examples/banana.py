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
