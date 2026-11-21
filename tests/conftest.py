
import sqlite3
import pytest

from app import app


@pytest.fixture
def client(tmp_path):
    """Create an isolated database and Flask test client."""

    database_path = tmp_path / "test_expenses.db"

    app.config.update(
        TESTING=True,
        DATABASE=str(database_path)
    )

    connection = sqlite3.connect(database_path)

    connection.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL
        );

        CREATE TABLE claims (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            merchant TEXT,
            amount REAL,
            note TEXT,
            status TEXT
        );

       INSERT INTO users
            (id, username, password, name, role)
        VALUES
            (1, 'jdoe', 'testhash1', 'Jane Doe', 'staff'),
            (2, 'rsmith', 'testhash2', 'Rob Smith', 'staff'),
            (3, 'achen', 'testhash3', 'Alice Chen', 'finance'),
            (4, 'admin', 'testhash4', 'System Admin', 'admin');

        INSERT INTO claims
            (id, user_id, merchant, amount, note, status)
        VALUES
            (1, 1, 'Hotel', 150.00, 'Jane hotel expense', 'pending'),
            (2, 2, 'Travel', 250.00, 'Rob travel expense', 'pending');
    """)

    connection.commit()
    connection.close()

    with app.test_client() as test_client:
        yield test_client
