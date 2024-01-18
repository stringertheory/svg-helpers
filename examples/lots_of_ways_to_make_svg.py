import svg_helpers

# parameters
svg_size = 400
size = 300
pad = (svg_size - size) / 2

# for a lot of graphics, it's easiest to use string formatting
svg_string = f"""
<svg width="{svg_size}" height="{svg_size}">
  <rect x="{pad}" y="{pad}" width="{size}" height="{size}" fill="blue" />
</svg>
"""
print(svg_string)

# the same graphic using the make_svg and add_element functions
svg = svg_helpers.make_svg(width=svg_size, height=svg_size)
svg.add_element("rect", x=pad, y=pad, width=size, height=size, fill="blue")
print(svg)
