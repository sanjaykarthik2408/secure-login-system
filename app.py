from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import re

app = Flask(__name__)

# Security Configurations
app.config['SECRET_KEY'] = 'super_secret_cybersecurity_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ---------------------------------------------------------
# Database Model (SQL Injection Protection via ORM)
# ---------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Database Tables Initialization
with app.app_context():
    db.create_all()

# Helper Function: Basic Input Validation
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# ---------------------------------------------------------
# Routes & Controllers
# ---------------------------------------------------------

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# 1. User Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        # Input Validation
        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))

        if not is_valid_email(email):
            flash('Invalid email format!', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('register'))

        # Check if user already exists (ORM parameterized query prevents SQLi)
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or Email already exists!', 'warning')
            return redirect(url_for('register'))

        # Password Hashing using Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Save User to Database
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# 2. User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email'].strip()
        password = request.form['password']

        # Fetch user securely
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        # Verify hashed password
        if user and bcrypt.check_password_hash(user.password, password):
            # Session Management
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

# 3. Protected Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Unauthorized access! Please login first.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', username=session['username'])

# 4. Logout Route
@app.route('/logout')
def logout():
    session.clear() # Clear active session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True) 