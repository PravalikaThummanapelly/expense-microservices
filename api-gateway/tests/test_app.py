from unittest.mock import patch, Mock


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_auth_signup_forwards_to_users_service(client):
    fake_response = Mock()
    fake_response.status_code = 201
    fake_response.content = b'{"id": 1, "name": "Test"}'
    fake_response.headers = {"Content-Type": "application/json"}

    with patch("app.requests.request", return_value=fake_response) as mocked_request:
        response = client.post(
            "/auth/signup",
            json={"name": "Test", "email": "t@test.com", "password": "pass123"},
        )
        assert response.status_code == 201
        # Confirm it forwarded to the RIGHT upstream URL
        called_url = mocked_request.call_args.kwargs["url"]
        assert called_url == "http://users-service:5001/signup"


def test_expenses_forwards_to_expenses_service_with_correct_path(client):
    """
    Regression test for the real path-rewriting bug we hit earlier:
    /expenses/<id>/verify-owner must forward to
    http://expenses-service:5002/expenses/<id>/verify-owner
    (not silently drop the 'expenses' prefix).
    """
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.content = b'{"ok": true}'
    fake_response.headers = {"Content-Type": "application/json"}

    with patch("app.requests.request", return_value=fake_response) as mocked_request:
        client.get("/expenses/3/verify-owner", headers={"Authorization": "Bearer faketoken"})
        called_url = mocked_request.call_args.kwargs["url"]
        assert called_url == "http://expenses-service:5002/expenses/3/verify-owner"
