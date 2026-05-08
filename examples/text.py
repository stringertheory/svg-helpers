from pathlib import Path

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
svg.save(Path(__file__).parent / "text.svg")
