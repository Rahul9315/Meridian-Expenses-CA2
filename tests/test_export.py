def test_anonymous_user_cannot_export_claims(client):
    # Trying to export claims without logging in
    response = client.get("/export")

    assert response.status_code == 302
    assert "/login" in response.location


def test_staff_user_cannot_export_all_claims(client):
    # Creating a staff user session
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    # Trying to export all users' claims as staff
    response = client.get("/export")

    assert response.status_code == 403


def test_finance_user_can_export_claims(client):
    # Creating a finance user session
    with client.session_transaction() as session:
        session["uid"] = 3
        session["name"] = "Alice Chen"
        session["role"] = "finance"

    # Downloading the claims CSV
    response = client.get("/export")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "attachment" in response.headers.get("Content-Disposition", "")
    assert b"Jane hotel expense" in response.data
    assert b"Rob travel expense" in response.data