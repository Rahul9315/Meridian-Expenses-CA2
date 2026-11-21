import sqlite3
from app import app
import pytest

def test_negative_expense_amount_is_rejected(client):
    # Logging in as Jane before submitting an expense
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    # Trying to submit an expense with a negative amount
    response = client.post("/claim/new", data={
        "merchant": "Test Hotel",
        "amount": "-500",
        "note": "Testing negative expense amount"
    })

    # Checking whether the invalid expense was saved
    connection = sqlite3.connect(app.config["DATABASE"])
    claim_count = connection.execute(
        "SELECT COUNT(*) FROM claims"
    ).fetchone()[0]
    connection.close()

    
    # Checking that the application rejected the invalid amount
    assert response.status_code == 400
    assert claim_count == 2

@pytest.mark.parametrize("amount", [
    "0",
    "hello",
    "125.999",
    "NaN",
    "Infinity"
])
def test_invalid_expense_amounts_are_rejected(client, amount):
    # Logging in as Jane before submitting an expense
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    # Trying to submit an expense with an invalid amount
    response = client.post("/claim/new", data={
        "merchant": "Test Hotel",
        "amount": amount,
        "note": "Testing invalid expense amount"
    })

    # Checking that the invalid amount was rejected
    assert response.status_code == 400

    # Checking that no new claim was saved
    connection = sqlite3.connect(app.config["DATABASE"])
    claim_count = connection.execute(
        "SELECT COUNT(*) FROM claims"
    ).fetchone()[0]
    connection.close()

    assert claim_count == 2


def test_valid_expense_amount_is_accepted(client):
    # Logging in as Jane before submitting an expense
    with client.session_transaction() as session:
        session["uid"] = 1
        session["name"] = "Jane Doe"
        session["role"] = "staff"

    # Trying to submit a valid expense amount
    response = client.post("/claim/new", data={
        "merchant": "Test Hotel",
        "amount": "125.50",
        "note": "Valid hotel expense"
    })

    # Checking that the claim was accepted
    assert response.status_code == 302

    # Checking that the new claim was saved correctly
    connection = sqlite3.connect(app.config["DATABASE"])
    claim = connection.execute(
        "SELECT amount FROM claims WHERE user_id = 1 "
        "ORDER BY id DESC LIMIT 1"
    ).fetchone()
    connection.close()

    assert claim[0] == 125.5
