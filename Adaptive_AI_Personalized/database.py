import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())

    # Migration check for new column
    try:
        conn.execute("SELECT is_leaderboard_hidden FROM users LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE users ADD COLUMN is_leaderboard_hidden INTEGER DEFAULT 0")

    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db_connection()
    cur = conn.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def create_user(name, email, password, role='student'):
    password_hash = generate_password_hash(password)
    return execute_db(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, role)
    )

def get_user_by_email(email):
    return query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)

def get_user_by_id(user_id):
    return query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)

def verify_password(stored_hash, password):
    return check_password_hash(stored_hash, password)
