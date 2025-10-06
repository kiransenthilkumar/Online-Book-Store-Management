from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, g
import sqlite3
import os
import hashlib
import secrets
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'bookstore-secret-key-2024'

# Session configuration for better separation
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600
)

def get_db_connection():
    conn = sqlite3.connect('bookstore.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Enhanced session management for simultaneous login
def create_user_session(user, user_type='user'):
    """Create a session with user type differentiation"""
    # Don't clear session - allow multiple logins
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['is_admin'] = bool(user['is_admin'])
    session['user_type'] = user_type
    session['login_time'] = datetime.now().isoformat()
    session.permanent = True

def validate_session():
    """Validate current session"""
    if 'user_id' not in session:
        return False
    
    if 'user_type' not in session:
        session['user_type'] = 'admin' if session.get('is_admin') else 'user'
    
    return True

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not validate_session():
            flash('Please login to access this page', 'error')
            return redirect(url_for('admin_login'))
        
        if not session.get('is_admin') or session.get('user_type') != 'admin':
            flash('Admin access required. Please login as admin.', 'error')
            return redirect(url_for('admin_login'))
        
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not validate_session():
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        
        if session.get('user_type') != 'user':
            flash('Please login as user to access store features', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def public_route(f):
    """Routes that can be accessed by anyone (no login required)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
@public_route
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        conn = get_db_connection()
        
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?', 
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username or email already exists', 'error')
            conn.close()
            return render_template('register.html')
        
        password_hash = hash_password(password)
        conn.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
@public_route
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND is_admin = 0', 
            (username,)
        ).fetchone()
        conn.close()
        
        if user and user['password_hash'] == hash_password(password):
            create_user_session(user, 'user')
            flash('User login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
@public_route
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND is_admin = 1', 
            (username,)
        ).fetchone()
        conn.close()
        
        if user and user['password_hash'] == hash_password(password):
            create_user_session(user, 'admin')
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('admin/login.html')

@app.route('/logout')
def logout():
    username = session.get('username', 'User')
    session.clear()
    flash(f'User {username} has been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/admin/logout')
def admin_logout():
    username = session.get('username', 'Admin')
    session.clear()
    flash(f'Admin {username} has been logged out', 'success')
    return redirect(url_for('admin_login'))

# ==================== SESSION MANAGEMENT ROUTES ====================

@app.route('/session/switch-to-user')
def switch_to_user_mode():
    """Switch session to user mode"""
    if validate_session() and session.get('is_admin'):
        session['user_type'] = 'user'
        flash('Switched to user mode', 'info')
        return redirect(url_for('index'))
    flash('Please login first', 'error')
    return redirect(url_for('login'))

@app.route('/session/switch-to-admin')
def switch_to_admin_mode():
    """Switch session to admin mode"""
    if validate_session() and session.get('is_admin'):
        session['user_type'] = 'admin'
        flash('Switched to admin mode', 'info')
        return redirect(url_for('admin_dashboard'))
    flash('Please login as admin first', 'error')
    return redirect(url_for('admin_login'))

# ==================== PUBLIC ROUTES ====================

@app.route('/')
@public_route
def index():
    conn = get_db_connection()
    
    genres = conn.execute('SELECT DISTINCT genre FROM books WHERE is_active = 1 ORDER BY genre').fetchall()
    
    books_by_genre = {}
    for genre in genres:
        books = conn.execute('''
            SELECT * FROM books 
            WHERE genre = ? AND is_active = 1 
            ORDER BY created_at DESC 
            LIMIT 6
        ''', (genre['genre'],)).fetchall()
        books_by_genre[genre['genre']] = books
    
    featured_books = conn.execute('''
        SELECT * FROM books 
        WHERE is_featured = 1 AND is_active = 1 
        ORDER BY created_at DESC 
        LIMIT 8
    ''').fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                         books_by_genre=books_by_genre,
                         featured_books=featured_books,
                         genres=genres)

@app.route('/books/<genre>')
@public_route
def books_by_genre(genre):
    conn = get_db_connection()
    books = conn.execute('''
        SELECT * FROM books 
        WHERE genre = ? AND is_active = 1 
        ORDER BY title
    ''', (genre,)).fetchall()
    conn.close()
    
    return render_template('books.html', books=books, genre=genre)

@app.route('/book/<int:book_id>')
@public_route
def book_detail(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('index'))
    
    related_books = conn.execute('''
        SELECT * FROM books 
        WHERE genre = ? AND id != ? AND is_active = 1 
        LIMIT 4
    ''', (book['genre'], book_id)).fetchall()
    
    conn.close()
    
    return render_template('book_detail.html', book=book, related_books=related_books)

@app.route('/search')
@public_route
def search():
    query = request.args.get('q', '')
    conn = get_db_connection()
    
    books = conn.execute('''
        SELECT * FROM books 
        WHERE (title LIKE ? OR author LIKE ? OR genre LIKE ?) 
        AND is_active = 1 
        ORDER BY title
    ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    
    conn.close()
    
    return render_template('books.html', books=books, search_query=query)

# ==================== USER PROTECTED ROUTES ====================

@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
@user_required
def add_to_cart(book_id):
    quantity = int(request.form.get('quantity', 1))
    
    conn = get_db_connection()
    
    book = conn.execute('SELECT * FROM books WHERE id = ? AND is_active = 1', (book_id,)).fetchone()
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('index'))
    
    if book['stock'] < quantity:
        flash('Not enough stock available', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    existing_item = conn.execute('''
        SELECT * FROM cart 
        WHERE user_id = ? AND book_id = ?
    ''', (session['user_id'], book_id)).fetchone()
    
    if existing_item:
        conn.execute('''
            UPDATE cart SET quantity = quantity + ? 
            WHERE user_id = ? AND book_id = ?
        ''', (quantity, session['user_id'], book_id))
    else:
        conn.execute('''
            INSERT INTO cart (user_id, book_id, quantity) 
            VALUES (?, ?, ?)
        ''', (session['user_id'], book_id, quantity))
    
    conn.commit()
    conn.close()
    
    flash('Book added to cart successfully', 'success')
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/cart')
@user_required
def cart():
    conn = get_db_connection()
    cart_items = conn.execute('''
        SELECT c.*, b.title, b.author, b.price, b.cover_image, b.stock 
        FROM cart c 
        JOIN books b ON c.book_id = b.id 
        WHERE c.user_id = ? AND b.is_active = 1
    ''', (session['user_id'],)).fetchall()
    
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    
    conn.close()
    
    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount)

@app.route('/remove_from_cart/<int:cart_id>')
@user_required
def remove_from_cart(cart_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM cart WHERE id = ? AND user_id = ?', (cart_id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout')
@user_required
def checkout():
    conn = get_db_connection()
    cart_items = conn.execute('''
        SELECT c.*, b.title, b.author, b.price, b.cover_image, b.stock 
        FROM cart c 
        JOIN books b ON c.book_id = b.id 
        WHERE c.user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))
    
    for item in cart_items:
        if item['stock'] < item['quantity']:
            flash(f'Not enough stock for {item["title"]}', 'error')
            return redirect(url_for('cart'))
    
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    
    conn.close()
    
    return render_template('checkout.html', cart_items=cart_items, total_amount=total_amount)

@app.route('/process_order', methods=['POST'])
@user_required
def process_order():
    payment_method = request.form.get('payment_method')
    shipping_address = request.form.get('shipping_address')
    
    if not shipping_address:
        flash('Please enter shipping address', 'error')
        return redirect(url_for('checkout'))
    
    conn = get_db_connection()
    
    cart_items = conn.execute('''
        SELECT c.*, b.title, b.price, b.stock 
        FROM cart c 
        JOIN books b ON c.book_id = b.id 
        WHERE c.user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))
    
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    
    order_id = conn.execute('''
        INSERT INTO orders (user_id, total_amount, payment_method, shipping_address) 
        VALUES (?, ?, ?, ?)
    ''', (session['user_id'], total_amount, payment_method, shipping_address)).lastrowid
    
    for item in cart_items:
        conn.execute('''
            INSERT INTO order_items (order_id, book_id, quantity, price) 
            VALUES (?, ?, ?, ?)
        ''', (order_id, item['book_id'], item['quantity'], item['price']))
        
        conn.execute('''
            UPDATE books SET stock = stock - ? 
            WHERE id = ?
        ''', (item['quantity'], item['book_id']))
    
    conn.execute('DELETE FROM cart WHERE user_id = ?', (session['user_id'],))
    
    conn.commit()
    conn.close()
    
    session['order_id'] = order_id
    return redirect(url_for('payment'))

@app.route('/payment')
@user_required
def payment():
    if 'order_id' not in session:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (session['order_id'],)).fetchone()
    conn.close()
    
    return render_template('payment.html', order=order)

@app.route('/complete_payment', methods=['POST'])
@user_required
def complete_payment():
    if 'order_id' not in session:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    conn.execute('UPDATE orders SET status = "completed" WHERE id = ?', (session['order_id'],))
    conn.commit()
    
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (session['order_id'],)).fetchone()
    conn.close()
    
    order_id = session.pop('order_id', None)
    
    return render_template('order_confirmation.html', order=order)

@app.route('/profile')
@user_required
def profile():
    conn = get_db_connection()
    
    orders = conn.execute('''
        SELECT o.*, 
               GROUP_CONCAT(b.title) as book_titles,
               SUM(oi.quantity) as total_items
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN books b ON oi.book_id = b.id
        WHERE o.user_id = ?
        GROUP BY o.id
        ORDER BY o.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('profile.html', orders=orders)

# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    
    stats = {
        'total_users': conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0').fetchone()[0],
        'total_books': conn.execute('SELECT COUNT(*) FROM books').fetchone()[0],
        'total_orders': conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0],
        'total_revenue': conn.execute('SELECT SUM(total_amount) FROM orders WHERE status = "completed"').fetchone()[0] or 0,
        'pending_orders': conn.execute('SELECT COUNT(*) FROM orders WHERE status = "pending"').fetchone()[0]
    }
    
    recent_orders = conn.execute('''
        SELECT o.*, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    low_stock_books = conn.execute('''
        SELECT * FROM books 
        WHERE stock < 10 AND is_active = 1 
        ORDER BY stock ASC 
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_orders=recent_orders,
                         low_stock_books=low_stock_books)

@app.route('/admin/books')
@admin_required
def admin_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/books.html', books=books)

@app.route('/admin/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        price = float(request.form['price'])
        genre = request.form['genre']
        stock = int(request.form['stock'])
        cover_image = request.form['cover_image']
        isbn = request.form['isbn']
        publisher = request.form['publisher']
        pages = int(request.form['pages']) if request.form['pages'] else 0
        is_featured = 1 if request.form.get('is_featured') else 0
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO books (title, author, description, price, genre, stock, cover_image, isbn, publisher, pages, is_featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, author, description, price, genre, stock, cover_image, isbn, publisher, pages, is_featured))
        conn.commit()
        conn.close()
        
        flash('Book added successfully', 'success')
        return redirect(url_for('admin_books'))
    
    return render_template('admin/add_book.html')

@app.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        price = float(request.form['price'])
        genre = request.form['genre']
        stock = int(request.form['stock'])
        cover_image = request.form['cover_image']
        isbn = request.form['isbn']
        publisher = request.form['publisher']
        pages = int(request.form['pages']) if request.form['pages'] else 0
        is_featured = 1 if request.form.get('is_featured') else 0
        is_active = 1 if request.form.get('is_active') else 0
        
        conn.execute('''
            UPDATE books SET title=?, author=?, description=?, price=?, genre=?, stock=?, 
            cover_image=?, isbn=?, publisher=?, pages=?, is_featured=?, is_active=?
            WHERE id=?
        ''', (title, author, description, price, genre, stock, cover_image, isbn, publisher, pages, is_featured, is_active, book_id))
        conn.commit()
        conn.close()
        
        flash('Book updated successfully', 'success')
        return redirect(url_for('admin_books'))
    
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    conn.close()
    
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('admin_books'))
    
    return render_template('admin/edit_book.html', book=book)

@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

@app.route('/admin/orders')
@admin_required
def admin_orders():
    status_filter = request.args.get('status', 'all')
    
    conn = get_db_connection()
    
    if status_filter == 'all':
        orders = conn.execute('''
            SELECT o.*, u.username 
            FROM orders o 
            JOIN users u ON o.user_id = u.id 
            ORDER BY o.created_at DESC
        ''').fetchall()
    else:
        orders = conn.execute('''
            SELECT o.*, u.username 
            FROM orders o 
            JOIN users u ON o.user_id = u.id 
            WHERE o.status = ? 
            ORDER BY o.created_at DESC
        ''', (status_filter,)).fetchall()
    
    conn.close()
    
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@app.route('/admin/orders/update_status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    new_status = request.form['status']
    
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()
    conn.close()
    
    flash('Order status updated successfully', 'success')
    return redirect(url_for('admin_orders'))

# ==================== CONTEXT PROCESSOR ====================

@app.context_processor
def inject_user_info():
    """Inject user information into all templates"""
    user_info = {
        'is_logged_in': validate_session(),
        'username': session.get('username'),
        'is_admin': session.get('is_admin', False),
        'user_type': session.get('user_type', 'user'),
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return dict(user_info=user_info)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    conn = get_db_connection()
    conn.rollback()
    conn.close()
    return render_template('500.html'), 500

# ==================== MAIN APPLICATION ====================

if __name__ == '__main__':
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1 FROM users LIMIT 1')
        conn.close()
        print("Database is ready!")
    except sqlite3.OperationalError:
        print("Warning: Database not initialized. Please run 'python init_data.py' first.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)