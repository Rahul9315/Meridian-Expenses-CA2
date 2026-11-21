import sqlite3
from app import app

def test_anonymous_user_cannot_submit_claim(client):
    # Trying to submit a claim without logging in
    response = client.post("/claim/new", data={
        "merchant": "Test Hotel",
        "amount": "150",
        "note": "Testing unauthorised claim submission"
    })

    # Checking how many claims are stored in the database
    connection = sqlite3.connect(app.config["DATABASE"])
    claim_count = connection.execute(
        "SELECT COUNT(*) FROM claims"
    ).fetchone()[0]
    connection.close()

    # Checking that no new claim was created
    assert claim_count == 2
    # Checking if the user is redirected to the login page
    assert response.status_code == 302
    assert "/login" in response.location