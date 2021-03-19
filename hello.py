import datetime
import hashlib
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "app secret key"


def hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/")
def hello_world():
    return redirect(url_for("chat"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row

        c = conn.cursor()

        username = request.form.get("username")
        password = request.form.get("password")

        c.execute(
            "select * from users where username=? and password=?",
            (username, hash(password)),
        )
        user = c.fetchone()

        conn.close()

        if user is None:
            error = "ユーザーネームまたはパスワードが違います"
            return render_template("login.html", error=error)
        else:
            session["username"] = user["username"]
            return redirect(url_for("chat"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row

        c = conn.cursor()

        icon = request.files.get("icon")
        icon.save("./static/" + icon.filename)

        username = request.form.get("username")
        password = request.form.get("password")

        try:
            c.execute(
                "insert into users values (?, ?, ?)",
                (icon.filename, username, hash(password)),
            )
        except sqlite3.IntegrityError:
            error = "同じユーザーネームがすでに登録済みです"
            return render_template("register.html", error=error)

        conn.commit()

        conn.close()

        session["username"] = username
        return redirect(url_for("chat"))


@app.route("/chat")
def chat():
    if "username" in session:
        username = session["username"]

        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row

        c = conn.cursor()

        c.execute("select * from messages")
        messages = c.fetchall()

        c.execute("select * from users")
        users = c.fetchall()

        conn.close()

        return render_template(
            "chat.html", username=username, messages=messages, users=users
        )
    else:
        return redirect(url_for("login"))


@app.route("/send", methods=["POST"])
def send():
    text = request.form.get("text")

    if text and not text.isspace():
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row

        c = conn.cursor()

        sender = request.form.get("sender")
        receiver = request.form.get("receiver")
        date = datetime.datetime.now().strftime("%Y年%m月%d日")
        time = datetime.datetime.now().strftime("%H:%M")

        c.execute(
            "insert into messages values (?, ?, ?, ?, ?)",
            (sender, receiver, text, date, time),
        )

        conn.commit()

        conn.close()

    return redirect(url_for("chat"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("chat"))
