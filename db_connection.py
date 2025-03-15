import sqlite3

def get_connection():
    conn = sqlite3.connect('fb_ads_database.db')
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

def execute_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result
