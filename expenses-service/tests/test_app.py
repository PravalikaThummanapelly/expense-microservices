from unittest.mock import patch, Mock


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_create_expense_without_token_fails(client):
    response = client.post("/expenses", json={"title": "Coffee", "amount": 5})
    assert response.status_code == 401


def test_create_expense_with_valid_token_succeeds(client, auth_headers):
    response = client.post(
        "/expenses",
        json={"title": "Coffee", "amount": 5.5, "category": "food"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Coffee"
    assert data["user_id"] == 1


def test_list_expenses_returns_only_created_ones(client, auth_headers):
    client.post("/expenses", json={"title": "Coffee", "amount": 5}, headers=auth_headers)
    client.post("/expenses", json={"title": "Lunch", "amount": 12}, headers=auth_headers)

    response = client.get("/expenses", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2


def test_verify_owner_calls_users_service(client, auth_headers):
    """
    This test proves the service-to-service call logic works WITHOUT needing
    users-service actually running. We fake ("mock") what the HTTP call to
    users-service would return, so we're only testing expenses-service's own
    logic here — exactly what a unit test should do.
    """
    create_resp = client.post(
        "/expenses", json={"title": "Coffee", "amount": 5}, headers=auth_headers
    )
    expense_id = create_resp.get_json()["id"]

    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"id": 1, "name": "Test User", "email": "t@test.com"}

    with patch("app.requests.get", return_value=fake_response) as mocked_get:
        response = client.get(f"/expenses/{expense_id}/verify-owner", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()["verified_user"]["id"] == 1
        mocked_get.assert_called_once()  # confirms we actually attempted the call
