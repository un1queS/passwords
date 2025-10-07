from flask import Flask, render_template, request
import random
import string

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)