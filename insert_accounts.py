import tkinter as tk
from tkinter import messagebox
import sqlite3
import sys

def insert_account_into_db(group_id, email, password, is_active):
    conn = sqlite3.connect('fb_ads_database.db')
    cursor = conn.cursor()

    try:
        # Insert account into the group_accounts table
        cursor.execute('''
            INSERT INTO group_accounts (group_id, email, password, is_active) 
            VALUES (?, ?, ?, ?)
        ''', (group_id, email, password, is_active))

        conn.commit()
        messagebox.showinfo("Success", "Account added successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        conn.close()

def insert_account_screen(group_id):
    conn = sqlite3.connect('fb_ads_database.db')
    cursor = conn.cursor()

    # Fetch group name using group_id
    cursor.execute("SELECT group_name FROM groups WHERE group_id = ?", (group_id,))
    group_name = cursor.fetchone()

    if group_name:
        group_name = group_name[0]
    else:
        group_name = "Unknown Group"

    conn.close()

    # Create GUI window for inserting account
    root = tk.Tk()
    root.title(f"Insert Account - {group_name}")

    # Group name display
    group_label = tk.Label(root, text=f"Group: {group_name}")
    group_label.pack(pady=10)

    # Email label and entry
    email_label = tk.Label(root, text="Email:")
    email_label.pack(pady=5)
    email_entry = tk.Entry(root)
    email_entry.pack(pady=5)

    # Password label and entry
    password_label = tk.Label(root, text="Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    is_active_label = tk.Label(root, text="Is Active:")
    is_active_label.pack(pady=5)
    is_active_entry = tk.Entry(root)
    is_active_entry.pack(pady=5)

    def on_submit():
        email = email_entry.get()
        password = password_entry.get()
        is_active = is_active_entry.get()

        if not email or not password or not is_active:
            messagebox.showwarning("Input Error", "Please enter values for email, password and is active.")
            return

        # Insert account into the database
        insert_account_into_db(group_id, email, password, is_active)
        root.destroy()  # Close the window after inserting the account

    # Submit button
    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.pack(pady=20)

    root.mainloop()

def insert_account(group_id):
    # if len(sys.argv) != 2:
    #     print("Usage: python insert_accounts.py <group_id>")
    #     sys.exit(1)

    # group_id = int(sys.argv[1])
    # print(f"the group id {group_id} passed to the file insert_accounts.py")
    insert_account_screen(group_id)


# if __name__ == "__main__":
#     insert_accounts()    
