from decimal import Decimal

from tests.conftest import auth_headers, register_user

PROJECT_PAYLOAD = {
    "title": "Racines",
    "project_type": "TV_SERIES",
    "country": "Cameroun",
}


def _register_and_get_token(client, email: str) -> str:
    data = register_user(client, email)
    return data["access_token"]


def _create_project(client, token: str) -> dict:
    resp = client.post("/api/v1/projects", json=PROJECT_PAYLOAD, headers=auth_headers(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_budget_requires_auth(client):
    resp = client.get("/api/v1/projects/1/budget")
    assert resp.status_code == 401


def test_empty_budget_summary(client):
    token = _register_and_get_token(client, "empty@example.com")
    project = _create_project(client, token)

    resp = client.get(f"/api/v1/projects/{project['id']}/budget", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["categories"] == []
    assert Decimal(body["total"]) == Decimal("0")
    assert body["currency"] is None


def test_category_and_line_item_subtotals(client):
    token = _register_and_get_token(client, "budget@example.com")
    project = _create_project(client, token)

    tournage = client.post(
        f"/api/v1/projects/{project['id']}/budget/categories",
        json={"name": "Tournage"},
        headers=auth_headers(token),
    ).json()
    post_prod = client.post(
        f"/api/v1/projects/{project['id']}/budget/categories",
        json={"name": "Post-production"},
        headers=auth_headers(token),
    ).json()

    client.post(
        f"/api/v1/projects/{project['id']}/budget/categories/{tournage['id']}/items",
        json={"label": "Cadreur", "quantity": "5", "unit_cost": "200"},
        headers=auth_headers(token),
    )
    client.post(
        f"/api/v1/projects/{project['id']}/budget/categories/{tournage['id']}/items",
        json={"label": "Location matériel", "quantity": "1", "unit_cost": "1500"},
        headers=auth_headers(token),
    )
    client.post(
        f"/api/v1/projects/{project['id']}/budget/categories/{post_prod['id']}/items",
        json={"label": "Montage", "quantity": "10", "unit_cost": "150"},
        headers=auth_headers(token),
    )

    resp = client.get(f"/api/v1/projects/{project['id']}/budget", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    categories = {c["name"]: c for c in body["categories"]}

    assert Decimal(categories["Tournage"]["subtotal"]) == Decimal("2500.00")  # 5*200 + 1*1500
    assert Decimal(categories["Post-production"]["subtotal"]) == Decimal("1500.00")  # 10*150
    assert Decimal(body["total"]) == Decimal("4000.00")


def test_update_line_item_recomputes_subtotal(client):
    token = _register_and_get_token(client, "editor-budget@example.com")
    project = _create_project(client, token)
    category = client.post(
        f"/api/v1/projects/{project['id']}/budget/categories",
        json={"name": "Tournage"},
        headers=auth_headers(token),
    ).json()
    item = client.post(
        f"/api/v1/projects/{project['id']}/budget/categories/{category['id']}/items",
        json={"label": "Cadreur", "quantity": "5", "unit_cost": "200"},
        headers=auth_headers(token),
    ).json()
    assert Decimal(item["subtotal"]) == Decimal("1000.00")

    resp = client.put(
        f"/api/v1/projects/{project['id']}/budget/items/{item['id']}",
        json={"quantity": "10"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert Decimal(resp.json()["subtotal"]) == Decimal("2000.00")


def test_delete_category_cascades_to_line_items(client):
    token = _register_and_get_token(client, "delete-cat@example.com")
    project = _create_project(client, token)
    category = client.post(
        f"/api/v1/projects/{project['id']}/budget/categories",
        json={"name": "Tournage"},
        headers=auth_headers(token),
    ).json()
    client.post(
        f"/api/v1/projects/{project['id']}/budget/categories/{category['id']}/items",
        json={"label": "Cadreur", "quantity": "1", "unit_cost": "100"},
        headers=auth_headers(token),
    )

    resp = client.delete(
        f"/api/v1/projects/{project['id']}/budget/categories/{category['id']}",
        headers=auth_headers(token),
    )
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/projects/{project['id']}/budget", headers=auth_headers(token))
    assert resp.json()["categories"] == []


def test_user_cannot_access_another_users_budget(client):
    token_a = _register_and_get_token(client, "usera-budget@example.com")
    token_b = _register_and_get_token(client, "userb-budget@example.com")
    project = _create_project(client, token_a)
    category = client.post(
        f"/api/v1/projects/{project['id']}/budget/categories",
        json={"name": "Tournage"},
        headers=auth_headers(token_a),
    ).json()

    resp = client.get(f"/api/v1/projects/{project['id']}/budget", headers=auth_headers(token_b))
    assert resp.status_code == 404

    resp = client.post(
        f"/api/v1/projects/{project['id']}/budget/categories/{category['id']}/items",
        json={"label": "Hijack", "quantity": "1", "unit_cost": "1"},
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 404

    resp = client.delete(
        f"/api/v1/projects/{project['id']}/budget/categories/{category['id']}",
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 404
