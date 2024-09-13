from flask import render_template, redirect, url_for, flash, request, session, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from app.models import User, Book
import io

# Ensure admin account exists
def ensure_admin_account():
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', password=generate_password_hash('admin'), is_admin=True)
        db.session.add(admin_user)
        db.session.commit()

# Initialize the app by ensuring the admin account exists
@app.before_request
def initialize():
    ensure_admin_account()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        # Create a new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find the user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))

    # Retrieve the user from the database using the session user_id
    user = User.query.get(session['user_id'])
    
    # Retrieve the books associated with the user
    books = Book.query.filter_by(user_id=user.id).all()

    return render_template('dashboard.html', user=user, books=books)



@app.route("/add_book", methods=['GET', 'POST'])
def add_book():
    if 'user_id' not in session:
        flash('Please log in to add a book.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        image = request.files.get('image')
        
        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('add_book'))

        # Handle image file
        image_data = None
        if image and image.filename:
            image_data = image.read()

        # Create new book and add to database
        new_book = Book(title=title, image=image_data, user_id=session['user_id'])
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('addbook.html')


@app.route("/remove_book/<int:book_id>")
def remove_book(book_id):
    if 'user_id' not in session:
        flash('Please log in to remove a book.', 'danger')
        return redirect(url_for('login'))

    book = Book.query.get(book_id)
    if book and book.user_id == session['user_id']:
        db.session.delete(book)
        db.session.commit()
        flash('Book removed successfully!', 'success')
    else:
        flash('You do not have permission to remove this book.', 'danger')
    return redirect(url_for('dashboard'))

@app.route("/admin")
def admin_dashboard():
    if 'is_admin' not in session or not session['is_admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    users = User.query.all()
    books = Book.query.all()
    return render_template('admindashboard.html', users=users, books=books)

@app.route("/admin/edit_user/<int:user_id>", methods=['GET', 'POST'])
def edit_user(user_id):
    if 'is_admin' not in session or not session['is_admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form['username']
        is_admin = 'is_admin' in request.form
        user.username = username
        user.is_admin = is_admin
        db.session.commit()
        flash('User details updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_user.html', user=user)

@app.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):
    if 'is_admin' not in session or not session['is_admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/edit_book/<int:book_id>", methods=['GET', 'POST'])
def edit_book(book_id):
    if 'is_admin' not in session or not session['is_admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        title = request.form['title']
        image = request.files.get('image')
        book.title = title
        if image and image.filename:
            book.image = image.read()
        db.session.commit()
        flash('Book details updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_book.html', book=book)

@app.route("/admin/delete_book/<int:book_id>")
def delete_book(book_id):
    if 'is_admin' not in session or not session['is_admin']:
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('login'))

    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route("/book_image/<int:book_id>")
def book_image(book_id):
    book = Book.query.get_or_404(book_id)
    if book.image:
        return send_file(io.BytesIO(book.image), mimetype='image/jpeg')
    return '', 404

@app.route("/")
def home():
    return render_template('home.html')
