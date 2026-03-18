from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import random, string

app = Flask(__name__)

# ================= DATABASE =================
def db():
    return sqlite3.connect("database.db", check_same_thread=False)

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

# ================= HOME =================
@app.route("/")
def home():
    return "AURUM LICENSE SERVER RUNNING ✅"

# ================= VERIFY =================
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

# ================= GENERATOR =================
def generate_key():
    return "AURUM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def get_days(plan):
    return {
        "1day":1,
        "1month":30,
        "2month":60,
        "3month":90,
        "1year":365,
        "2year":730,
        "lifetime":3650
    }.get(plan,30)

# ================= DASHBOARD =================
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    msg = ""

    if request.method == "POST":
        username = request.form.get("username")
        account = request.form.get("account")
        plan = request.form.get("plan")

        key = generate_key()
        expiry = datetime.now() + timedelta(days=get_days(plan))

        conn = db()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO licenses (username,account,license_key,expiry,status)
        VALUES (?,?,?,?,?)
        """,(username,account,key,expiry.strftime("%Y-%m-%d"),"active"))

        conn.commit()

        msg = f"✅ KEY: {key} | EXP: {expiry.strftime('%Y-%m-%d')}"

    return f"""
    <h2>AURUM LICENSE PANEL 🔐</h2>

    <form method="POST">
        Username:<br><input name="username"><br><br>
        Account:<br><input name="account"><br><br>

        Plan:<br>
        <select name="plan">
            <option value="1day">1 Day</option>
            <option value="1month">1 Month</option>
            <option value="2month">2 Month</option>
            <option value="3month">3 Month</option>
            <option value="1year">1 Year</option>
            <option value="2year">2 Year</option>
            <option value="lifetime">Lifetime</option>
        </select><br><br>

        <button>Create License</button>
    </form>

    <p>{msg}</p>
    <hr>
    <a href="/users">VIEW USERS</a>
    """

# ================= USERS =================
@app.route("/users")
def users():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM licenses")
    data = cur.fetchall()

    html = "<h2>USERS</h2><table border=1>"
    html += "<tr><th>User</th><th>Key</th><th>Expiry</th><th>Status</th><th>Action</th></tr>"

    for row in data:
        html += f"""
        <tr>
        <td>{row[1]}</td>
        <td>{row[3]}</td>
        <td>{row[4]}</td>
        <td>{row[5]}</td>
        <td>
            <a href="/pause/{row[3]}">Pause</a> |
            <a href="/delete/{row[3]}">Delete</a> |
            <a href="/renew/{row[3]}">Renew</a>
        </td>
        </tr>
        """

    html += "</table><br><a href='/dashboard'>Back</a>"
    return html

# ================= ACTIONS =================
@app.route("/pause/<key>")
def pause(key):
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE licenses SET status='paused' WHERE license_key=?", (key,))
    conn.commit()
    return "Paused ✅ <br><a href='/users'>Back</a>"

@app.route("/delete/<key>")
def delete(key):
    conn = db()
    cur = conn.cursor()
    cur.execute("DELETE FROM licenses WHERE license_key=?", (key,))
    conn.commit()
    return "Deleted ❌ <br><a href='/users'>Back</a>"

@app.route("/renew/<key>")
def renew(key):
    new_date = datetime.now() + timedelta(days=30)
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE licenses SET expiry=? WHERE license_key=?",
                (new_date.strftime("%Y-%m-%d"), key))
    conn.commit()
    return "Renewed 🔄 <br><a href='/users'>Back</a>"

# ================= RUN =================
app.run(host="0.0.0.0", port=10000)
