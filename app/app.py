"""FlightDesk: a deliberately vulnerable demo app for a DevSecOps pipeline lab.

Every flaw marked PLANTED was added on purpose so the scanners have something
to find. Fictional data only. Never deploy this anywhere.
"""
import html
import os
import sqlite3

from flask import Flask, request

app = Flask(__name__)
app.secret_key = "flightdesk-dev-secret"  # PLANTED: hardcoded secret

conn = sqlite3.connect(":memory:", check_same_thread=False)
conn.execute("CREATE TABLE flights (number TEXT, origin TEXT, destination TEXT, status TEXT)")
conn.executemany(
    "INSERT INTO flights VALUES (?, ?, ?, ?)",
    [
        ("FD100", "SEA", "ANC", "On time"),
        ("FD205", "SFO", "SEA", "Delayed"),
        ("FD310", "LAX", "PDX", "On time"),
    ],
)


@app.route("/")
def index():
    return (
        "<h1>FlightDesk</h1>"
        "<p><a href='/flight?number=FD100'>Look up a flight</a></p>"
        "<p><a href='/search?q=SEA'>Search airports</a></p>"
    )


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/flight")
def flight():
    number = request.args.get("number", "")
    rows = conn.execute(
        "SELECT number, origin, destination, status FROM flights WHERE number = ?",
        (number,),
    ).fetchall()
    return {"results": rows}


@app.route("/search")
def search():
    q = request.args.get("q", "")
    return "<h2>Results for " + html.escape(q) + "</h2>"


if __name__ == "__main__":
    # Debug stays off. Listen on localhost unless the container sets FLASK_HOST.
    app.run(host=os.environ.get("FLASK_HOST", "127.0.0.1"), port=5000, debug=False)
