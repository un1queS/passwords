from flask import Flask, render_template, request, session, redirect, url_for, flash, g
import random
import string
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret-key'  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'app.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            site TEXT DEFAULT '',
            login TEXT DEFAULT '',
            password TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )
    db.commit()

def get_user_by_username(username):
    db = get_db()
    row = db.execute("SELECT id, username, password FROM users WHERE username = ?", (username,)).fetchone()
    if row:
        return {'id': row['id'], 'username': row['username'], 'password': row['password']}
    return None

def create_user(username, password):
    db = get_db()
    try:
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def save_password_to_db(username, password, site="", login=""):
    db = get_db()
    user = get_user_by_username(username)
    if not user:
        return False
    db.execute(
        "INSERT INTO passwords (user_id, site, login, password) VALUES (?, ?, ?, ?)",
        (user['id'], site or '', login or '', password),
    )
    db.commit()
    return True

def load_saved_passwords(username):
    user = get_user_by_username(username)
    if not user:
        return []
    db = get_db()
    rows = db.execute(
        "SELECT site, login, password FROM passwords WHERE user_id = ? ORDER BY id DESC",
        (user['id'],),
    ).fetchall()
    return [{'site': r['site'], 'login': r['login'], 'password': r['password']} for r in rows]

def delete_saved_password(username, site, password, login=""):
    user = get_user_by_username(username)
    if not user:
        return False
    db = get_db()
    db.execute(
        "DELETE FROM passwords WHERE user_id = ? AND IFNULL(site,'') = ? AND IFNULL(login,'') = ? AND password = ?",
        (user['id'], site or '', login or '', password),
    )
    db.commit()
    return True

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def generate_password(length=12, use_uppercase=False, use_lowercase=True, 
                     use_numbers=True, use_special=False):
    characters = ''
    
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_numbers:
        characters += string.digits
    if use_special:
        characters += string.punctuation
    
    if not characters:
        characters = string.ascii_lowercase + string.digits
    
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    password = ""
    saved_passwords = load_saved_passwords(session['username'])
    
    if request.method == 'POST':
        try:
            length = int(request.form.get('length', 12))
            use_uppercase = 'uppercase' in request.form
            use_lowercase = 'lowercase' in request.form
            use_numbers = 'numbers' in request.form
            use_special = 'special' in request.form
            
            
            if length < 4:
                length = 4
            elif length > 50:
                length = 50
            
            password = generate_password(
                length=length,
                use_uppercase=use_uppercase,
                use_lowercase=use_lowercase,
                use_numbers=use_numbers,
                use_special=use_special
            )
            
        except Exception as e:
            password = f"Ошибка: {str(e)}"
    
    return render_template('index.html', password=password, saved_passwords=saved_passwords)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        flash('Неверное имя пользователя или пароль')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if get_user_by_username(username):
            flash('Пользователь с таким именем уже существует')
            return render_template('register.html')
        if create_user(username, password):
            flash('Регистрация успешна! Теперь вы можете войти в систему.')
            return redirect(url_for('login'))
        flash('Ошибка регистрации')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/save_password', methods=['POST'])
@login_required
def save_password():
    password = request.form.get('password')
    site = request.form.get('site', '')
    login = request.form.get('login', '')
    if password:
        save_password_to_db(session['username'], password, site, login)
    return redirect(url_for('index'))

@app.route('/delete_password', methods=['POST'])
@login_required
def delete_password():
    site = request.form.get('site', '') 
    password = request.form.get('password')
    login = request.form.get('login', '')
    print(f"DEBUG: Deleting password for user {session['username']}, site='{site}', login='{login}', password='{password}'")
    if password:  # Убираем проверку на site, так как он может быть пустым
        delete_saved_password(session['username'], site, password, login)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host = '0.0.0.0' , port = 2222)
