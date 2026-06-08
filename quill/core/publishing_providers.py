from __future__ import annotations

from dataclasses import dataclass

WORDPRESS_PROVIDER_ID = "wordpress"

AUTH_METHOD_APP_PASSWORD = "app_password"
AUTH_METHOD_PASSWORD = "password"
AUTH_METHOD_BROWSER_SESSION = "browser_session"
AUTH_METHOD_EMAIL_LINK = "email_link"


@dataclass(frozen=True, slots=True)
class PublishingAuthMethodDefinition:
    id: str
    name: str
    description: str
    requires_identifier: bool = False
    requires_secret: bool = False


@dataclass(frozen=True, slots=True)
class PublishingProviderDefinition:
    id: str
    name: str
    help_text: str
    default_content_format: str
    auth_methods: tuple[str, ...]
    implemented_auth_methods: tuple[str, ...]


AUTH_METHOD_DEFINITIONS: dict[str, PublishingAuthMethodDefinition] = {
    AUTH_METHOD_APP_PASSWORD: PublishingAuthMethodDefinition(
        id=AUTH_METHOD_APP_PASSWORD,
        name="Application password",
        description="Use a username or email plus an application password.",
        requires_identifier=True,
        requires_secret=True,
    ),
    AUTH_METHOD_PASSWORD: PublishingAuthMethodDefinition(
        id=AUTH_METHOD_PASSWORD,
        name="Site password",
        description="Use a normal account password when a provider supports it.",
        requires_identifier=True,
        requires_secret=True,
    ),
    AUTH_METHOD_BROWSER_SESSION: PublishingAuthMethodDefinition(
        id=AUTH_METHOD_BROWSER_SESSION,
        name="Browser sign-in",
        description="Sign in through a browser-based flow managed by the provider.",
    ),
    AUTH_METHOD_EMAIL_LINK: PublishingAuthMethodDefinition(
        id=AUTH_METHOD_EMAIL_LINK,
        name="Email sign-in link",
        description="Use a provider flow that sends a one-time sign-in link by email.",
        requires_identifier=True,
    ),
}


PROVIDER_DEFINITIONS: dict[str, PublishingProviderDefinition] = {
    WORDPRESS_PROVIDER_ID: PublishingProviderDefinition(
        id=WORDPRESS_PROVIDER_ID,
        name="WordPress",
        help_text=(
            "Works with WordPress.com, self-hosted WordPress, and compatible hosts "
            "that expose the standard WordPress REST API."
        ),
        default_content_format="html",
        auth_methods=(
            AUTH_METHOD_APP_PASSWORD,
            AUTH_METHOD_PASSWORD,
            AUTH_METHOD_BROWSER_SESSION,
            AUTH_METHOD_EMAIL_LINK,
        ),
        implemented_auth_methods=(AUTH_METHOD_APP_PASSWORD,),
    ),
}


def publishing_provider_definition(provider_id: str) -> PublishingProviderDefinition:
    normalized = provider_id.strip().lower()
    return PROVIDER_DEFINITIONS.get(normalized, PROVIDER_DEFINITIONS[WORDPRESS_PROVIDER_ID])


def publishing_provider_display_name(provider_id: str) -> str:
    return publishing_provider_definition(provider_id).name


def publishing_provider_help_text(provider_id: str) -> str:
    return publishing_provider_definition(provider_id).help_text


def default_content_format_for_provider(provider_id: str) -> str:
    return publishing_provider_definition(provider_id).default_content_format


def auth_method_definition(auth_method_id: str) -> PublishingAuthMethodDefinition:
    normalized = auth_method_id.strip().lower()
    return AUTH_METHOD_DEFINITIONS.get(
        normalized, AUTH_METHOD_DEFINITIONS[AUTH_METHOD_APP_PASSWORD]
    )


def publishing_auth_method_name(auth_method_id: str) -> str:
    return auth_method_definition(auth_method_id).name


def provider_auth_methods(provider_id: str) -> tuple[str, ...]:
    return publishing_provider_definition(provider_id).auth_methods


def provider_implemented_auth_methods(provider_id: str) -> tuple[str, ...]:
    return publishing_provider_definition(provider_id).implemented_auth_methods
