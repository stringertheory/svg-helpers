from svg_helpers import make_svg

size = 400
noun = "banana"

svg = make_svg(width=size, height=size)
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
svg.add_element("rect", width=size, height=size, fill="white", stroke="#eee")
svg.add_from_string(
    f'<text x="{size / 2}" y="{size / 2}" text-anchor="middle" class="small">'
    f"You are <tspan>not</tspan> a {noun}!"
    "</text>"
)
svg.save("banana.svg")
