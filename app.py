from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import pyshorteners

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLAlchemy for SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///chotu.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define your User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hash = db.Column(db.String(128), nullable=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle form submission
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the database for the user
        user = db.execute("SELECT * FROM chotu_users WHERE username = ?", username)

        # Check if the user exists and the password is correct
        if user and check_password_hash(user[0]['hash'], password):
            flash(f"Login successful for {username}")

            # Set the session variable to indicate the user is logged in
            session['user_id'] = user[0]['id']

            # Redirect to the /index route
            return redirect(url_for('index'))
        else:
            flash(f"Invalid Credentials.. try again")
            return redirect(url_for('login'))

    # If it's a GET request, just render the login page
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle form submission
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return render_template('register.html')

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert user information into the database using SQLAlchemy
        new_user = User(username=username, hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash(f"Registration successful for {username}")
        return redirect(url_for('login'))

    # If it's a GET request, just render the registration page
    return render_template('register.html')


# Update the /index route in your Flask app
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle form submission and generate the shortened URL
        long_url = request.form.get('long_url')
        tag = request.form.get('tag')
        user_id = session.get('user_id')

        # Generate the shortened URL and retrieve previous transactions
        shortened_url, previous_transactions = generate_short_url(long_url, tag, user_id)

        # Fetch all transactions for the current user from the database
        all_transactions = db.execute(
            "SELECT original_url, short_url, tag FROM chotu_transactions WHERE user_id = ?",
            user_id
        )

        return render_template('index.html', shortened_url=shortened_url, previous_transactions=all_transactions)

    # If it's a GET request or the form is not submitted, just render the index page

    # Retrieve previous transactions for the current user from the database
    user_id = session.get('user_id')
    previous_transactions = db.execute(
        "SELECT original_url, short_url, tag FROM chotu_transactions WHERE user_id = ?",
        user_id
    )

    return render_template('index.html', previous_transactions=previous_transactions)



def generate_short_url(long_url, tag, user_id):
    # Check if the user_id exists in the users table
    user_exists = db.execute("SELECT id FROM chotu_users WHERE id = ?", user_id)

    if not user_exists:
        # Handle the case where the user_id does not exist (e.g., redirect to login)
        flash("User not found. Please log in.")
        return None, None

    print(f"User ID exists: {user_id}")

    # Your existing code to generate a short URL
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(long_url)

    print(f"Generated Short URL: {short_url}")

    # Check if the short URL already exists in the database
    existing_url = db.execute("SELECT * FROM chotu_transactions WHERE short_url = ?", short_url)

    print(f"Existing URL: {existing_url}")

    # If the short URL already exists, generate a new one
    while existing_url:
        short_url = s.tinyurl.short(long_url)
        existing_url = db.execute("SELECT * FROM chotu_transactions WHERE short_url = ?", short_url)

        print(f"Regenerated Short URL: {short_url}")

    try:
        # Save the transaction to the database
        db.execute(
            "INSERT INTO chotu_transactions (date, original_url, short_url, tag, user_id) VALUES (CURRENT_DATE, ?, ?, ?, ?)",
            long_url, short_url, tag, user_id
        )

        print("Transaction saved to the database.")

        # Retrieve previous transactions from the database for the current user
        previous_transactions = db.execute(
            "SELECT original_url, short_url, tag FROM chotu_transactions WHERE user_id = ?",
            user_id
        )

        print(f"Previous Transactions: {previous_transactions}")

        return short_url, previous_transactions

    except Exception as e:
        print(f"Error saving transaction: {e}")
        return None, None



@app.route('/')
def main_route():
    return redirect("/login")




@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

if __name__ == '__main__':
    app.run(debug=True)
