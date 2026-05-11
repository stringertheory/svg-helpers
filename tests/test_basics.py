import copy
import io

import pytest

import svg_helpers


def test_create():
    svg = svg_helpers.make_svg(width=10, height=10)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" />'
    )


def test_add_element():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect", x=0, y=0, width=1, height=1)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<rect x="0" y="0" width="1" height="1" />'
        "</svg>"
    )


def test_add_element_from_string():
    svg = svg_helpers.make_svg(viewBox="0 0 240 40")
    svg.add_from_string(
        '<text x="1" y="3" class="hi">I <tspan>ain\'t</tspan> a cat!</text>'
    )
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 40">'
        """<text x="1" y="3" class="hi">I <tspan>ain't</tspan> a cat!</text>"""
        "</svg>"
    )


def test_add_element_dashed_attributes():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("circle", cx=0, cy=0, r=1, stroke_width=1)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<circle cx="0" cy="0" r="1" stroke-width="1" />'
        "</svg>"
    )


def test_add_element_keyword_attributes():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("line", x1=0, y1=0, x2=1, y2=1, class_="hi")
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<line x1="0" y1="0" x2="1" y2="1" class="hi" />'
        "</svg>"
    )


def test_add_element_namespaced_attributes():
    svg = svg_helpers.make_svg(
        width=10,
        height=10,
        **{
            "xmlns:inkscape": "http://www.inkscape.org/namespaces/inkscape",
        },
    )
    svg.add_element(
        "g",
        **{
            "inkscape:groupmode": "layer",
        },
    )
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" '
        'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">'
        '<g inkscape:groupmode="layer" />'
        "</svg>"
    )


def test_to_string_from_subelement():
    svg = svg_helpers.make_svg(width=10, height=10)
    rect = svg.add_element("rect", x=0, y=0, width=1, height=1)
    assert rect.to_string() == '<rect x="0" y="0" width="1" height="1" />'


def test_add_element_from_subelement():
    svg = svg_helpers.make_svg(width=10, height=10)
    group = svg.add_element("g")
    group.add_element("rect", x=0, y=0, width=1, height=1)
    assert svg.to_string() == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><g>'
        '<rect x="0" y="0" width="1" height="1" />'
        "</g></svg>"
    )


def test_str_method():
    svg = svg_helpers.make_svg(width=10, height=10)
    assert str(svg) == (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" />'
    )


def test_to_string_options():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect", x=0, y=0, width=1, height=1)

    expected = """
<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">
  <rect x="0" y="0" width="1" height="1" />
</svg>
    """.strip()
    assert svg.to_string(pretty=True) == expected

    expected = """
<?xml version='1.0' encoding='utf-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">
  <rect x="0" y="0" width="1" height="1" />
</svg>
    """.strip()
    assert svg.to_string(xml_declaration=True, pretty=True) == expected

    expected = """
<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">
  <rect x="0" y="0" width="1" height="1"></rect>
</svg>
    """.strip()
    assert svg.to_string(short_empty_elements=False, pretty=True) == expected


def test_to_string_pretty_is_idempotent():
    svg = svg_helpers.make_svg(width=10, height=10)
    g = svg.add_element("g")
    g.add_element("rect", x=0, y=0, width=1, height=1)

    first = svg.to_string(pretty=True)
    second = svg.to_string(pretty=True)
    third = svg.to_string(pretty=True)
    assert first == second == third


def test_class_keyword_escape():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("g", class_="layer")
    g = svg.find("g")
    assert g.get("class") == "layer"
    assert "class_" not in g.attrib


def test_from_string_raises_value_error_with_hint():
    # The error message includes the underlying parser diagnostic so
    # the user can tell unquoted attributes apart from e.g. malformed
    # tags or multiple root elements.
    with pytest.raises(ValueError, match="not well-formed"):
        svg_helpers.Element.from_string("<text x=10>hi</text>")


def test_from_string_chains_underlying_parse_error():
    from xml.etree.ElementTree import ParseError

    with pytest.raises(ValueError) as info:
        svg_helpers.Element.from_string("<not-closed>")
    assert isinstance(info.value.__cause__, ParseError)


def test_save_writes_file_with_defaults(tmp_path):
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect", x=0, y=0, width=1, height=1)
    target = tmp_path / "out.svg"
    svg.save(target)
    contents = target.read_text(encoding="utf-8")
    assert contents.startswith("<?xml")  # xml_declaration default is True
    assert "\n  <rect" in contents  # pretty default is True


def test_save_can_override_defaults(tmp_path):
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect", x=0, y=0, width=1, height=1)
    target = tmp_path / "compact.svg"
    svg.save(target, pretty=False, xml_declaration=False)
    contents = target.read_text(encoding="utf-8")
    assert not contents.startswith("<?xml")
    assert "\n" not in contents  # no indentation, no trailing newline


def test_namespaced_parsing_uses_clark_notation():
    # Document a limitation: when xmlns is declared, ElementTree's parser
    # converts namespaced tags to Clark notation ({uri}localname). The
    # original prefix is not preserved on round-trip — re-serialization
    # generates a fresh prefix (ns0, ns1, ...).
    markup = (
        '<root xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">'
        "<inkscape:layer />"
        "</root>"
    )
    parsed = svg_helpers.Element.from_string(markup)
    layer = list(parsed)[0]
    assert layer.tag == "{http://www.inkscape.org/namespaces/inkscape}layer"
    out = parsed.to_string()
    assert "{http://" not in out  # Clark notation gets resolved on output
    assert "inkscape:layer" not in out  # original prefix not preserved
    assert "layer" in out  # local name survives


def test_from_string_error_message_contains_underlying_cause():
    # Multi-root failure used to wrongly suggest "quotes around values".
    with pytest.raises(ValueError) as info:
        svg_helpers.Element.from_string("<g/><g/>")
    msg = str(info.value)
    assert "junk" in msg.lower() or "document" in msg.lower()


def test_from_string_empty_input_error_message():
    with pytest.raises(ValueError) as info:
        svg_helpers.Element.from_string("")
    msg = str(info.value)
    # Should not give the misleading "quotes" hint for empty input.
    assert "no element" in msg.lower() or "empty" in msg.lower()


def test_from_string_does_not_rewrite_underscore_attr_names():
    # Parsed XML attribute names are already in canonical form;
    # format_attribute_name (kwargs-style) must not run on them.
    e = svg_helpers.Element.from_string(
        '<rect class_="foo" data_value_="1" />'
    )
    assert e.get("class_") == "foo"
    assert e.get("data_value_") == "1"


def test_pretty_does_not_mutate_text():
    svg = svg_helpers.make_svg(width=10, height=10)
    g = svg.add_element("g")
    g.add_element("rect")
    assert g.text is None
    svg.to_string(pretty=True)
    assert g.text is None


def test_pretty_then_compact_round_trip():
    svg = svg_helpers.make_svg(width=10, height=10)
    g = svg.add_element("g")
    g.add_element("rect")
    fresh_compact = svg.to_string(pretty=False)
    svg.to_string(pretty=True)  # used to permanently inject whitespace
    assert svg.to_string(pretty=False) == fresh_compact


def test_save_does_not_mutate_tree(tmp_path):
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect")
    expected_compact = svg.to_string(pretty=False)
    svg.save(tmp_path / "out.svg")  # default pretty=True
    assert svg.to_string(pretty=False) == expected_compact


def test_save_to_string_io():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect")
    buf = io.StringIO()
    svg.save(buf, pretty=False, xml_declaration=False)
    assert "<svg" in buf.getvalue()
    assert "<rect" in buf.getvalue()


def test_save_to_path_object(tmp_path):
    import pathlib

    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect")
    target = pathlib.Path(tmp_path) / "out.svg"
    svg.save(target)
    assert "<rect" in target.read_text()


def test_copy_preserves_subclass():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect")
    clone = copy.copy(svg)
    assert isinstance(clone, svg_helpers.Element)
    assert clone.to_string() == svg.to_string()


def test_deepcopy_preserves_subclass():
    svg = svg_helpers.make_svg(width=10, height=10)
    g = svg.add_element("g")
    g.add_element("rect")
    clone = copy.deepcopy(svg)
    assert isinstance(clone, svg_helpers.Element)
    for descendant in clone.iter():
        assert isinstance(descendant, svg_helpers.Element)
    assert clone.to_string() == svg.to_string()


def test_deepcopy_is_independent():
    svg = svg_helpers.make_svg(width=10, height=10)
    rect = svg.add_element("rect", fill="red")
    clone = copy.deepcopy(svg)
    rect.set("fill", "blue")
    assert clone.find("rect").get("fill") == "red"


def test_subclass_format_propagates_to_add_element_children():
    class CamelCaseElement(svg_helpers.Element):
        @staticmethod
        def format_attribute_name(key):
            return key.rstrip("_")  # don't transform underscores

    svg = CamelCaseElement("svg")
    svg.add_element("rect", stroke_width=1)
    assert svg.find("rect").get("stroke_width") == "1"


def test_add_element_returns_subclass_type():
    class MyElement(svg_helpers.Element):
        pass

    root = MyElement("svg")
    child = root.add_element("g")
    assert isinstance(child, MyElement)


def test_readme_xlink_href_invariant():
    # The README claims **dict and attrib=dict produce identical output
    # for non-Python-identifier attribute names.
    a = svg_helpers.make_svg(width=10, height=10)
    a.add_element("use", **{"xlink:href": "#circle"})
    b = svg_helpers.make_svg(width=10, height=10)
    b.add_element("use", attrib={"xlink:href": "#circle"})
    assert a.to_string() == b.to_string()


def test_add_element_tag_name_as_attribute():
    # tag_name is positional-only, so a tag-name="..." attribute can be
    # passed as a kwarg without colliding with the parameter.
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect", tag_name="trick")
    assert svg.find("rect").get("tag-name") == "trick"


def test_none_attribute_is_dropped():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("rect", stroke=None, fill="red")
    rect = svg.find("rect")
    assert "stroke" not in rect.attrib
    assert rect.get("fill") == "red"


def test_bool_true_becomes_lowercase_true():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("animate", repeatCount=True)
    assert svg.find("animate").get("repeatCount") == "true"


def test_bool_false_becomes_lowercase_false():
    svg = svg_helpers.make_svg(width=10, height=10)
    svg.add_element("animate", repeatCount=False)
    assert svg.find("animate").get("repeatCount") == "false"


def test_pretty_does_not_indent_inside_text():
    # XML default whitespace rules: indentation inside <text> renders as
    # a literal space, shifting visible layout. The custom indenter must
    # leave text-content children adjacent.
    svg = svg_helpers.make_svg(width=10, height=10)
    text = svg.add_element("text")
    text.add_element("tspan").text = "A"
    text.add_element("tspan").text = "B"
    assert "</tspan><tspan>" in svg.to_string(pretty=True)


def test_pretty_does_not_indent_inside_textpath():
    svg = svg_helpers.make_svg(width=10, height=10)
    text = svg.add_element("text")
    textpath = text.add_element("textPath", href="#p")
    textpath.add_element("tspan").text = "X"
    textpath.add_element("tspan").text = "Y"
    assert "</tspan><tspan>" in svg.to_string(pretty=True)


def test_pretty_respects_xml_space_preserve():
    # The escape hatch lets users opt any element out of indenting,
    # including ones outside the hardcoded text-content list.
    svg = svg_helpers.make_svg(width=10, height=10)
    custom = svg.add_element("future-element", **{"xml:space": "preserve"})
    custom.add_element("child").text = "A"
    custom.add_element("child").text = "B"
    assert "</child><child>" in svg.to_string(pretty=True)


def test_pretty_still_indents_normal_elements():
    svg = svg_helpers.make_svg(width=10, height=10)
    g = svg.add_element("g")
    g.add_element("rect")
    out = svg.to_string(pretty=True)
    assert "\n  <g>" in out
    assert "\n    <rect" in out


def test_pretty_on_childless_element_is_unchanged():
    # The indenter must early-return on a leaf — otherwise it would set
    # the element's .text to indentation whitespace, breaking output.
    rect = svg_helpers.Element("rect", width=1, height=1)
    assert rect.to_string(pretty=True) == '<rect width="1" height="1" />'


def test_pretty_handles_namespaced_text_content_elements():
    # Tags parsed from XML come back in Clark notation ({uri}local) —
    # the preserve list still matches them so layout is not shifted.
    # (The serializer prepends a generated `nsN:` prefix on output.)
    svg = svg_helpers.Element.from_string(
        '<svg xmlns="http://www.w3.org/2000/svg">'
        "<text><tspan>A</tspan><tspan>B</tspan></text>"
        "</svg>"
    )
    out = svg.to_string(pretty=True)
    assert "A</ns0:tspan><ns0:tspan>B" in out
