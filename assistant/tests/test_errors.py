"""The friendly one-line explanations for the failures that happen on a bad day."""

import luna


class AuthenticationError(Exception):
    pass


def test_known_failures_get_a_fix():
    assert "Credentials" in luna.explain(AuthenticationError("401"))
    assert "Credentials" in luna.explain(Exception("UnrecognizedClientException: token invalid"))
    assert "model id" in luna.explain(Exception("ValidationException: The provided model identifier is invalid"))
    assert "network" in luna.explain(Exception("Failed to connect to proxy URL"))
    assert "credit" in luna.explain(Exception("Your credit balance is too low"))


def test_unknown_failures_are_not_hidden():
    assert luna.explain(ValueError("a real bug")) is None
