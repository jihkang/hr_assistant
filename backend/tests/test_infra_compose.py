from pathlib import Path


def test_backend_service_wires_security_env_vars_from_compose() -> None:
    compose_text = Path(__file__).resolve().parents[2].joinpath("infra", "docker-compose.yml").read_text()

    assert "SECRET_KEY: ${SECRET_KEY:-change-this-secret-key-at-least-32-bytes}" in compose_text
    assert "COOKIE_SAMESITE: ${COOKIE_SAMESITE:-lax}" in compose_text
    assert "COOKIE_SECURE: ${COOKIE_SECURE:-false}" in compose_text
