def test_staff_can_access_own_claim(client):
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    response = client.get("/claim/1")

    assert response.status_code == 200


def test_anonymous_user_cannot_access_claim(client):
    response = client.get("/claim/1")

    assert response.status_code == 302
    assert "/login" in response.location


def test_staff_cannot_access_another_users_claim(client):
    """Jane must not access Rob's expense claim."""

    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    response = client.get("/claim/2")

    assert response.status_code == 403
