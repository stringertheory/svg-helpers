"""Use jinja2 to template parts of an SVG.

It's pretty nice to use jinja for parameterized CSS or markup
fragments, then embed the rendered string into the svg-helpers tree
via `add_from_string` or by setting an element's `.text`.

"""

import jinja2

import svg_helpers

css_template = jinja2.Template("""
.title {
    font: bold {{ size }}px sans-serif;
    fill: {{ color }};
}
""")

text_template = jinja2.Template(
    '<text x="{{ x }}" y="{{ y }}" text-anchor="middle" class="title">'
    "Hello, {{ name }}!"
    "</text>"
)

svg = svg_helpers.make_svg(width=300, height=100)
svg.add_element("rect", width=300, height=100, fill="white", stroke="#eee")

# Render parameterized CSS into a <style> element's text content
style = svg.add_element("style")
style.text = css_template.render(size=28, color="navy")

# Render a parameterized text fragment and embed it as a parsed element
svg.add_from_string(text_template.render(x=150, y=60, name="world"))

svg.save("jinja_templates.svg")
