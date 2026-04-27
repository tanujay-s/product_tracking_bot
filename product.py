import psycopg2
import os
from datetime import datetime

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def add_product(user_id, url, days_to_track):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO user_products (user_id, url, days_to_track)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, url) DO NOTHING
    """, (user_id, url, days_to_track))

    conn.commit()
    cur.close()
    conn.close()

def get_user_products(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, url, days_to_track, created_at
        FROM user_products
        WHERE user_id = %s AND is_active = TRUE
    """, (user_id,))

    products = cur.fetchall()

    cur.close()
    conn.close()

    return products

def get_all_active_products():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
        up.id,
        u.telegram_user_id,
        up.url,
        up.days_to_track,
        up.created_at
        FROM user_products up
        JOIN users u ON up.user_id = u.id
        WHERE up.is_active = TRUE
    """)

    products = cur.fetchall()

    cur.close()
    conn.close()

    return products

def deactivate_expired_products():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE user_products
        SET is_active = FALSE
        WHERE is_active = TRUE
        AND NOW() > created_at + (days_to_track || ' days')::interval
    """)

    conn.commit()
    cur.close()
    conn.close()

def delete_product(product_id, user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM user_products
        WHERE id = %s AND user_id = %s
    """, (product_id, user_id))

    conn.commit()
    cur.close()
    conn.close()