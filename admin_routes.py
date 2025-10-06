from app import app, get_db_connection, admin_required
from flask import render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    
    # Get dashboard stats
    stats = {
        'total_users': conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0').fetchone()[0],
        'total_books': conn.execute('SELECT COUNT(*) FROM books').fetchone()[0],
        'total_orders': conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0],
        'total_revenue': conn.execute('SELECT SUM(total_amount) FROM orders WHERE status = "completed"').fetchone()[0] or 0,
        'pending_orders': conn.execute('SELECT COUNT(*) FROM orders WHERE status = "pending"').fetchone()[0]
    }
    
    # Recent orders
    recent_orders = conn.execute('''
        SELECT o.*, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    # Low stock books
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

# Manage Books
@app.route('/admin/books')
@admin_required
def admin_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/books.html', books=books)

# Add New Book
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
        pages = int(request.form['pages'])
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

# Edit Book
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
        pages = int(request.form['pages'])
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

# Manage Users
@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

# Manage Orders
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

# Update Order Status
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