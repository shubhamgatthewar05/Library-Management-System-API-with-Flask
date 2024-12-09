import pymongo
from bson import ObjectId
from datetime import datetime, timedelta
import hashlib
import os

class Database:
    def __init__(self, connection_string = 'mongodb://localhost:27017/', database_name = 'library_management'):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[database_name]

        #Collections in databse
        self.book_collection = self.db['books']
        self.users_collection = self.db['users']
        self.loans_collection = self.db['loans']


        #indexes for 
        self.book_collection.create_index([('title', pymongo.TEXT), ('author', pymongo.TEXT)])

    def hash_password(self,password):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt , 100000)
        return salt + key
    
    def verify_password(self,stored_password, provided_password):
        salt = stored_password[:32]
        stored_key = stored_password[32:]
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt,100000)

        return stored_key == new_key
    
    def create_book(self,title, author, ishon, quantity):
        book = {
            'title': title,
            'author': author,
            'ishon': ishon,
            'quantity': quantity,
            'available_quantity' :quantity
        }
        return self.book_collection.insert_one(book).inserted_id
    
    def get_books(self, page = 1, limit = 10, search = None):
        skip =(page - 1) * limit
        query = {}

        if search:
            query['$text'] = {'$search': search}
        
        total_books = self.books_collection.count_documents(query)
        books = list(self.book_collection.find(query).skip(skip).limit(limit))

        return {
            'books': books,
            'total_pages': (total_books + limit - 1) // limit,
            'current_page': page
        }


    def create_user(self, username, email, password, role='member'):
            """Create a new user"""
            user = {
            'username': username,
            'email': email,
            'password': self.hash_password(password),
            'role': role,
            'created_at': datetime.utcnow()
        }
            return self.users_collection.insert_one(user).inserted_id
    
    def authenticate_user(self, username, password):
        """Authenticate user"""
        user = self.users_collection.find_one({'username': username})
        if user and self.verify_password(user['password'], password):
            return user
        return None
    
    def loan_book(self, user_id, book_id, days=14):
        """Create a book loan"""
        # Check book availability
        book = self.books_collection.find_one({'_id': ObjectId(book_id)})
        if not book or book['available_quantity'] < 1:
            return False
        
        # Create loan
        loan = {
            'user_id': ObjectId(user_id),
            'book_id': ObjectId(book_id),
            'loan_date': datetime.utcnow(),
            'return_date': datetime.utcnow() + timedelta(days=days),
            'status': 'active'
        }
        
        # Decrease available quantity
        self.books_collection.update_one(
            {'_id': ObjectId(book_id)}, 
            {'$inc': {'available_quantity': -1}}
        )
        
        return self.loans_collection.insert_one(loan).inserted_id
    
    def return_book(self, loan_id):
        """Process book return"""
        loan = self.loans_collection.find_one({'_id': ObjectId(loan_id)})
        if not loan:
            return False
        
        # Increase book availability
        self.books_collection.update_one(
            {'_id': loan['book_id']}, 
            {'$inc': {'available_quantity': 1}}
        )
        
        # Update loan status
        self.loans_collection.update_one(
            {'_id': ObjectId(loan_id)}, 
            {'$set': {'status': 'returned', 'return_date': datetime.utcnow()}}
        )
        
        return True

# Initialize database
db = Database()

    