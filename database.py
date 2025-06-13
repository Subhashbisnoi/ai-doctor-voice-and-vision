# database.py
import sqlite3
import os


def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect('medical_history.db')
    c = conn.cursor()

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 full_name TEXT,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )''')

    # Create consultations table (updated schema)
    c.execute('''CREATE TABLE IF NOT EXISTS consultations (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 audio_path TEXT,
                 image_path TEXT,
                 patient_speech TEXT,
                 doctor_response TEXT,
                 audio_response_path TEXT,
                 language TEXT,
                 FOREIGN KEY (user_id) REFERENCES users (id)
                 )''')

    conn.commit()
    conn.close()


def create_user(username, password, full_name):
    """Create a new user in the database"""
    conn = sqlite3.connect('medical_history.db')
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (username, password, full_name) VALUES (?, ?, ?)",
                  (username, password, full_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()


def authenticate_user(username, password):
    """Authenticate a user"""
    conn = sqlite3.connect('medical_history.db')
    c = conn.cursor()

    c.execute("SELECT id, full_name FROM users WHERE username = ? AND password = ?",
              (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return {"user_id": user[0], "full_name": user[1]}
    return None


def save_consultation(user_id, audio_path, image_path, patient_speech, doctor_response, audio_response_path, language):
    """Save a consultation to the database"""
    conn = sqlite3.connect('medical_history.db')
    c = conn.cursor()

    c.execute('''INSERT INTO consultations 
                 (user_id, audio_path, image_path, patient_speech, doctor_response, audio_response_path, language)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (user_id, audio_path, image_path, patient_speech, doctor_response, audio_response_path, language))

    conn.commit()
    conn.close()


def get_user_history(user_id):
    """Retrieve a user's consultation history"""
    conn = sqlite3.connect('medical_history.db')
    c = conn.cursor()

    c.execute('''SELECT id, timestamp, patient_speech, doctor_response, language 
                 FROM consultations 
                 WHERE user_id = ?
                 ORDER BY timestamp DESC''', (user_id,))

    history = []
    for row in c.fetchall():
        history.append({
            "id": row[0],
            "timestamp": row[1],
            "patient_speech": row[2],
            "doctor_response": row[3],
            "language": row[4]
        })

    conn.close()
    print(history)
    return history


# Initialize the database when this module is imported
init_database()