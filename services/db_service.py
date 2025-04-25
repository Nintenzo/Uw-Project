import sqlite3


def create_db_users():
    conn = sqlite3.connect("circle_users.db")
    cursor = conn.cursor()
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
    return conn, cursor


def insert_users(name, email, password, final_identity, original_identity, pronouns, bio, headline, location, avatar, remember_user_token, user_session_identifier, memeber_id, public_uid, community_member_id):
    conn, cursor = create_db_users()
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


def create_post_db():
    conn = sqlite3.connect("reddit_scrap.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_title TEXT,
        original_description TEXT,
        ai_title TEXT,
        ai_description TEXT,
        post_id INTEGER,
        space_id INTEGER,
        links TEXT NOT NULL,
        needed_likes INTEGER,
        needed_comments INTEGER
    )
    """)
    return conn, cursor


def insert_post(original_title, original_description, ai_title, ai_description, post_id, space_id, links, needed_likes, needed_comments):
    conn, cursor = create_post_db()
    try:

        cursor.execute("""
        INSERT INTO posts (original_title, original_description, ai_title, ai_description, post_id, space_id, links, needed_likes, needed_comments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (original_title, original_description, ai_title, ai_description, post_id, space_id, links, needed_likes, needed_comments))
        conn.commit()
        print("Data inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    return

def fetch_posts():
    conn, cursor = create_post_db()
    cursor.execute("""
    SELECT * FROM posts
    WHERE needed_likes >= 0""")
    result = cursor.fetchall()
    return result

def fetch_post_byID(post_id):
    conn, cursor = create_post_db()
    cursor.execute(f"""
    SELECT * FROM posts
    WHERE post_id = {post_id}""")
    result = cursor.fetchone()
    return result

def check_if_posted(link, cursor):
    """Checks if a post with the given link and a non-null post_id exists."""
    sql = (
        "SELECT EXISTS (SELECT 1 FROM posts "
        "WHERE links = ? AND post_id IS NOT NULL)"
    )
    try:
        cursor.execute(sql, (link,))
        exists = cursor.fetchone()[0]
        return exists == 1
    except sqlite3.Error as e:
        print(f"Error checking link existence: {e}")
        return False

def decrement_likes_comments(post_id, value):
    conn, cursor = create_post_db()
    cursor.execute(f"""
    UPDATE posts
    SET {value} = {value} - 1
    WHERE post_id = {post_id}
    """)
    conn.commit()
    cursor.close()
    conn.close()

def get_gender(email):
    conn = sqlite3.connect("circle_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT final_identity, original_identity FROM users WHERE email = ?", (email,))
    identity = cursor.fetchall()
    return identity

def get_user_cookies(email):
	conn, cursor = create_db_users()
	cursor.execute("""
		SELECT remember_user_token, user_session_identifier FROM users
		WHERE email = ?
	""", (email,))
	cookies = cursor.fetchall()
	return cookies

def get_user_password(email):
    conn = sqlite3.connect("circle_users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    return result

def update_cookies(remember_user_token, user_session_identifier, email):
    conn = sqlite3.connect("circle_users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET remember_user_token = ?, user_session_identifier = ? WHERE email = ?",
        (remember_user_token, user_session_identifier, email))
    conn.commit()
    print("cookies updated")
    return


def get_random_user_email():
    """Fetches a random email from the users table."""
    conn = None
    try:
        conn = sqlite3.connect("circle_users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print("Warning: No users found in the database.")
            return None
    except sqlite3.Error as e:
        print(f"Database error fetching random email: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_users_count():
    try:
        conn = sqlite3.connect("circle_users.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        return count
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()
