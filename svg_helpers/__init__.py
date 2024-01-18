"""Simple functions for making graphics with svg.

For example, this will make a picture of a Japanese flag:

```python3
import svg_helpers

svg = svg_helpers.make_svg(width=300, height=200)
svg.add_element("rect", width=300, height=200, fill="white")
svg.add_element("circle", cx=150, cy=100, r=60, fill="#bc002d")
print(svg)
```

"""

from svg_helpers.element import Element


def make_svg(**attributes) -> Element:
    """Shorthand for `Element("svg", **attributes)`. Returns a new svg
    element with given attributes. For example:

    ```python3
    svg = make_svg(width=400, height=400, viewBox="0 0 100 100", **{
        "xmlns": "https://www.w3.org/2000/svg",
        "xmlns:inkscape": "https://www.inkscape.org/namespaces/inkscape",
    })
    ```

    """
    return Element("svg", **attributes)
