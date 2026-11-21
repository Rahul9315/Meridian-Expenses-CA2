
def test_anonymous_user_cannot_access_admin_users(client):
    # Requesting the administrator page without logging in
    response = client.get("/admin/users")

    assert response.status_code == 302


def test_staff_user_cannot_access_admin_users(client):
    # Creating a session for a staff user
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    # Requesting the administrator page as a staff user
    response = client.get("/admin/users")

    assert response.status_code == 403


def test_admin_user_can_access_admin_users(client):
    # Creating a session for an administrator
    with client.session_transaction() as session:
        session["uid"] = 4
        session["name"] = "System Admin"
        session["role"] = "admin"

    # Requesting the administrator page as an administrator
    response = client.get("/admin/users")

    assert response.status_code == 200
