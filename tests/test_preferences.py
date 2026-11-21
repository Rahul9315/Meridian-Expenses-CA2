def test_anonymous_user_cannot_update_preferences(client):
    # Trying to update preferences without logging in
    response = client.post("/prefs", data={
        "prefs": '{"theme": "dark"}'
    })

    assert response.status_code == 302
    assert "/login" in response.location


def test_logged_in_user_can_save_valid_preferences(client):
    # Creating a logged-in user session
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    # Submitting valid JSON preferences
    response = client.post("/prefs", data={
        "prefs": '{"theme": "dark", "notifications": true}'
    })

    assert response.status_code == 302

    # Checking that the preferences were saved
    with client.session_transaction() as session:
        assert session["prefs"] == {
            "theme": "dark",
            "notifications": True
        }


def test_invalid_json_preferences_are_rejected(client):
    # Creating a logged-in user session
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    # Submitting malformed JSON
    response = client.post("/prefs", data={
        "prefs": '{"theme": '
    })

    assert response.status_code == 400


def test_non_dictionary_preferences_are_rejected(client):
    # Creating a logged-in user session
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    # Submitting a JSON list instead of a dictionary
    response = client.post("/prefs", data={
        "prefs": '["dark", "light"]'
    })

    assert response.status_code == 400
