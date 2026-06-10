from __future__ import annotations

import json

import quill.core.publishing as publishing
import quill.core.publishing_clients as publishing_clients
from quill.core.publishing import PublishingConnectionProfile
from quill.core.publishing_providers import AUTH_METHOD_APP_PASSWORD


class _FakeResponse:
    def __init__(self, payload: object) -> None:
        self._payload = payload
        self.headers: dict[str, str] = {}

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_browse_publishing_content_returns_posts_and_pages(
    monkeypatch,
) -> None:
    calls: list[str] = []

    def _urlopen(request, **_kwargs):
        calls.append(request.full_url)
        if "/posts?" in request.full_url:
            return _FakeResponse(
                [
                    {
                        "id": 11,
                        "link": "https://example.com/posts/hello",
                        "title": {"rendered": "Hello post"},
                        "status": "draft",
                        "modified_gmt": "2026-06-08T04:00:00",
                        "type": "post",
                    }
                ]
            )
        return _FakeResponse(
            [
                {
                    "id": 22,
                    "link": "https://example.com/about",
                    "title": {"rendered": "About page"},
                    "status": "publish",
                    "modified_gmt": "2026-06-08T05:00:00",
                    "type": "page",
                }
            ]
        )

    monkeypatch.setattr(publishing_clients, "urlopen", _urlopen)
    profile = PublishingConnectionProfile(
        id="pub-one",
        label="Site one",
        provider_id="wordpress",
        site_url="https://example.com",
        auth_method=AUTH_METHOD_APP_PASSWORD,
        account_identifier="writer",
    )

    ok, message, items = publishing.browse_publishing_content(profile, "secret")

    assert ok is True
    assert message == "Loaded published content from example.com."
    assert [item.content_kind for item in items] == ["page", "post"]
    assert items[0].title == "About page"
    assert items[1].remote_url == "https://example.com/posts/hello"
    assert any("/posts?" in call for call in calls)
    assert any("/pages?" in call for call in calls)


def test_load_publishing_remote_item_returns_remote_document(monkeypatch) -> None:
    def _urlopen(request, **_kwargs):
        return _FakeResponse(
            {
                "id": 22,
                "link": "https://example.com/about",
                "title": {"rendered": "About page"},
                "status": "publish",
                "modified_gmt": "2026-06-08T05:00:00",
                "type": "page",
                "content": {"rendered": "<p>About body</p>"},
            }
        )

    monkeypatch.setattr(publishing_clients, "urlopen", _urlopen)
    profile = PublishingConnectionProfile(
        id="pub-one",
        label="Site one",
        provider_id="wordpress",
        site_url="https://example.com",
        auth_method=AUTH_METHOD_APP_PASSWORD,
        account_identifier="writer",
    )

    ok, message, document = publishing.load_publishing_remote_item(
        profile,
        "secret",
        content_kind="page",
        remote_id="22",
    )

    assert ok is True
    assert message == "Opened published content from example.com."
    assert document is not None
    assert document.title == "About page"
    assert document.content_kind == "page"
    assert document.body == "<p>About body</p>"


def test_load_publishing_remote_item_decodes_typographic_html_entities(monkeypatch) -> None:
    def _urlopen(request, **_kwargs):
        return _FakeResponse(
            {
                "id": 22,
                "link": "https://example.com/about",
                "title": {"rendered": "Writer&#8217;s notes"},
                "status": "publish",
                "modified_gmt": "2026-06-08T05:00:00",
                "type": "page",
                "content": {
                    "rendered": (
                        "<p>It&#8217;s ready&#8230; &ldquo;Quoted&rdquo; text"
                        "&nbsp;with spacing.</p>"
                    )
                },
            }
        )

    monkeypatch.setattr(publishing_clients, "urlopen", _urlopen)
    profile = PublishingConnectionProfile(
        id="pub-one",
        label="Site one",
        provider_id="wordpress",
        site_url="https://example.com",
        auth_method=AUTH_METHOD_APP_PASSWORD,
        account_identifier="writer",
    )

    ok, _message, document = publishing.load_publishing_remote_item(
        profile,
        "secret",
        content_kind="page",
        remote_id="22",
    )

    assert ok is True
    assert document is not None
    assert document.title == "Writer’s notes"
    assert document.body == '<p>It’s ready… “Quoted” text with spacing.</p>'


def test_load_publishing_remote_item_preserves_markup_significant_escapes(monkeypatch) -> None:
    def _urlopen(request, **_kwargs):
        return _FakeResponse(
            {
                "id": 22,
                "link": "https://example.com/about",
                "title": {"rendered": "Code sample"},
                "status": "publish",
                "modified_gmt": "2026-06-08T05:00:00",
                "type": "page",
                "content": {
                    "rendered": "<pre>&lt;em&gt;keep escaped markup&lt;/em&gt; &amp; text</pre>"
                },
            }
        )

    monkeypatch.setattr(publishing_clients, "urlopen", _urlopen)
    profile = PublishingConnectionProfile(
        id="pub-one",
        label="Site one",
        provider_id="wordpress",
        site_url="https://example.com",
        auth_method=AUTH_METHOD_APP_PASSWORD,
        account_identifier="writer",
    )

    ok, _message, document = publishing.load_publishing_remote_item(
        profile,
        "secret",
        content_kind="page",
        remote_id="22",
    )

    assert ok is True
    assert document is not None
    assert document.body == "<pre>&lt;em&gt;keep escaped markup&lt;/em&gt; &amp; text</pre>"


def test_load_publishing_remote_item_rejects_unsupported_content_kind() -> None:
    profile = PublishingConnectionProfile(
        id="pub-one",
        label="Site one",
        provider_id="wordpress",
        site_url="https://example.com",
        auth_method=AUTH_METHOD_APP_PASSWORD,
        account_identifier="writer",
    )

    ok, message, document = publishing.load_publishing_remote_item(
        profile,
        "secret",
        content_kind="product",
        remote_id="22",
    )

    assert ok is False
    assert message == "That publishing content type is not supported for this provider."
    assert document is None


def test_prepare_publishing_remote_content_defaults_to_readable_markdown() -> None:
    prepared = publishing.prepare_publishing_remote_content("<h1>Title</h1><p>Hello world</p>")

    assert prepared.authoring_surface == "markdown"
    assert prepared.open_representation == "readable_markdown"
    assert prepared.text == "# Title\n\nHello world\n"


def test_prepare_publishing_remote_content_allows_raw_html_override() -> None:
    prepared = publishing.prepare_publishing_remote_content(
        "<p>Hello world</p>",
        requested_open_representation="raw_html",
    )

    assert prepared.authoring_surface == "html"
    assert prepared.open_representation == "raw_html"
    assert prepared.text == "<p>Hello world</p>"


def test_prepare_publishing_remote_content_falls_back_to_raw_html_for_tables() -> None:
    prepared = publishing.prepare_publishing_remote_content(
        "<table><tr><td>Cell</td></tr></table>"
    )

    assert prepared.authoring_surface == "html"
    assert prepared.open_representation == "raw_html"
    assert prepared.text == "<table><tr><td>Cell</td></tr></table>"
