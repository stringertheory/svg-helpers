from __future__ import annotations

from typing import Any, Literal
from xml.etree import ElementTree

from svg_helpers.shapely_helpers import make_paths_from_shape


class Element(ElementTree.Element):
    """Wrapper around `xml.etree.ElementTree.Element`, that adds a few
    convenience methods: `to_string`, `add_element`, and `add_shape`.

    """

    def __init__(self, tag: str, attrib=None, **attributes):
        combined = {**(attrib or {}), **attributes}
        super().__init__(tag, **self._format_attributes(combined))

    def add(self, *args, **kwargs):
        """Alias for Element.append"""
        return super().append(*args, **kwargs)

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
        self.add(sub_element)
        return sub_element

    @classmethod
    def from_string(cls, markup: str) -> Element:
        """Parse markup and return a new Element. Companion to
        `add_from_string` for the times you want the element without
        appending it to a parent. For example:

        ```python3
        text = Element.from_string('<text x="10" y="30">hi</text>')
        ```

        Raises ValueError if the markup can't be parsed.

        """
        parser = ElementTree.XMLParser(
            target=ElementTree.TreeBuilder(element_factory=cls)
        )
        try:
            parser.feed(markup)
            return parser.close()
        except ElementTree.ParseError as exc:
            msg = (
                f"Couldn't parse {markup!r}. "
                "Do you have quotes around attribute values?"
            )
            raise ValueError(msg) from exc

    @classmethod
    def from_shape(cls, shape, *, precision=None, **attributes) -> Element:
        """Build an Element from a shapely geometry: a `<g>` group with
        one `<path>` per sub-shape. For example:

        ```python3
        import shapely
        circle = shapely.Point(0, 0).buffer(10)
        g = Element.from_shape(circle, fill="none", stroke="black")
        ```

        Pass `precision` to round coordinates and strip trailing zeros —
        the output gets noticeably smaller for shapes with many points.

        """
        group = cls("g", **attributes)
        for path in make_paths_from_shape(shape, precision=precision):
            group.add_element("path", d=path)
        return group

    def add_from_string(self, markup: str) -> Element:
        """Add an element parsed from raw markup as a child. Handy for
        content with mixed text and tags (e.g. `<text>` with `<tspan>`),
        where keyword arguments would be awkward. For example:

        ```python3
        parent.add_from_string(
            '<text x="10" y="30">You are <tspan>not</tspan> a banana!</text>'
        )
        ```

        Raises ValueError if the markup can't be parsed.

        """
        sub_element = Element.from_string(markup)
        self.add(sub_element)
        return sub_element

    def add_shape(self, shape, *, precision=None, **attributes) -> Element:
        """Add an element as a child to this element. For example:

        ```python3
        circle = shapely.Point(0, 0).buffer(10)
        parent.add_shape(circle, fill="none", stroke="black")
        ```

        Will add <path d="M ... Z" fill="none" stroke="black" /> as a
        child of the parent element.

        Any type of shapely geometry is accepted.

        """
        sub_element = Element.from_shape(
            shape, precision=precision, **attributes
        )
        self.add(sub_element)
        return sub_element

    def add_text(
        self,
        text: str,
        vertical_align: Literal["bottom", "middle", "top"] = "bottom",
        line_height: float = 1.2,
        **attributes,
    ) -> Element:
        lines = text.split("\n")

        # calculate total height of text block, in em
        total_height = len(lines) + (len(lines) - 1) * (line_height - 1)

        # calculate dy value to use for the first line
        if vertical_align == "top":
            dy = 0.75
        elif vertical_align == "middle":
            dy = -total_height / 2 + 0.85
        elif vertical_align == "bottom":
            dy = -total_height + 1
        else:
            raise ValueError(
                f"unknown value for vertical_align {vertical_align!r}, "
                "must be 'top', 'middle', or 'bottom'"
            )

        # get the x attribute value, to set on each line individually
        x = attributes.get("x", 0)

        text_element = Element("text", **attributes)

        # use the calculated dy for the first line
        for line in lines[:1]:
            text_element.add_from_string(
                f'<tspan x="{x}" dy="{dy}em">{line}</tspan>'
            )

        # the rest of the lines are offset using the line height
        for line in lines[1:]:
            text_element.add_from_string(
                f'<tspan x="{x}" dy="{line_height}em">{line}</tspan>'
            )

        self.add(text_element)
        return text_element

    def to_string(
        self,
        pretty=False,
        xml_declaration=False,
        short_empty_elements=True,
    ) -> str:
        """Generate string representation of the element. All
        subelements are included.

        This is a convenient way of calling `xml.etree.ElementTree.tostring`.

        """
        if pretty:
            ElementTree.indent(self)

        return ElementTree.tostring(
            self,
            encoding="unicode",
            method="xml",
            xml_declaration=xml_declaration,
            short_empty_elements=short_empty_elements,
        )

    def save(
        self,
        filename,
        *,
        pretty=True,
        xml_declaration=True,
        short_empty_elements=True,
    ) -> None:
        """Write the SVG to a file. For example:

        ```python3
        svg.save("japan.svg")
        svg.save("compact.svg", pretty=False, xml_declaration=False)
        ```

        """
        with open(filename, "w", encoding="utf-8") as outfile:
            outfile.write(
                self.to_string(
                    pretty=pretty,
                    xml_declaration=xml_declaration,
                    short_empty_elements=short_empty_elements,
                )
            )

    def __str__(self) -> str:
        return self.to_string()
