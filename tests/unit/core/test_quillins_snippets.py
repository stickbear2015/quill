"""Tests for Layer 1 snippet placeholder expansion."""

from __future__ import annotations

from quill.core.quillins.snippets import SnippetContext, expand_snippet


def test_plain_text_is_unchanged() -> None:
    result = expand_snippet("hello world", SnippetContext())
    assert result.text == "hello world"
    assert result.cursor == len("hello world")


def test_selection_placeholder_substitutes() -> None:
    result = expand_snippet("```\n${selection}\n```", SnippetContext(selection="code"))
    assert result.text == "```\ncode\n```"


def test_all_known_placeholders_substitute() -> None:
    context = SnippetContext(
        selection="SEL",
        clipboard="CLIP",
        filename="notes.txt",
        date="2024-01-02",
        time="09:30",
    )
    body = "${selection} ${clipboard} ${filename} ${date} ${time}"
    result = expand_snippet(body, context)
    assert result.text == "SEL CLIP notes.txt 2024-01-02 09:30"


def test_cursor_marker_sets_offset_and_is_removed() -> None:
    result = expand_snippet("before${cursor}after", SnippetContext())
    assert result.text == "beforeafter"
    assert result.cursor == len("before")


def test_cursor_offset_accounts_for_earlier_substitution() -> None:
    result = expand_snippet("${selection}${cursor}!", SnippetContext(selection="hello"))
    assert result.text == "hello!"
    assert result.cursor == len("hello")


def test_first_cursor_marker_wins() -> None:
    result = expand_snippet("a${cursor}b${cursor}c", SnippetContext())
    assert result.text == "abc"
    assert result.cursor == 1


def test_unknown_placeholder_is_left_intact() -> None:
    result = expand_snippet("keep ${unknown} token", SnippetContext())
    assert result.text == "keep ${unknown} token"


def test_missing_date_and_time_fall_back_without_crashing() -> None:
    result = expand_snippet("${date} ${time}", SnippetContext())
    assert "${" not in result.text
    assert " " in result.text


def test_empty_selection_yields_empty_substitution() -> None:
    result = expand_snippet("[${selection}]", SnippetContext())
    assert result.text == "[]"


def test_title_placeholder_substitutes() -> None:
    result = expand_snippet("# ${title}", SnippetContext(title="my-notes"))
    assert result.text == "# my-notes"


def test_line_number_placeholder_substitutes() -> None:
    result = expand_snippet("line:${line_number}", SnippetContext(line_number="42"))
    assert result.text == "line:42"


def test_word_at_cursor_placeholder_substitutes() -> None:
    result = expand_snippet("[${word_at_cursor}]", SnippetContext(word_at_cursor="hello"))
    assert result.text == "[hello]"


def test_uuid_placeholder_produces_valid_uuid4() -> None:
    import re
    result = expand_snippet("id:${uuid}", SnippetContext())
    assert result.text.startswith("id:")
    uuid_part = result.text[3:]
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
        uuid_part,
    ), uuid_part


def test_uuid_placeholder_is_fresh_each_call() -> None:
    r1 = expand_snippet("${uuid}", SnippetContext())
    r2 = expand_snippet("${uuid}", SnippetContext())
    assert r1.text != r2.text


def test_new_placeholders_in_combined_body() -> None:
    context = SnippetContext(
        title="report",
        line_number="7",
        word_at_cursor="foo",
    )
    body = "${title}:${line_number}:${word_at_cursor}"
    result = expand_snippet(body, context)
    assert result.text == "report:7:foo"


def test_empty_new_fields_yield_empty_substitution() -> None:
    result = expand_snippet(
        "${title}/${line_number}/${word_at_cursor}", SnippetContext()
    )
    assert result.text == "//"
