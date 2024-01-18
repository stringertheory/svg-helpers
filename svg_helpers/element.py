from __future__ import annotations

from typing import Any
from xml.etree import ElementTree

from svg_helpers.shapely_helpers import make_paths_from_shape


class Element(ElementTree.Element):
    """Wrapper around `xml.etree.ElementTree.Element`, that adds a few
    convenience methods: `to_string`, `add_element`, and `add_shape`.

    """

    def __init__(self, tag: str, **attributes):
        super().__init__(tag, **self._format_attributes(attributes))

    def _format_attributes(self, attributes: dict) -> dict:
        """Replace attributes dictionary with a new one where
        attribute names (keys) and attribute values (values) have been
        formatted by the `format_attribute_name` and
        `format_attribute_value` methods.

        """
        return {
            self.format_attribute_name(k): self.format_attribute_value(v)
            for k, v in attributes.items()
        }

    @staticmethod
    def format_attribute_name(key: str) -> str:
        """Replace underscores in passed attribute names with dashes
        in the svg element. For example, `stroke_width` becomes
        `stroke-width`.

        Override the method to format attribute names differently.

        """
        return key.rstrip("_").replace("_", "-")

    @staticmethod
    def format_attribute_value(value: Any) -> str:
        """Convert attribute values to string. For example, `10`
        becomes `"10"`.

        Override the method to format attribute values differently.

        """
        return str(value)

    def add_element(self, tag_name: str, **attributes) -> Element:
        """Add an element as a child to this element. For example:

        ```python3
        parent.add_element("circle", cx=150, cy=100, r=60)
        ```

        Will add <circle cx="150" cy="100" r="60" /> as a child of the
        parent element.

        """
        sub_element = Element(tag_name, **attributes)
        self.append(sub_element)
        return sub_element

    def add_shape(self, shape, **attributes) -> Element:
        """Add an element as a child to this element. For example:

        ```python3
        circle = shapely.Point(0, 0).buffer(10)
        parent.add_shape(circle, fill="none", stroke="black")
        ```

        Will add <path d="M ... Z" fill="none" stroke="black" /> as a
        child of the parent element.

        Any type of shapely geometry is accepted.

        """
        group = self.add_element("g", **attributes)
        for path in make_paths_from_shape(shape):
            group.add_element("path", d=path)
        return group

    def to_string(self) -> str:
        """Write the svg as a string."""
        return ElementTree.tostring(self, encoding="unicode")

    def __str__(self) -> str:
        return self.to_string()
