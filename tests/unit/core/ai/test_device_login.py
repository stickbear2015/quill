"""Tests for the accessible OAuth device-flow sign-in engine (AI-19)."""

from __future__ import annotations

from quill.core.ai import device_login as dl


def _config() -> dl.DeviceFlowConfig:
    return dl.DeviceFlowConfig(
        client_id="quill-app",
        device_authorization_url="https://example.com/device",
        token_url="https://example.com/token",
        scope="ai.generate",
    )


def _grant() -> dl.DeviceCodeGrant:
    return dl.DeviceCodeGrant(
        device_code="DEV-123",
        user_code="WDJB-MJHT",
        verification_uri="https://example.com/activate",
        interval=5.0,
        expires_in=900.0,
    )


def test_request_device_code_parses_response():
    def poster(url, form):
        assert url == "https://example.com/device"
        assert form == {"client_id": "quill-app", "scope": "ai.generate"}
        return {
            "device_code": "DEV-123",
            "user_code": "WDJB-MJHT",
            "verification_uri": "https://example.com/activate",
            "interval": 5,
            "expires_in": 600,
        }

    grant = dl.request_device_code(_config(), poster=poster)
    assert grant.user_code == "WDJB-MJHT"
    assert grant.interval == 5.0
    assert grant.expires_in == 600.0


def test_poll_once_classifies_states():
    config = _config()
    grant = _grant()

    assert (
        dl.poll_once(config, grant, poster=lambda u, f: {"error": "authorization_pending"}).status
        == dl.STATUS_PENDING
    )
    assert (
        dl.poll_once(config, grant, poster=lambda u, f: {"error": "slow_down"}).status
        == dl.STATUS_SLOW_DOWN
    )
    assert (
        dl.poll_once(config, grant, poster=lambda u, f: {"error": "access_denied"}).status
        == dl.STATUS_DENIED
    )
    assert (
        dl.poll_once(config, grant, poster=lambda u, f: {"error": "expired_token"}).status
        == dl.STATUS_EXPIRED
    )
    authorized = dl.poll_once(config, grant, poster=lambda u, f: {"access_token": "tok"})
    assert authorized.status == dl.STATUS_AUTHORIZED
    assert authorized.tokens == {"access_token": "tok"}


def test_run_device_login_succeeds_after_pending():
    replies = [
        {"error": "authorization_pending"},
        {"error": "authorization_pending"},
        {"access_token": "tok", "token_type": "bearer"},
    ]

    def poster(url, form):
        return replies.pop(0)

    slept: list[float] = []
    result = dl.run_device_login(
        _config(),
        _grant(),
        poster=poster,
        clock=lambda: 0.0,
        sleeper=slept.append,
    )
    assert result.status == dl.STATUS_AUTHORIZED
    assert result.tokens["access_token"] == "tok"
    assert slept == [5.0, 5.0]


def test_run_device_login_backs_off_on_slow_down():
    replies = [
        {"error": "slow_down"},
        {"access_token": "tok"},
    ]

    def poster(url, form):
        return replies.pop(0)

    slept: list[float] = []
    result = dl.run_device_login(
        _config(),
        _grant(),
        poster=poster,
        clock=lambda: 0.0,
        sleeper=slept.append,
    )
    assert result.status == dl.STATUS_AUTHORIZED
    assert slept == [10.0]  # interval grew from 5 to 10


def test_run_device_login_expires_at_deadline():
    clock_value = {"t": 0.0}

    def clock():
        clock_value["t"] += 100.0
        return clock_value["t"]

    def poster(url, form):
        return {"error": "authorization_pending"}

    grant = dl.DeviceCodeGrant(
        device_code="DEV-123",
        user_code="WDJB-MJHT",
        verification_uri="https://example.com/activate",
        interval=5.0,
        expires_in=120.0,
    )
    result = dl.run_device_login(
        _config(), grant, poster=poster, clock=clock, sleeper=lambda s: None
    )
    assert result.status == dl.STATUS_EXPIRED


def test_run_device_login_stops_on_denied():
    def poster(url, form):
        return {"error": "access_denied"}

    result = dl.run_device_login(
        _config(), _grant(), poster=poster, clock=lambda: 0.0, sleeper=lambda s: None
    )
    assert result.status == dl.STATUS_DENIED


def test_announcements_are_spoken():
    grant = _grant()
    spoken = dl.announce_device_code(grant)
    assert "https://example.com/activate" in spoken
    assert "WDJB-MJHT" in spoken
    assert "15 minutes" in spoken

    assert "connected" in dl.describe_login_result(dl.PollResult(dl.STATUS_AUTHORIZED, tokens={}))
    denied = dl.describe_login_result(
        dl.PollResult(dl.STATUS_DENIED, error="You declined the sign-in request.")
    )
    assert "declined" in denied
