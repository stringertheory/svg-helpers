from __future__ import annotations

import copy as _copy
from typing import Any
from xml.etree import ElementTree

from svg_helpers.shapely_helpers import make_paths_from_shape

# SVG elements whose inter-child whitespace is rendered as a literal
# space character per the XML default whitespace rules. Indenting
# inside one of these shifts visible layout (e.g. a half-space per
# chunk under text-anchor="middle"), so pretty-printing must leave
# their contents untouched. From SVG 1.1 §10.10 ("Text content
# elements") plus `foreignObject` (whose contents are non-SVG markup
# where whitespace also matters).
PRESERVE_INNER_WHITESPACE_TAGS = frozenset(
    {"text", "tspan", "textPath", "tref", "altGlyph", "foreignObject"}
)

_XML_SPACE_ATTR = "{http://www.w3.org/XML/1998/namespace}space"


def _local_tag(tag):
    """Strip a Clark-notation namespace prefix from a tag name."""
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def _preserve_inner_whitespace(elem):
    if _local_tag(elem.tag) in PRESERVE_INNER_WHITESPACE_TAGS:
        return True
    # xml:space="preserve" is the spec-defined escape hatch — check
    # both the Clark-notation form (used by the parser) and the bare
    # form (used by direct kwargs).
    return (
        elem.get(_XML_SPACE_ATTR) == "preserve"
        or elem.get("xml:space") == "preserve"
    )


def _indent_preserving_text(tree, space="  ", level=0):
    """Like ``xml.etree.ElementTree.indent`` but does not insert
    whitespace inside elements whose layout depends on character data
    (text, tspan, textPath, foreignObject, ...) or that opt out via
    ``xml:space="preserve"``.

    """
    if not len(tree):
        return

    indentations = ["\n" + level * space]

    def walk(elem, level):
        if _preserve_inner_whitespace(elem):
            return

        child_level = level + 1
        try:
            child_indentation = indentations[child_level]
        except IndexError:
            child_indentation = indentations[level] + space
            indentations.append(child_indentation)

        if not elem.text or not elem.text.strip():
            elem.text = child_indentation

        last_child = None
        for child in elem:
            if len(child):
                walk(child, child_level)
            if not child.tail or not child.tail.strip():
                child.tail = child_indentation
            last_child = child

        if last_child is not None and (
            not last_child.tail or not last_child.tail.strip()
        ):
            last_child.tail = indentations[level]

    walk(tree, level)


class Element(ElementTree.Element):
    """Wrapper around `xml.etree.ElementTree.Element` with convenience
    methods for building SVG: `add_element`, `add_from_string`,
    `add_shape`, `from_string`, `from_shape`, `to_string`, `save`.

    Higher-level helpers (multi-line text, etc.) live in
    `svg_helpers.recipes` and are reachable via the `recipes` property:
    `element.recipes.add_text(...)`.

    """

    def __init__(self, tag: str, attrib=None, **attributes):
        combined = {**(attrib or {}), **attributes}
        super().__init__(tag, **self._format_attributes(combined))

    def _format_attributes(self, attributes: dict) -> dict:
        """Replace attributes dictionary with a new one where
        attribute names (keys) and attribute values (values) have been
        formatted by the `format_attribute_name` and
        `format_attribute_value` methods. Attributes whose formatted
        value is `None` are dropped.

        """
        result = {}
        for k, v in attributes.items():
            formatted_value = self.format_attribute_value(v)
            if formatted_value is None:
                continue
            result[self.format_attribute_name(k)] = formatted_value
        return result

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
    def format_attribute_value(value: Any) -> str | None:
        """Convert attribute values to a string suitable for SVG output.

        - `None` returns `None`; the caller drops the attribute. Handy
          for building attribute sets conditionally:
          `add_element("rect", stroke=None if outlined else "black")`.
        - `bool` returns lowercase `"true"` / `"false"` (the XML/SVG
          canonical form).
        - Anything else is `str(value)`. The library does not validate
          that the result is meaningful SVG: `float('nan')` and
          `float('inf')` stringify as `"nan"` / `"inf"`, which most
          renderers will ignore.

        Override the method to format attribute values differently.

        """
        if value is None:
            return None
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def add_element(self, tag_name: str, /, **attributes) -> Element:
        """Add an element as a child to this element. For example:

        ```python3
        parent.add_element("circle", cx=150, cy=100, r=60)
        ```

        Will add <circle cx="150" cy="100" r="60" /> as a child of the
        parent element.

        `tag_name` is positional-only so that a kwarg literally named
        `tag_name` (e.g. for an SVG/HTML attribute of that name) doesn't
        collide with the parameter.

        """
        sub_element = type(self)(tag_name, **attributes)
        self.append(sub_element)
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
    def from_shape(cls, shape, /, *, precision=None, **attributes) -> Element:
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
        self.append(sub_element)
        return sub_element

    def add_shape(self, shape, /, *, precision=None, **attributes) -> Element:
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
        self.append(sub_element)
        return sub_element

    @property
    def recipes(self):
        """Opt-in higher-level helpers bound to this element as parent.
        See `svg_helpers.recipes` for available recipes.

        """
        # Lazy import to avoid the circular: recipes.py imports Element.
        from svg_helpers.recipes import _RecipeAccessor

        return _RecipeAccessor(self)

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
            # The custom indenter mutates text/tail in place. Snapshot
            # those two fields per node and restore in `finally` so
            # that calling to_string doesn't change the tree. Saving
            # like this is is faster than deepcopy, but not
            # thread-safe for concurrent reads of the same tree.
            saved = [(el, el.text, el.tail) for el in self.iter()]
            try:
                _indent_preserving_text(self)
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
        # newline="" disables platform newline translation so saved
        # files use \n everywhere — Windows otherwise rewrites \n to \r\n
        # on disk
        with open(filename, "w", encoding="utf-8", newline="") as outfile:
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
