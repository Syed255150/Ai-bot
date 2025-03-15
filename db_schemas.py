import sqlite3
from db_connection import get_connection

def setup_schema():

    conn = get_connection()
    cursor = conn.cursor()

     # Create product table with updated fields
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS product (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        image_path TEXT,
        video_path TEXT,
        title TEXT,
        price INTEGER NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        tags TEXT NOT NULL,
        location TEXT
    )
    ''')

    # Create groups table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        group_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_name TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        FOREIGN KEY (created_by) REFERENCES users (user_id) ON DELETE CASCADE
    )
    ''')

    # Create group_accounts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        is_active TEXT NOT NULL,
        FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE CASCADE
    )
    ''')

    # Create group_products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_products (
        group_id INTEGER,
        product_id INTEGER,
        FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE CASCADE
    )
    ''')

    # new accounts

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS na_groups (
        na_group_id INTEGER PRIMARY KEY AUTOINCREMENT,
        na_group_name TEXT NOT NULL
    )
    ''')

    # Create new accounts group_accounts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS na_group_accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        na_group_id INTEGER,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        FOREIGN KEY (na_group_id) REFERENCES na_groups (na_group_id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS na_group_products (
        na_group_id INTEGER,
        product_id INTEGER,
        FOREIGN KEY (na_group_id) REFERENCES na_groups (na_group_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    additional_number INTEGER NOT NULL,
    random_renew_number INTEGER,
    random_price INTEGER NOT NULL,
    delete_relist INTEGER,
    posting_speed INTEGER NOT NULL,
    post_action INTEGER NOT NULL,
    shuffle_accounts INTEGER,
    schedule_datetime DATETIME NOT NULL,
    status TEXT DEFAULT 'Pending')''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    machine_address TEXT NOT NULL,
    validated INTEGER DEFAULT 0)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    batch_size TEXT DEFAULT '1',
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_actions INTEGER NOT NULL DEFAULT 45,
    end_actions INTEGER NOT NULL DEFAULT 65,
    start_price REAL DEFAULT 10,
    end_price REAL DEFAULT 15,
    batch_size INTEGER NOT NULL DEFAULT 3,
    shuffle BOOLEAN NOT NULL DEFAULT TRUE,
    posting_lower_limit INTEGER NOT NULL DEFAULT 10,
    posting_upper_limit INTEGER NOT NULL DEFAULT 20,
    min_seconds_to_post INTEGER NOT NULL DEFAULT 60,
    max_seconds_to_post INTEGER NOT NULL DEFAULT 80,
    delete_and_relist_lower_limit INTEGER NOT NULL DEFAULT 100,
    delete_and_relist_upper_limit INTEGER NOT NULL DEFAULT 200,
    renew_lower_limit INTEGER NOT NULL DEFAULT 50,
    renew_upper_limit INTEGER NOT NULL DEFAULT 90,
    deleting_lower_limit INTEGER NOT NULL DEFAULT 40,
    deleting_upper_limit INTEGER NOT NULL DEFAULT 60,
    no_of_browser_can_launch_parallely INTEGER NOT NULL DEFAULT 5,
    no_of_tabs_to_load_parallely INTEGER NOT NULL DEFAULT 10,
    account_start_gap_in_sec INTEGER NOT NULL DEFAULT 5,
    retry_count_before_quitting INTEGER NOT NULL DEFAULT 3,
    skip_images_used_in_no_of_days INTEGER NOT NULL DEFAULT 8,
    gap_between_turns_mins INTEGER NOT NULL DEFAULT 0)''')


    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_schema()
