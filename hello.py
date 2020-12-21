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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
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
            return render_template('login.html',
                                   error="ユーザーネームまたはパスワードが違います")
        else:
            return redirect(url_for('chat', sender=user['username']), code=307)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
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
            return render_template('register.html',
                                   error="同じユーザーネームがすでに登録済みです")

        conn.commit()

        conn.close()

        return redirect(url_for('chat', sender=username), code=307)


@app.route('/chat/<sender>', methods=['POST'])
def chat(sender):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    text = request.form.get('text')

    if text and not text.isspace():
        receiver = request.form.get('receiver')
        date = datetime.datetime.now().strftime('%Y年%m月%d日')
        time = datetime.datetime.now().strftime('%H:%M')

        c.execute("insert into messages values (?, ?, ?, ?, ?)",
                  (sender, text, receiver, date, time))

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
