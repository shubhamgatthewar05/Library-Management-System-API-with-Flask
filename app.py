from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from database import db
from bson import json_util
import json
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Secure secret key for sessions

def json_response(data, status=200):
    """Convert MongoDB documents to JSON"""
    return app.response_class(
        response=json_util.dumps(data),
        status=status,
        mimetype='application/json'
    )

def login_required(f):
    """Decorator to require login"""
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.get_json()
        user = db.authenticate_user(data['username'], data['password'])
        
        if user:
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user.get('role', 'member')
            return jsonify({'success': True, 'role': session['role']})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        data = request.get_json()
        
        # Check if username or email already exists
        existing_user = db.users_collection.find_one({
            '$or': [
                {'username': data['username']},
                {'email': data['email']}
            ]
        })
        
        if existing_user:
            return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
        
        user_id = db.create_user(
            data['username'], 
            data['email'], 
            data['password']
        )
        
        return jsonify({'success': True, 'user_id': str(user_id)})
    
    return render_template('register.html')

@app.route('/books', methods=['GET', 'POST'])
@login_required
def books():
    """Book management"""
    if request.method == 'POST':
        # Create a new book (admin only)
        if session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        book_id = db.create_book(
            data['title'], 
            data['author'], 
            data.get('isbn', ''), 
            data.get('quantity', 1)
        )
        return jsonify({'book_id': str(book_id)})
    
    # GET: List books with pagination and search
    page = int(request.args.get('page', 1))
    search = request.args.get('search', '')
    result = db.get_books(page=page, search=search)
    
    return json_response(result)

@app.route('/books/<book_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def book_detail(book_id):
    """Book details, update, and delete"""
    if request.method == 'GET':
        book = db.books_collection.find_one({'_id': db.ObjectId(book_id)})
        return json_response(book)
    
    # Require admin permissions for modification
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'PUT':
        data = request.get_json()
        db.books_collection.update_one(
            {'_id': db.ObjectId(book_id)}, 
            {'$set': data}
        )
        return jsonify({'success': True})
    
    if request.method == 'DELETE':
        db.books_collection.delete_one({'_id': db.ObjectId(book_id)})
        return jsonify({'success': True})

@app.route('/loan', methods=['POST'])
@login_required
def loan_book():
    """Loan a book"""
    data = request.get_json()
    loan_id = db.loan_book(
        session['user_id'], 
        data['book_id']
    )
    
    if loan_id:
        return jsonify({'loan_id': str(loan_id), 'success': True})
    return jsonify({'success': False, 'message': 'Book not available'}), 400

@app.route('/return', methods=['POST'])
@login_required
def return_book():
    """Return a book"""
    data = request.get_json()
    success = db.return_book(data['loan_id'])
    
    return jsonify({'success': success})

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

    # Uncomment the following line to create a sample user for testing
    # db.create_user('admin', 'admin@example.com', 'password123', role='admin')