from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import hashlib
import datetime

app = Flask(__name__)


def hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route('/')
def hello_world():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/auth', methods=['POST'])
def auth():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    username = request.form.get('username')
    password = request.form.get('password')

    c.execute("select * from users where username=? and password=?",
              (username, hash(password)))
    user = c.fetchone()

    conn.close()

    if user is None:
        return render_template('login.html', error="ユーザーネームまたはパスワードが違います")
    else:
        return redirect(url_for('chat', sender=user['username']))


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/create', methods=['POST'])
def create():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    icon = request.files.get('icon')
    icon.save("./static/" + icon.filename)

    username = request.form.get('username')
    password = request.form.get('password')

    try:
        c.execute("insert into users values (?, ?, ?)",
                  (icon.filename, username, hash(password)))
    except sqlite3.IntegrityError:
        return render_template('register.html', error="同じユーザーネームがすでに登録済みです")

    conn.commit()

    conn.close()

    return redirect(url_for('chat', sender=username))


@app.route('/chat/<sender>', methods=['GET', 'POST'])
def chat(sender):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    receiver = request.form.get('receiver')
    text = request.form.get('text')
    if text:
        date = datetime.datetime.now().strftime('%Y年%m月%d日')
        time = datetime.datetime.now().strftime('%H:%M')
        c.execute("insert into messages values (?, ?, ?, ?, ?)",
                  (sender, receiver, text, date, time))

        conn.commit()

    c.execute("select * from messages")
    messages = c.fetchall()

    c.execute("select * from users")
    users = c.fetchall()

    conn.close()

    return render_template('chat.html',
                           messages=messages,
                           sender=sender,
                           users=users)
