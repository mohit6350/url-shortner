import secrets, hashlib
import pyshorteners

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
type_tiny = pyshorteners.Shortener()
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chotu.db'  # Change the database name if needed
db = SQLAlchemy(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle form submission
        username = request.form.get('username')
        password = request.form.get('password')

        # Add your authentication logic here (e.g., check against a database)
        # check with temp data
        if username.lower() == 'mohit' and password == 'mohit123':
            flash(f"Login successful for {username}")
            return redirect(url_for('index'))
        else:
            flash(f"Invalid Credientials.. try again")
            return render_template('login.html')

    # If it's a GET request, just render the login page
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle form submission and generate the shortened URL
        long_url = request.form.get('long_url')
        
        # Add your logic to generate the shortened URL (this can be a function or an API call)
        shortened_url = generate_short_url(long_url)
        
        return render_template('index.html', shortened_url=shortened_url)

    # If it's a GET request or the form is not submitted, just render the index page
    return render_template('index.html')

def generate_short_url(long_url):
    short_url = type_tiny.tinyurl.short(long_url)
    return short_url

