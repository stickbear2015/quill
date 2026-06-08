from __future__ import annotations

from dataclasses import dataclass

WORDPRESS_PROVIDER_ID = "wordpress"
SUPPORTED_PUBLISHING_PROVIDERS = frozenset({WORDPRESS_PROVIDER_ID})


@dataclass(frozen=True, slots=True)
class PublishingProviderDefinition:
    id: str
    name: str
    help_text: str
    default_content_format: str = "html"


_PROVIDERS: dict[str, PublishingProviderDefinition] = {
    WORDPRESS_PROVIDER_ID: PublishingProviderDefinition(
        id=WORDPRESS_PROVIDER_ID,
        name="WordPress",
        help_text=(
            "Connect to a WordPress site with your username and an application "
            "password. Quill verifies the site before any publish action runs."
        ),
    ),
}


def publishing_provider_definition(provider_id: str) -> PublishingProviderDefinition:
    return _PROVIDERS.get(provider_id.strip().lower(), _PROVIDERS[WORDPRESS_PROVIDER_ID])


def publishing_provider_display_name(provider_id: str) -> str:
    return publishing_provider_definition(provider_id).name


def publishing_provider_help_text(provider_id: str) -> str:
    return publishing_provider_definition(provider_id).help_text


def default_content_format_for_provider(provider_id: str) -> str:
    return publishing_provider_definition(provider_id).default_content_format
