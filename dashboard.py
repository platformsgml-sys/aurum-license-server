from flask import Flask, request, render_template_string
import sqlite3, random, string
from datetime import datetime, timedelta

app = Flask(__name__)

def db():
    return sqlite3.connect("database.db", check_same_thread=False)

def gen_key():
    return "AURUM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def get_days(opt):
    return {
        "1day":1,
        "1month":30,
        "3month":90,
        "1year":365,
        "lifetime":3650
    }.get(opt,30)

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        account = request.form["account"]
        plan = request.form["plan"]

        key = gen_key()
        expiry = datetime.now() + timedelta(days=get_days(plan))

        conn = db()
        cur = conn.cursor()
        cur.execute("INSERT INTO licenses (username,account,license_key,expiry,status) VALUES (?,?,?,?,?)",
                    (username,account,key,expiry.strftime("%Y-%m-%d"),"active"))
        conn.commit()

        msg = f"KEY: {key} | EXP: {expiry}"

    return render_template_string("""
    <h2>AURUM LICENSE PANEL</h2>

    <form method="POST">
        Username:<br><input name="username"><br>
        Account:<br><input name="account"><br>

        Plan:<br>
        <select name="plan">
            <option value="1day">1 Day</option>
            <option value="1month">1 Month</option>
            <option value="3month">3 Month</option>
            <option value="1year">1 Year</option>
            <option value="lifetime">Lifetime</option>
        </select><br><br>

        <button>Create License</button>
    </form>

    <p>{{msg}}</p>
    """, msg=msg)
