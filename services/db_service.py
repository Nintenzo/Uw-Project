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
        final_identity TEXT,
        original_identity TEXT,
        pronouns TEXT,
        bio TEXT,
        headline TEXT,
        location TEXT,
        avatar TEXT,
        remember_user_token TEXT,
        user_session_identifier TEXT,
        memeber_id INTEGER,
        public_uid TEXT,
        community_member_id INTEGER
    )
    """)
    return

def create_db_space():
    conn = sqlite3.connect("spaces.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        space_name TEXT NOT NULL,
        original TEXT NOT NULL,
        space_id INTEGER NOT NULL,
        keywords TEXT NOT NULL,
        context TEXT NOT NULL
    )
    """)
    return conn, cursor

def insert_space(space_name, original, space_id, keywords, context):
    conn, cursor = create_db_space()
    try:
        
        cursor.execute("""
        INSERT INTO spaces (space_name, original, space_id, keywords, context)
        VALUES (?, ?, ?, ?, ?)

        """, (space_name, original, space_id, keywords, context))
        conn.commit()
        print("Data inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    return

def fetch_spaces_id(x):
    conn = sqlite3.connect("spaces.db")
    cursor = conn.cursor()
    data = cursor.execute(f"""
    SELECT {x} FROM spaces
    """)
    return data

def insert_users(name, email, password, final_identity, original_identity, pronouns, bio, headline, location, avatar, remember_user_token, user_session_identifier, memeber_id, public_uid, community_member_id):
    global cursor, conn
    try:
        cursor.execute("""
        INSERT INTO users (name, email, password, final_identity, original_identity, pronouns, bio, headline, location, avatar, remember_user_token, user_session_identifier, memeber_id, public_uid, community_member_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (name, email, password, final_identity, original_identity, pronouns, bio, headline, location, avatar, remember_user_token, user_session_identifier, memeber_id, public_uid, community_member_id ))
        conn.commit()
        print("Data inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    return
