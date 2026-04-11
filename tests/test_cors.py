ALLOWED_ORIGIN = "http://localhost:5173"
FORBIDDEN_ORIGIN = "http://localhost:3000"


def test_cors_allows_local_frontend_origin(client):
    response = client.get(
        "/api/links",
        headers={"Origin": ALLOWED_ORIGIN},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN


def test_cors_preflight_allows_required_methods(client):
    response = client.options(
        "/api/links",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    allowed_methods = response.headers["access-control-allow-methods"]
    assert "GET" in allowed_methods
    assert "POST" in allowed_methods
    assert "PUT" in allowed_methods
    assert "DELETE" in allowed_methods


def test_cors_rejects_unknown_origin(client):
    response = client.get(
        "/api/links",
        headers={"Origin": FORBIDDEN_ORIGIN},
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
