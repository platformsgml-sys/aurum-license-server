from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

def db():
    return sqlite3.connect("database.db", check_same_thread=False)

# create table
conn = db()
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS licenses (
id INTEGER PRIMARY KEY,
username TEXT,
account TEXT,
license_key TEXT,
expiry TEXT,
status TEXT
)
""")

conn.commit()

@app.route("/")
def home():
    return "AURUM SERVER LIVE ✅"

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    key = data.get("license")

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM licenses WHERE license_key=?", (key,))
    row = cur.fetchone()

    if not row:
        return jsonify({"status": "INVALID"})

    expiry = datetime.strptime(row[4], "%Y-%m-%d")

    if datetime.now() > expiry:
        return jsonify({"status": "EXPIRED"})

    if row[5] == "paused":
        return jsonify({"status": "PAUSED"})

    return jsonify({"status": "VALID"})

@app.route("/dashboard")
def dashboard():
    return "DASHBOARD COMING SOON"

app.run(host="0.0.0.0", port=10000)
