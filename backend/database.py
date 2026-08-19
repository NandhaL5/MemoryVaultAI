import sqlite3

# Connect to SQLite database
conn = sqlite3.connect(
    "memoryvault.db",
    check_same_thread=False
)

cursor = conn.cursor()


# ==========================================
# Memories Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    content TEXT,
    created_at TEXT,
    favorite INTEGER DEFAULT 0
)
""")


# ==========================================
# Add user_id to existing database
# ==========================================

try:
    cursor.execute(
        "ALTER TABLE memories ADD COLUMN user_id INTEGER"
    )
except sqlite3.OperationalError:
    pass


# ==========================================
# Users Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TEXT
)
""")


# ==========================================
# Save changes
# ==========================================

conn.commit()