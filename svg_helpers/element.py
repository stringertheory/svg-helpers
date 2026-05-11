from __future__ import annotations

import copy as _copy
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
        `stroke-width`. A trailing underscore is stripped first to
        allow escaping Python keywords (`class_` becomes `class`).

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
        sub_element = type(self)(tag_name, **attributes)
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

        def factory(tag, attrib_dict):
            # Bypass __init__ formatting for parsed attributes — the
            # names came straight from XML, so they're already in
            # canonical form. Running format_attribute_name on them
            # would silently rewrite e.g. `class_` → `class`.
            element = cls.__new__(cls)
            ElementTree.Element.__init__(element, tag, attrib_dict)
            return element

        parser = ElementTree.XMLParser(
            target=ElementTree.TreeBuilder(element_factory=factory)
        )
        try:
            parser.feed(markup)
            return parser.close()
        except ElementTree.ParseError as exc:
            raise ValueError(f"couldn't parse {markup!r}: {exc}") from exc

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
        sub_element = type(self).from_string(markup)
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
        sub_element = type(self).from_shape(
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
        """Add a `<text>` element with one `<tspan>` per line, laid out
        vertically using `dy` offsets.

        `text` is split on line terminators (`\\n`, `\\r\\n`, `\\r`); a
        single trailing newline is treated as a terminator (no empty
        tspan), but blank lines in the middle are preserved.

        `vertical_align` controls where the text block sits relative to
        the text element's `y` coordinate: `"top"` puts the top of the
        first line at `y`; `"middle"` centers the block on `y`;
        `"bottom"` puts the baseline of the last line at `y`.

        Special characters in `text` (`<`, `>`, `&`, `"`) are escaped
        automatically because tspans are built directly rather than
        parsed from a string.

        """
        # splitlines handles \r, \n, \r\n uniformly and drops a single
        # trailing terminator. Empty input collapses to one empty line.
        lines = text.splitlines() or [""]

        # total height of the text block, in em
        total_height = len(lines) + (len(lines) - 1) * (line_height - 1)

        if vertical_align == "top":
            first_dy = 0.75
        elif vertical_align == "middle":
            first_dy = -total_height / 2 + 0.85
        elif vertical_align == "bottom":
            first_dy = -total_height + 1
        else:
            raise ValueError(
                f"unknown value for vertical_align {vertical_align!r}, "
                "must be 'top', 'middle', or 'bottom'"
            )

        x = attributes.get("x", 0)

        text_element = type(self)("text", **attributes)

        first_tspan = type(self)("tspan", x=x, dy=f"{round(first_dy, 6)}em")
        first_tspan.text = lines[0]
        text_element.add(first_tspan)

        for line in lines[1:]:
            tspan = type(self)("tspan", x=x, dy=f"{round(line_height, 6)}em")
            tspan.text = line
            text_element.add(tspan)

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
            # ElementTree.indent mutates text/tail in place. Snapshot
            # those two fields per node and restore in `finally` so
            # serialization is non-destructive. Faster than deepcopy,
            # but not thread-safe for concurrent reads of the same tree.
            saved = [(el, el.text, el.tail) for el in self.iter()]
            try:
                ElementTree.indent(self)
                return ElementTree.tostring(
                    self,
                    encoding="unicode",
                    method="xml",
                    xml_declaration=xml_declaration,
                    short_empty_elements=short_empty_elements,
                )
            finally:
                for el, text, tail in saved:
                    el.text = text
                    el.tail = tail

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
        """Write the SVG to a file. `filename` may be a path-like
        object or an open text-mode file object with a `.write` method.
        For example:

        ```python3
        svg.save("japan.svg")
        svg.save("compact.svg", pretty=False, xml_declaration=False)
        ```

        """
        content = self.to_string(
            pretty=pretty,
            xml_declaration=xml_declaration,
            short_empty_elements=short_empty_elements,
        )
        if hasattr(filename, "write"):
            filename.write(content)
            return
        with open(filename, "w", encoding="utf-8") as outfile:
            outfile.write(content)

    def __copy__(self) -> Element:
        clone = type(self).__new__(type(self))
        ElementTree.Element.__init__(clone, self.tag, dict(self.attrib))
        clone.text = self.text
        clone.tail = self.tail
        for child in self:
            clone.append(child)
        return clone

    def __deepcopy__(self, memo) -> Element:
        clone = type(self).__new__(type(self))
        ElementTree.Element.__init__(
            clone, self.tag, _copy.deepcopy(self.attrib, memo)
        )
        clone.text = self.text
        clone.tail = self.tail
        for child in self:
            clone.append(_copy.deepcopy(child, memo))
        return clone

    def __str__(self) -> str:
        return self.to_string()
