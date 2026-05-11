"""Higher-level conveniences for common SVG patterns. Recipes are
opinionated about how SVG looks (font metrics, layout, etc.) — unlike
core, which is mechanism-only.

Reach recipes via `element.recipes.add_<name>(...)` for the common
add-to-parent case, or import the underlying `make_<name>` factory
directly for explicit composition.

Recipes are an opt-in grab-bag: idiosyncratic, may change, no stability
promise. If you depend on one and want it stable, copy it into your
project.

"""

from __future__ import annotations

from typing import Literal

from svg_helpers.element import Element

# Empirical dy offsets (in em) for make_text's vertical_align modes.
# Assume typical sans-serif font metrics; display fonts or unusual
# scripts may misalign visibly.
_FIRST_LINE_DY_TOP_EM = 0.75
_FIRST_LINE_DY_MIDDLE_OFFSET_EM = 0.85


def make_text(
    text: str,
    /,
    vertical_align: Literal["top", "middle", "bottom"] = "bottom",
    line_height: float = 1.2,
    *,
    element_class: type[Element] = Element,
    **attributes,
) -> Element:
    """Build a `<text>` element with one `<tspan>` per line, laid out
    vertically using `dy` offsets. The returned element is not attached
    to any parent — for the common build-and-attach case, use
    `parent.recipes.add_text(...)`.

    `text` is split on line terminators (`\\n`, `\\r\\n`, `\\r`); a
    single trailing newline is treated as a terminator (no empty
    tspan), but blank lines in the middle are preserved.

    `vertical_align` controls where the text block sits relative to the
    text element's `y` coordinate: `"top"` puts the top of the first
    line at `y`; `"middle"` centers the block on `y`; `"bottom"` puts
    the baseline of the last line at `y`.

    `element_class` is the class used to construct the `<text>` and
    `<tspan>` elements; pass a subclass of `Element` to propagate
    `format_attribute_name` / `format_attribute_value` overrides to
    the recipe-built elements. The accessor path
    (`parent.recipes.add_text(...)`) passes `type(parent)` here
    automatically.

    Special characters in `text` (`<`, `>`, `&`, `"`) are escaped
    automatically because tspans are built directly rather than parsed
    from a string.

    """
    lines = text.splitlines() or [""]

    total_height = len(lines) + (len(lines) - 1) * (line_height - 1)

    if vertical_align == "top":
        first_dy = _FIRST_LINE_DY_TOP_EM
    elif vertical_align == "middle":
        first_dy = -total_height / 2 + _FIRST_LINE_DY_MIDDLE_OFFSET_EM
    elif vertical_align == "bottom":
        first_dy = -total_height + 1
    else:
        raise ValueError(
            f"unknown value for vertical_align {vertical_align!r}, "
            "must be 'top', 'middle', or 'bottom'"
        )

    x = attributes.get("x", 0)

    text_element = element_class("text", **attributes)

    first_tspan = element_class("tspan", x=x, dy=f"{round(first_dy, 6)}em")
    first_tspan.text = lines[0]
    text_element.append(first_tspan)

    for line in lines[1:]:
        tspan = element_class("tspan", x=x, dy=f"{round(line_height, 6)}em")
        tspan.text = line
        text_element.append(tspan)

    return text_element


class _RecipeAccessor:
    """Bound accessor for the recipes module. Don't instantiate
    directly — get one via `element.recipes`.

    """

    __slots__ = ("_parent",)

    def __init__(self, parent: Element):
        self._parent = parent

    def add_text(self, *args, **kwargs) -> Element:
        """Build a multi-line text element and append it to the parent.
        See `make_text` for details.

        Propagates the parent's class as `element_class` so subclass
        overrides of `format_attribute_*` reach the recipe-built
        `<text>` and `<tspan>` children.

        """
        kwargs.setdefault("element_class", type(self._parent))
        element = make_text(*args, **kwargs)
        self._parent.append(element)
        return element
