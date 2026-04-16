CONFLICT_RESPONSE = {"detail": "short_name already exists"}
NOT_FOUND_RESPONSE = {"detail": "Link not found"}
INVALID_RANGE_RESPONSE = {"detail": "Invalid range parameter"}


def create_link(client, original_url: str, short_name: str):
    return client.post(
        "/api/links",
        json={"original_url": original_url, "short_name": short_name},
    )


def seed_links(client, amount: int):
    for index in range(amount):
        create_link(
            client=client,
            original_url=f"https://example.com/{index}",
            short_name=f"seed-{index}",
        )


def test_list_links_returns_empty_list(client):
    response = client.get("/api/links")

    assert response.status_code == 200
    assert response.headers["accept-ranges"] == "links"
    assert response.headers["content-range"] == "links 0-0/0"
    assert response.json() == []


def test_create_link_returns_created_object(client):
    response = create_link(
        client=client,
        original_url="https://example.com/long-url",
        short_name="exmpl",
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "original_url": "https://example.com/long-url",
        "short_name": "exmpl",
        "short_url": "https://short.io/r/exmpl",
    }


def test_list_links_returns_all_links(client):
    create_link(
        client=client,
        original_url="https://example.com/long-url",
        short_name="exmpl",
    )
    create_link(
        client=client,
        original_url="https://example.com/long-url2",
        short_name="exmpl2",
    )

    response = client.get("/api/links")

    assert response.status_code == 200
    assert response.headers["accept-ranges"] == "links"
    assert response.headers["content-range"] == "links 0-2/2"
    assert response.json() == [
        {
            "id": 1,
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
            "short_url": "https://short.io/r/exmpl",
        },
        {
            "id": 2,
            "original_url": "https://example.com/long-url2",
            "short_name": "exmpl2",
            "short_url": "https://short.io/r/exmpl2",
        },
    ]


def test_list_links_supports_pagination_from_start(client):
    seed_links(client=client, amount=11)

    response = client.get("/api/links?range=[0,10]")
    payload = response.json()

    assert response.status_code == 200
    assert response.headers["accept-ranges"] == "links"
    assert response.headers["content-range"] == "links 0-10/11"
    assert len(payload) == 10
    assert payload[0]["id"] == 1
    assert payload[-1]["id"] == 10


def test_list_links_supports_pagination_with_offset(client):
    seed_links(client=client, amount=11)

    response = client.get("/api/links?range=[5,10]")
    payload = response.json()

    assert response.status_code == 200
    assert response.headers["accept-ranges"] == "links"
    assert response.headers["content-range"] == "links 5-10/11"
    assert len(payload) == 5
    assert [item["id"] for item in payload] == [6, 7, 8, 9, 10]


def test_list_links_with_invalid_range_returns_400(client):
    response = client.get("/api/links?range=broken")

    assert response.status_code == 400
    assert response.json() == INVALID_RANGE_RESPONSE


def test_get_link_by_id(client):
    created_link = create_link(
        client=client,
        original_url="https://example.com/long-url",
        short_name="exmpl",
    ).json()

    response = client.get(f"/api/links/{created_link['id']}")

    assert response.status_code == 200
    assert response.json() == created_link


def test_get_link_by_id_returns_404_for_unknown_id(client):
    response = client.get("/api/links/999")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_RESPONSE


def test_redirect_by_short_name(client):
    create_link(
        client=client,
        original_url="https://example.com/long-url",
        short_name="exmpl",
    )

    response = client.get("/r/exmpl", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/long-url"


def test_redirect_by_short_name_returns_404_for_unknown_short_name(client):
    response = client.get("/r/unknown", follow_redirects=False)

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_RESPONSE


def test_update_link(client):
    created_link = create_link(
        client=client,
        original_url="https://example.com/long-url",
        short_name="exmpl",
    ).json()

    response = client.put(
        f"/api/links/{created_link['id']}",
        json={
            "original_url": "https://example.com/updated-url",
            "short_name": "updated",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": created_link["id"],
        "original_url": "https://example.com/updated-url",
        "short_name": "updated",
        "short_url": "https://short.io/r/updated",
    }


def test_update_link_returns_404_for_unknown_id(client):
    response = client.put(
        "/api/links/999",
        json={
            "original_url": "https://example.com/updated-url",
            "short_name": "updated",
        },
    )

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_RESPONSE


def test_create_link_returns_409_for_duplicate_short_name(client):
    create_link(
        client=client,
        original_url="https://example.com/one",
        short_name="same",
    )

    response = create_link(
        client=client,
        original_url="https://example.com/two",
        short_name="same",
    )

    assert response.status_code == 409
    assert response.json() == CONFLICT_RESPONSE


def test_update_link_returns_409_for_duplicate_short_name(client):
    first_link = create_link(
        client=client,
        original_url="https://example.com/one",
        short_name="one",
    ).json()
    create_link(
        client=client,
        original_url="https://example.com/two",
        short_name="two",
    )

    response = client.put(
        f"/api/links/{first_link['id']}",
        json={
            "original_url": "https://example.com/one-updated",
            "short_name": "two",
        },
    )

    assert response.status_code == 409
    assert response.json() == CONFLICT_RESPONSE


def test_delete_link(client):
    created_link = create_link(
        client=client,
        original_url="https://example.com/long-url",
        short_name="exmpl",
    ).json()

    response = client.delete(f"/api/links/{created_link['id']}")
    link_response_after_delete = client.get(f"/api/links/{created_link['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert link_response_after_delete.status_code == 404
    assert link_response_after_delete.json() == NOT_FOUND_RESPONSE


def test_delete_link_returns_404_for_unknown_id(client):
    response = client.delete("/api/links/999")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_RESPONSE
