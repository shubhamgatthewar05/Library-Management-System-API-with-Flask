from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

mongo = PyMongo(app)
jwt = JWTManager(app)

# Collection references
users = mongo.db.users
books = mongo.db.books
members = mongo.db.members

# Routes

# 1. Home route
@app.route('/')
def home():
    return render_template('login.html')

# 2. User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if users.find_one({'username': username}):
            return "User already exists!"
        users.insert_one({'username': username, 'password': password, 'role': 'user'})
        return redirect('/login')
    return render_template('register.html')

# 3. Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            token = create_access_token(identity={'username': username, 'role': user['role']}, expires_delta=timedelta(days=1))
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        return "Invalid credentials"
    return render_template('login.html')

# 4. Admin Dashboard
@app.route('/admin_dashboard')
@jwt_required()
def admin_dashboard():
    return render_template('admin_dashboard.html')

# 5. User Dashboard
@app.route('/user_dashboard')
@jwt_required()
def user_dashboard():
    all_books = books.find()
    return render_template('view_books.html', books=all_books)

# 6. Add Book
@app.route('/add_book', methods=['GET', 'POST'])
@jwt_required()
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        books.insert_one({'title': title, 'author': author})
        return redirect('/admin_dashboard')
    return render_template('add_book.html')

# 7. View Books
@app.route('/view_books')
def view_books():
    all_books = books.find()
    return render_template('view_books.html', books=all_books)

# 8. Search Books
@app.route('/search_books', methods=['GET'])
def search_books():
    query = request.args.get('query')
    result = books.find({'$or': [{'title': {'$regex': query, '$options': 'i'}}, {'author': {'$regex': query, '$options': 'i'}}]})
    return render_template('view_books.html', books=result)

if __name__ == '__main__':
    app.run(debug=True)
