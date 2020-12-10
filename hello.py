from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import hashlib
import datetime

app = Flask(__name__)


@app.route('/')
def hello_world():
    return redirect(url_for('login'))


@app.route('/sum')
def sum():
    return render_template('sum.html')


@app.route('/result')
def result():
    return str(int(request.args.get('a')) + int(request.args.get('b')))


@app.route('/students')
def students():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    # Create table
    c.execute("create table if not exists students "
              "(gakuseki_id, name, nickname)")

    # Insert a row of data
    gakuseki_id = request.args.get('gakuseki_id')
    name = request.args.get('name')
    nickname = request.args.get('nickname')
    c.execute("insert into students values (?, ?, ?)",
              (gakuseki_id, name, nickname))

    # Save (commit) the changes
    conn.commit()

    c.execute("select * from students")
    students = c.fetchall()

    conn.close()

    return render_template('students.html', students=students)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/user', methods=['POST'])
def user():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    username = request.form.get('username')
    password = request.form.get('password')
    c.execute("select * from users where username=? and password=?",
              (username, hashlib.sha256(password.encode()).hexdigest()))
    user = c.fetchone()

    conn.close()

    if user is None:
        return "ユーザーネームまたはパスワードが違います"
    else:
        return redirect(url_for('bbs', sender=user['username']))


@app.route('/register', methods=['POST'])
def register():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    username = request.form.get('username')
    password = request.form.get('password')

    try:
        c.execute("insert into users values (?, ?)",
                  (username, hashlib.sha256(password.encode()).hexdigest()))
    except sqlite3.IntegrityError:
        return "同じユーザーネームがすでに登録済みです"

    conn.commit()

    conn.close()

    return redirect(url_for('bbs', sender=username))


@app.route('/bbs/<sender>', methods=['GET', 'POST'])
def bbs(sender):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    text = request.form.get('text')
    if text:
        date = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        c.execute("insert into messages values (?, ?, ?)",
                  (sender, text, date))

        conn.commit()

    c.execute("select * from messages")
    messages = c.fetchall()

    conn.close()

    return render_template('bbs.html', messages=messages, sender=sender)
