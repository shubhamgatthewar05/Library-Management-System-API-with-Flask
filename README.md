# **Library Management System API with Flask**

This is a web application that implements a **Library Management System** with CRUD operations for books and members, authentication via JSON Web Tokens (JWT), and a user-friendly interface. It uses **MongoDB** for the database.

---

## **Features**
1. **User Roles**:
   - Admins: Manage books (add, delete, view).
   - Users: View and search books.
2. **Authentication**:
   - JWT-based authentication for secure access.
3. **CRUD Functionality**:
   - Add, view, and search books.
4. **Search Functionality**:
   - Search for books by title or author.
5. **Responsive Design**:
   - Includes registration, login, admin dashboard, and user views.

---

## **How to Run the Project**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-github-username/library-management-system.git
cd library-management-system
```

### **2. Set Up the Environment**
- Install Python (3.8 or later) and ensure it's added to your PATH.
- Install MongoDB and ensure the service is running locally.

### **3. Install Dependencies**
Set up a virtual environment and install required Python packages:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### **4. Configure the Project**
- Create a `config.py` file in the root directory with the following:
```python
MONGO_URI = "mongodb://localhost:27017/library_db"
JWT_SECRET_KEY = "your_jwt_secret_key"
```

- Replace `your_jwt_secret_key` with a secure, randomly generated key.

### **5. Run the Application**
Start the Flask server:
```bash
python app.py
```

- Access the application at `http://127.0.0.1:5000`.

### **6. Interact with the Application**
1. Register as a user (via `/register`).
2. Log in as a user or admin (via `/login`).
3. Admin access: Manage books (add, view).
4. User access: Search and view books.

---

## **Design Choices**

### **Backend Framework**:
- **Flask**: Lightweight and flexible for building REST APIs.

### **Database**:
- **MongoDB**: A NoSQL database for its ease of use and schema flexibility.

### **Authentication**:
- **JWT**: Ensures secure, stateless authentication.

### **Frontend**:
- Basic HTML/CSS for simplicity and demonstration purposes.

---

## **Assumptions and Limitations**

### **Assumptions**:
1. Admin users are pre-registered in the system (manual entry in the `users` collection).
2. The application is deployed locally for demonstration purposes.

### **Limitations**:
1. Pagination is not implemented for viewing books.
2. No role-based access control in the frontend (role enforcement is backend-driven).
3. The `members` collection is unused in the current implementation.
4. This project does not include Docker or deployment configurations.





