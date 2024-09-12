from flask import render_template, redirect, url_for, flash, request, session, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from app.models import User, Book
import io

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Try a different one.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, password=generate_password_hash(password), is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()

        flash('Registered successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    books = user.books if user else []
    return render_template('dashboard.html', user=user, books=books)

@app.route("/add_book", methods=['GET', 'POST'])
def add_book():
    if 'user_id' not in session:
        flash('Please log in to add a book.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        image = request.files.get('image')
        image_data = image.read() if image else None

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
    else:
        return '', 404

@app.route("/")
def home():
    return render_template('home.html')
