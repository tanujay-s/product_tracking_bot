import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def create_user(telegram_user_id, username):
    conn = get_connection()

    if not conn:
        print("DB connection failed for user")
        return
    
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (telegram_user_id, username)
        VALUES (%s, %s)
        ON CONFLICT (telegram_user_id) DO NOTHING;
    """, (telegram_user_id, username))

    conn.commit()
    cur.close()
    conn.close()

def get_user(telegram_user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, telegram_user_id, username
        FROM users
        WHERE telegram_user_id = %s
    """, (telegram_user_id,))

    user = cur.fetchone()

    cur.close()
    conn.close()

    return user