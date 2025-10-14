from flask import Flask, render_template, request, session, redirect, url_for, flash
import random
import string
import os

app = Flask(__name__)
app.secret_key = 'secret-key'  
USERS_FILE = 'users.txt'
PASSWORDS_FILE = 'saved_passwords.txt'

def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) >= 2:
                        username = parts[0]
                        password_hash = parts[1]
                        users[username] = {
                            'password': password_hash
                        }
    return users

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        for username, data in users.items():
            f.write(f"{username}:{data['password']}\n")

def save_password_to_file(password, username):
    with open(PASSWORDS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{username}: {password}\n")

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
    
    return render_template('index.html', password=password)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        if username in users and users[username]['password'] == password:
            session['user_id'] = username
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Пароли не совпадают')
            return render_template('register.html')
        
        users = load_users()
        if username in users:
            flash('Пользователь с таким именем уже существует')
            return render_template('register.html')
        
        users[username] = {
            'password': password
        }
        save_users(users)
        
        flash('Регистрация успешна! Теперь вы можете войти в систему.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/save_password', methods=['POST'])
@login_required
def save_password():
    password = request.form.get('password')
    if password:
        save_password_to_file(password, session['username'])
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)