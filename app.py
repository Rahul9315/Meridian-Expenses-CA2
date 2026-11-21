"""
Meridian Expenses — staff expense portal.

*** INTENTIONALLY VULNERABLE. TEACHING ARTEFACT. ***
Issued for CCT MSc Cybersecurity, Secure Programming and Scripting, CA1.
Do not deploy. Do not expose beyond localhost. Contains no real data.

There are more than six distinct, independently exploitable defects in this
file and its siblings. They are not marked.
"""
## import hashlib
import os
## import pickle
import json
import csv
import io
from pathlib import Path
import secrets
import sqlite3
## import subprocess
from decimal import Decimal, InvalidOperation
from werkzeug.security import generate_password_hash, check_password_hash

from flask import (Flask, g, redirect, render_template, request, session,
                   send_file, url_for)

app = Flask(__name__)

# Loading the Flask secret from the environment
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

## app = Flask(__name__)
## app.secret_key = "meridian-dev-key"          # fixed across every deployment
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")

"""
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db

"""

def db():
    if "db" not in g:
        database_path = app.config.get("DATABASE", DB)
        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close(_exc):
    d = g.pop("db", None)
    if d is not None:
        d.close()

def hash_pw(pw):
    # Generating a secure password hash using scrypt
    return generate_password_hash(pw, method="scrypt")


"""

def hash_pw(pw):
    return hashlib.md5(pw.encode()).hexdigest()


@app.route("/", methods=["GET"])
def index():
    if "uid" not in session:
        return redirect(url_for("login"))
    rows = db().execute(
        "SELECT * FROM claims WHERE user_id = %s ORDER BY id DESC" % session["uid"]
    ).fetchall()
    return render_template("index.html", claims=rows, user=session.get("name"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        q = ("SELECT id, name, role FROM users "
             "WHERE username = '%s' AND password = '%s'" % (u, hash_pw(p)))
        row = db().execute(q).fetchone()
        if row:
            session["uid"], session["name"], session["role"] = row["id"], row["name"], row["role"]
            return redirect(url_for("index"))
        exists = db().execute(
            "SELECT 1 FROM users WHERE username = ?", (u,)).fetchone()
        error = "Wrong password." if exists else "No such user."
    return render_template("login.html", error=error)
"""

@app.route("/", methods=["GET"])
def index():
    if "uid" not in session:
        return redirect(url_for("login"))

    # Retrieving claims belonging to the logged-in user
    rows = db().execute(
        "SELECT * FROM claims WHERE user_id = ? ORDER BY id DESC",
        (session["uid"],)
    ).fetchall()

    return render_template("index.html", claims=rows, user=session.get("name"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")

        # Retrieving the account using a parameterised query
        row = db().execute(
            "SELECT id, password, name, role FROM users WHERE username = ?",
            (u,)
        ).fetchone()

        # Checking the submitted password against the stored hash
        if row and check_password_hash(row["password"], p):
            session["uid"], session["name"], session["role"] = row["id"], row["name"], row["role"]
            return redirect(url_for("index"))

        # Checking whether the submitted username exists
        error = "Wrong password." if row else "No such user."

    return render_template("login.html", error=error)



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

"""
@app.route("/claim/<int:cid>")
def claim(cid):
    row = db().execute("SELECT * FROM claims WHERE id = ?", (cid,)).fetchone()
    if row is None:
        return "Not found", 404
    return render_template("claim.html", c=row)
"""
## Fixing  the IDOR vulnerability
@app.route("/claim/<int:cid>")
def claim(cid):
    if "uid" not in session:
        return redirect(url_for("login"))

    row = db().execute(
        "SELECT * FROM claims WHERE id = ?", (cid,)
    ).fetchone()

    if row is None:
        return "Not found", 404

    if row["user_id"] != session["uid"]:
        return "Forbidden", 403

    return render_template("claim.html", c=row)



"""
@app.route("/claim/new", methods=["POST"])
def new_claim():
    db().execute(
        "INSERT INTO claims (user_id, merchant, amount, note, status) "
        "VALUES (?,?,?,?,'pending')",
        (session.get("uid"), request.form.get("merchant"),
         request.form.get("amount"), request.form.get("note")))
    db().commit()
    return redirect(url_for("index"))
"""


@app.route("/claim/new", methods=["POST"])
def new_claim():
    # Checking if the user is logged in before creating a claim
    if "uid" not in session:
        return redirect(url_for("login"))

    # Getting the submitted expense amount
    amount_input = request.form.get("amount", "")

    # Checking if the amount is a valid positive number
    try:
        amount = Decimal(amount_input)

        if not amount.is_finite() or amount <= 0:
            return "Invalid expense amount", 400

        if amount.as_tuple().exponent < -2:
            return "Maximum two decimal places allowed", 400

    except InvalidOperation:
        return "Invalid expense amount", 400

    # Saving the valid expense claim
    db().execute(
        "INSERT INTO claims (user_id, merchant, amount, note, status) "
        "VALUES (?,?,?,?, 'pending')",
        (session["uid"], request.form.get("merchant"),
         float(amount), request.form.get("note"))
    )
    db().commit()

    return redirect(url_for("index"))


@app.route("/receipt")
def receipt():
    # Checking whether the user is logged in
    if "uid" not in session:
        return redirect(url_for("login"))

    # Resolving the permitted receipts directory
    receipts_dir = Path(app.root_path) / "receipts"
    receipts_dir = receipts_dir.resolve()

    # Resolving the requested receipt filename
    requested_file = (receipts_dir / request.args.get("f", "")).resolve()

    # Checking whether the requested file remains inside the receipts directory
    if not requested_file.is_relative_to(receipts_dir):
        return "Forbidden", 403

    # Checking whether the requested path identifies an existing file
    if not requested_file.is_file():
        return "Receipt not found", 404

    # Sending the permitted receipt file
    return send_file(requested_file)



"""
@app.route("/receipt")
def receipt():
    name = request.args.get("f", "")
    return send_file(os.path.join("receipts", name))


@app.route("/export")
def export():
    month = request.args.get("month", "2026-09")
    out = "/tmp/expenses-%s.csv" % month
    subprocess.call(
        "sqlite3 %s '.mode csv' '.once %s' 'SELECT * FROM claims'" % (DB, out),
        shell=True)
    return send_file(out, as_attachment=True)
"""

@app.route("/export")
def export():
    # Checking if the user is logged in
    if "uid" not in session:
        return redirect(url_for("login"))

    # Checking if the user has permission to export all claims
    if session.get("role") not in ("finance", "admin"):
        return "Forbidden", 403

    # Creating an in-memory CSV file
    output = io.StringIO()
    writer = csv.writer(output)

    # Retrieving claim records from the database
    rows = db().execute(
        "SELECT * FROM claims ORDER BY id"
    ).fetchall()

    # Writing the CSV column headings
    writer.writerow(["id", "user_id", "merchant", "amount", "note", "status"])

    # Writing the claim records
    for row in rows:
        writer.writerow([
            row["id"],
            row["user_id"],
            row["merchant"],
            row["amount"],
            row["note"],
            row["status"]
        ])

    # Preparing the CSV file for download
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="expenses.csv"
    )
"""
@app.route("/prefs", methods=["POST"])
def prefs():
    blob = request.form.get("prefs", "")
    data = pickle.loads(bytes.fromhex(blob))
    session["prefs"] = data
    return redirect(url_for("index"))

"""
@app.route("/prefs", methods=["POST"])
def prefs():
    # Checking if the user is logged in
    if "uid" not in session:
        return redirect(url_for("login"))

    # Reading the submitted preferences
    blob = request.form.get("prefs", "")

    # Checking whether the submitted preferences contain valid JSON
    try:
        data = json.loads(blob)
    except (json.JSONDecodeError, TypeError):
        return "Invalid preferences", 400

    # Checking that preferences are stored as a dictionary
    if not isinstance(data, dict):
        return "Invalid preferences", 400

    # Saving the validated preferences in the session
    session["prefs"] = data
    return redirect(url_for("index"))


@app.route("/admin/users")
def admin_users():
    # Checking whether the user is logged in
    if "uid" not in session:
        return redirect(url_for("login"))

    # Checking whether the logged-in user has administrator privileges
    if session.get("role") != "admin":
        return "Forbidden", 403

    # Retrieving user records for the administrator
    rows = db().execute(
        "SELECT id, username, name, role FROM users"
    ).fetchall()

    return render_template("admin.html", users=rows)


"""
@app.route("/admin/users")
def admin_users():
    rows = db().execute("SELECT id, username, name, role FROM users").fetchall()
    return render_template("admin.html", users=rows)


@app.route("/debug/config")
def debug_config():
    return {"secret_key": app.secret_key, "db": DB,
            "env": {k: v for k, v in os.environ.items() if "CCT" in k or "FLASK" in k}}

"""

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
