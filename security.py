import hashlib
import hmac
import secrets
import sqlite3

from database import DB_PATH

ITERATIONS =  600_000

def make_password_hash(password,salt,iterations):
    return hashlib.pbkdf2_hmac("sha256",password.encode("utf-8"),salt,iterations)

def has_staff_accounts():
    connection = sqlite3.connect(DB_PATH)
    
    try:
        row = connection.execute( "SELECT 1 FROM staff LIMIT 1").fetchone()
        return row is not None
    finally:
        connection.close()
def create_first_account(username,password):
    username = username.strip()
    
    if not username:
        raise ValueError("Enter a username.")
    
    if len(password) < 12:
        raise ValueError("Use a password with at least 12 characters.")
    
    salt = secrets.token_bytes(16)
    
    password_hash = make_password_hash(password,salt,ITERATIONS)
    
    connection = sqlite3.connect(DB_PATH)
    
    try:
        connection.execute("BEGIN IMMEDIATE")
        
        existing = connection.execute("select 1 from staff LIMIT 1").fetchone()
        
        if existing is not None:
            raise ValueError("A staff account already exists. Please sign in.")
        
        connection.execute(
            """
            INSERT INTO staff (
                username,
                password_hash,
                salt,
                iterations
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                password_hash,
                salt,
                ITERATIONS
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def verify_login(username,password):
    connection = sqlite3.connect(DB_PATH)
    try:
        row = connection.execute("""
            SELECT password_hash, salt, iterations
            FROM staff
            WHERE username = ?
            """,
            (username.strip(),)
        ).fetchone()
        
    finally:
        connection.close()
    if row is None:
        return False
    
    saved_hash,salt,iterations = row
    
    entered_hash = make_password_hash(password,salt,iterations)
    
    return hmac.compare_digest(entered_hash,saved_hash)
        
def create_staff_account(username, password):
    username = username.strip()

    if not username:
        raise ValueError("Enter a username.")

    if len(password) < 12:
        raise ValueError(
            "Use a password with at least 12 characters."
        )

    salt = secrets.token_bytes(16)

    password_hash = make_password_hash(
        password,
        salt,
        ITERATIONS
    )

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute(
            """
            INSERT INTO staff (
                username,
                password_hash,
                salt,
                iterations
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                password_hash,
                salt,
                ITERATIONS
            )
        )

        connection.commit()

    except sqlite3.IntegrityError:
        connection.rollback()

        raise ValueError(
            "That username already exists. Choose another username."
        ) from None

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()    

