
def test_staff_cannot_access_another_users_claim(client):
    """Jane must not be able to access Rob's expense claim."""

    # Authenticate as Jane (user ID 1).
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    # Attempt to access Rob's claim (claim ID 2).
    response = client.get("/claim/2")

    # Expected secure behaviour.
    assert response.status_code == 403
