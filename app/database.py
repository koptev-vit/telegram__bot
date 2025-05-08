import sqlite3
import random
import string

def init_db():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    # Таблица пользователей
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            role TEXT DEFAULT 'resident',
            house_number INTEGER,
            apartment TEXT
        )
    ''')

    # Таблица кодов доступа
    cur.execute('''
        CREATE TABLE IF NOT EXISTS access_codes (
            code TEXT PRIMARY KEY,
            used INTEGER DEFAULT 0
        )
    ''')

    # Таблица заявок
    cur.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            source TEXT,
            method TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()

def is_code_valid(code):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT used FROM access_codes WHERE code=?", (code,))
    row = cur.fetchone()
    conn.close()
    return row is not None and row[0] == 0

def mark_code_used(code):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("UPDATE access_codes SET used=1 WHERE code=?", (code,))
    conn.commit()
    conn.close()

def add_user(user_id, full_name, house_number, apartment, role='resident'):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT OR REPLACE INTO users (user_id, full_name, house_number, apartment, role)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, full_name, house_number, apartment, role))
    conn.commit()
    conn.close()

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def add_access_code(code):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO access_codes (code) VALUES (?)", (code,))
    conn.commit()
    conn.close()

def add_request(user_id, r_type, source, method):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO requests (user_id, type, source, method, status)
        VALUES (?, ?, ?, ?, 'new')
    ''', (user_id, r_type, source, method))
    
    conn.commit()
    conn.close()
