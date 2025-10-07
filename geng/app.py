from flask import Flask, render_template, request, jsonify
import random
import string

app = Flask(__name__)

def generate_password(length=12, use_uppercase=True, use_lowercase=True, 
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
        characters = string.ascii_letters + string.digits
    
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        length = int(request.form.get('length', 12))
        use_uppercase = request.form.get('uppercase') == 'true'
        use_lowercase = request.form.get('lowercase') == 'true'
        use_numbers = request.form.get('numbers') == 'true'
        use_special = request.form.get('special') == 'true'
        
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
        
        return jsonify({'password': password})
    
    except Exception as e:
        return jsonify

if __name__ == '__main__':
    app.run(debug=True)