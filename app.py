import os,secrets

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


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
    return render_template('index.html')
