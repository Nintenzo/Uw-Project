import sqlite3
conn = sqlite3.connect("circle_users.db")
cursor = conn.cursor()


def create_db():
    global cursor, conn
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT,
        bio TEXT,
        headline TEXT,
        avatar TEXT,
        remember_user_token TEXT,
        user_session_identifier TEXT
    )
    """)
    return


def insert_users(name, email, password, bio, headline, avatar, remember_user_token, user_session_identifier):
    global cursor, conn
    try:
        cursor.execute("""
        INSERT INTO users (name, email, password, bio, headline, avatar,remember_user_token,user_session_identifier)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        """, (name, email, password, bio, headline, avatar, remember_user_token, user_session_identifier))
        conn.commit()
        print("Data inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    return
