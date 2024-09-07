from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "Ahmed123"
app.permanent_session_lifetime = timedelta(days=5)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route("/home")
@app.route("/")
def home_page():
    return render_template("home.html")

@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        user_name = request.form['nm']
        password = request.form['ps']
        confirm_password = request.form['confirm_ps']
        
        if password == confirm_password:
            found_user = User.query.filter_by(username=user_name).first()
            if found_user:
                flash("User Already Exists")
                return render_template("users/signup.html")
            else:
                hashed_password = generate_password_hash(password)
                u1 = User(user_name, hashed_password)
                db.session.add(u1)
                db.session.commit()
                return redirect(url_for("login"))
        else:
            flash("Passwords do not match")
            return render_template("users/signup.html")
    return render_template("users/signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user_name = request.form['nm']
        password = request.form['ps']
        
        user_found = User.query.filter_by(username=user_name).first()
        if user_found and check_password_hash(user_found.password, password):
            session['username'] = user_name
            session['password'] = user_found.password
            session.permanent = True
            flash("Successfully logged in", "info")
            return redirect(url_for('user.profile'))
        else:
            flash("Invalid username or password", "info")
            return render_template("login.html")
    return render_template("login.html")

@app.route("/profile", methods=['GET', 'POST'], endpoint='user.profile')
def show_profile():
    if 'username' in session:
        name = session['username']
        password = session['password']
        return render_template("profile.html", name=name, password=password)
    else:
        flash("Session expired, please log in again", "info")
        return redirect(url_for("login"))


@app.route("/edit_profile", methods=['POST'])
def edit_profile():
    if 'username' in session:
        if request.method == "POST":
            # Get new username and password from the form
            new_username = request.form['new_username']
            new_password = request.form['new_password']
            
            # Hash the new password
            hashed_password = generate_password_hash(new_password)
            
            # Fetch the current user from the database
            user = User.query.filter_by(username=session['username']).first()
            
            # Update the user's data
            if user:
                user.username = new_username
                user.password = hashed_password
                db.session.commit()  # Save changes to the database
                
                # Update session data with the new username and password
                session['username'] = new_username
                session['password'] = hashed_password
                
                flash("Profile updated successfully", "info")
                return redirect(url_for('user.profile'))
    
    # Redirect to login if the user is not in session
    return redirect(url_for("login"))


@app.route("/delete_account", methods=['POST'])
def delete_account():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            session.pop('username')
            session.pop('password')
            flash("Account deleted successfully", "info")
    return redirect(url_for("home_page"))

@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('password', None)
    flash("Logged out successfully", "info")
    return redirect(url_for("home_page"))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/error.html')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
