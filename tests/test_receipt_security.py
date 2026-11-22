
def test_anonymous_user_cannot_access_receipt(client):
    response = client.get("/receipt?f=claim-1.txt")
    assert response.status_code == 302


def test_user_can_access_own_receipt(client, monkeypatch, tmp_path):
    # Creating a permitted test receipt
    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    receipt_file = receipts_dir / "claim-1.txt"
    receipt_file.write_text("Test receipt", encoding="utf-8")

    # Setting the application root to the temporary test directory
    from app import app
    monkeypatch.setattr(app, "root_path", str(tmp_path))

    # Creating an authenticated session for the claim owner
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    response = client.get("/receipt?f=claim-1.txt")

    assert response.status_code == 200
    assert response.data == b"Test receipt"


def test_user_cannot_access_another_users_receipt(client, monkeypatch, tmp_path):
    # Creating a receipt belonging to another user
    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    receipt_file = receipts_dir / "claim-2.txt"
    receipt_file.write_text("Rob's receipt", encoding="utf-8")

    # Setting the application root to the temporary test directory
    from app import app
    monkeypatch.setattr(app, "root_path", str(tmp_path))

    # Creating an authenticated session for Jane
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    response = client.get("/receipt?f=claim-2.txt")

    assert response.status_code == 403


def test_path_traversal_is_blocked(client, monkeypatch, tmp_path):
    # Creating a file outside the permitted receipts directory
    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("Sensitive information", encoding="utf-8")

    # Setting the application root to the temporary test directory
    from app import app
    monkeypatch.setattr(app, "root_path", str(tmp_path))

    # Creating an authenticated test session
    with client.session_transaction() as session:
        session["uid"] = 1
        session["role"] = "staff"

    response = client.get("/receipt?f=../secret.txt")

    assert response.status_code == 403
