import sqlite3
import os
import pandas as pd
from datetime import datetime
import streamlit as st
from pathlib import Path
from config import DB_PATH

def ensure_db_directory():
    """Ensure the data directory exists"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_connection():
    """Create a database connection"""
    ensure_db_directory()
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table with location coordinates
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        phone TEXT,
        user_type TEXT NOT NULL, 
        language TEXT DEFAULT 'en',
        location TEXT,
        latitude REAL,
        longitude REAL,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create crops table with location coordinates
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        price REAL NOT NULL,
        location TEXT,
        latitude REAL,
        longitude REAL,
        available BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        image_path TEXT,
        FOREIGN KEY (farmer_id) REFERENCES users (id)
    )
    ''')
    
    # Create transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_id INTEGER NOT NULL,
        buyer_id INTEGER NOT NULL,
        farmer_id INTEGER NOT NULL,
        quantity REAL NOT NULL,
        total_price REAL NOT NULL,
        status TEXT NOT NULL,
        payment_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (crop_id) REFERENCES crops (id),
        FOREIGN KEY (buyer_id) REFERENCES users (id),
        FOREIGN KEY (farmer_id) REFERENCES users (id)
    )
    ''')
    
    # Create contracts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER NOT NULL,
        terms TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (transaction_id) REFERENCES transactions (id)
    )
    ''')
    
    # Create messages table with read status and language
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        original_language TEXT NOT NULL,
        read BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users (id),
        FOREIGN KEY (receiver_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def insert_user(email, password_hash, name, phone, user_type, language, location):
    """Insert a new user into the database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO users (email, password, name, phone, user_type, language, location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (email, password_hash, name, phone, user_type, language, location))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    """Get a user by email"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, user))
    return None

def insert_crop(farmer_id, title, description, quantity, unit, price, location, image_path=None):
    """Insert a new crop into the database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO crops (farmer_id, title, description, quantity, unit, price, location, image_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (farmer_id, title, description, quantity, unit, price, location, image_path))
    conn.commit()
    crop_id = cursor.lastrowid
    conn.close()
    return crop_id

def get_available_crops(search_term=None, min_price=None, max_price=None, location=None):
    """Get available crops with optional filtering"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = '''
    SELECT c.*, u.name as farmer_name, u.location as farmer_location 
    FROM crops c
    JOIN users u ON c.farmer_id = u.id
    WHERE c.available = TRUE
    '''
    
    params = []
    if search_term:
        query += " AND (c.title LIKE ? OR c.description LIKE ?)"
        params.extend([f'%{search_term}%', f'%{search_term}%'])
    
    if min_price is not None:
        query += " AND c.price >= ?"
        params.append(min_price)
    
    if max_price is not None:
        query += " AND c.price <= ?"
        params.append(max_price)
    
    if location:
        query += " AND (c.location LIKE ? OR u.location LIKE ?)"
        params.extend([f'%{location}%', f'%{location}%'])
    
    cursor.execute(query, params)
    crops = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return crops

def get_farmer_crops(farmer_id):
    """Get crops listed by a specific farmer"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM crops WHERE farmer_id = ? ORDER BY created_at DESC
    ''', (farmer_id,))
    crops = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return crops

def create_transaction(crop_id, buyer_id, farmer_id, quantity, total_price, status='pending'):
    """Create a new transaction"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO transactions (crop_id, buyer_id, farmer_id, quantity, total_price, status)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (crop_id, buyer_id, farmer_id, quantity, total_price, status))
    conn.commit()
    transaction_id = cursor.lastrowid
    conn.close()
    return transaction_id

def get_user_transactions(user_id, as_buyer=True):
    """Get transactions for a specific user"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    role_column = 'buyer_id' if as_buyer else 'farmer_id'
    
    cursor.execute(f'''
    SELECT t.*, c.title as crop_title, c.unit, 
           u1.name as buyer_name, u2.name as farmer_name
    FROM transactions t
    JOIN crops c ON t.crop_id = c.id
    JOIN users u1 ON t.buyer_id = u1.id
    JOIN users u2 ON t.farmer_id = u2.id
    WHERE t.{role_column} = ?
    ORDER BY t.created_at DESC
    ''', (user_id,))
    
    transactions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return transactions

def insert_message(sender_id, receiver_id, content, original_language):
    """Insert a new message"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO messages (sender_id, receiver_id, content, original_language)
    VALUES (?, ?, ?, ?)
    ''', (sender_id, receiver_id, content, original_language))
    conn.commit()
    message_id = cursor.lastrowid
    conn.close()
    return message_id

def get_conversation(user1_id, user2_id):
    """Get conversation between two users"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT m.*, u1.name as sender_name, u2.name as receiver_name
    FROM messages m
    JOIN users u1 ON m.sender_id = u1.id
    JOIN users u2 ON m.receiver_id = u2.id
    WHERE (m.sender_id = ? AND m.receiver_id = ?) OR (m.sender_id = ? AND m.receiver_id = ?)
    ORDER BY m.created_at ASC
    ''', (user1_id, user2_id, user2_id, user1_id))
    
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

def create_contract(transaction_id, terms, status='pending'):
    """Create a new contract"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO contracts (transaction_id, terms, status)
    VALUES (?, ?, ?)
    ''', (transaction_id, terms, status))
    conn.commit()
    contract_id = cursor.lastrowid
    conn.close()
    return contract_id

def get_contract(contract_id):
    """Get a specific contract"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.*, t.crop_id, t.buyer_id, t.farmer_id, t.quantity, t.total_price
    FROM contracts c
    JOIN transactions t ON c.transaction_id = t.id
    WHERE c.id = ?
    ''', (contract_id,))
    
    contract = cursor.fetchone()
    if contract:
        contract = dict(contract)
    
    conn.close()
    return contract

def update_user_language(user_id, language):
    """Update a user's preferred language"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE id = ?', (language, user_id))
    conn.commit()
    conn.close()
    return True

def update_payment_status(transaction_id, payment_id, status):
    """Update payment status for a transaction"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE transactions 
    SET payment_id = ?, status = ? 
    WHERE id = ?
    ''', (payment_id, status, transaction_id))
    conn.commit()
    conn.close()
    return True

def update_crop_availability(crop_id, available):
    """Update crop availability"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE crops SET available = ? WHERE id = ?', (available, crop_id))
    conn.commit()
    conn.close()
    return True

def get_user_contacts(user_id):
    """Get all users that the current user has messaged with"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT DISTINCT u.id, u.name, u.email
    FROM users u
    JOIN messages m ON (u.id = m.sender_id OR u.id = m.receiver_id)
    WHERE (m.sender_id = ? OR m.receiver_id = ?) AND u.id != ?
    ''', (user_id, user_id, user_id))
    
    contacts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return contacts

def delete_crop(crop_id):
    """Delete a crop from the database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # First get the image path to delete the image file if it exists
        cursor.execute('SELECT image_path FROM crops WHERE id = ?', (crop_id,))
        result = cursor.fetchone()
        if result and result[0]:
            image_path = result[0]
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete the crop record
        cursor.execute('DELETE FROM crops WHERE id = ?', (crop_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting crop: {e}")
        return False
    finally:
        conn.close()

def get_all_farmers():
    """Get all farmers in the system"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, name, email, phone, location 
    FROM users 
    WHERE user_type = 'farmer'
    ORDER BY name
    ''')
    farmers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return farmers

def get_all_buyers():
    """Get all buyers in the system"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, name, email, phone, location 
    FROM users 
    WHERE user_type = 'buyer'
    ORDER BY name
    ''')
    buyers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return buyers
def get_user_contacts(user_id, user_type):
    """Get all available contacts based on user type"""
    if user_type == 'farmer':
        return get_all_buyers()
    else:
        return get_all_farmers()
