import sys
import sqlite3
import tkinter as tk
from tkinter import messagebox

# Function to fetch group name from the groups table using group_id
def get_group_name(conn, group_id):
    cursor = conn.cursor()
    cursor.execute("SELECT group_name FROM groups WHERE group_id = ?", (group_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return "Unknown Group"

# Function to fetch all accounts in the group
def fetch_group_accounts(conn, group_id):
    cursor = conn.cursor()
    cursor.execute("SELECT account_id, email, is_active FROM group_accounts WHERE group_id = ?", (group_id,))
    return cursor.fetchall()

# Function to update the is_active status in the database
def update_is_active_status(conn, account_id, new_status):
    cursor = conn.cursor()
    cursor.execute("UPDATE group_accounts SET is_active = ? WHERE account_id = ?", (new_status, account_id))
    conn.commit()

# Function to handle changes in the is_active field
def on_is_active_change(account_id, status_var, conn):
    new_status = status_var.get()
    update_is_active_status(conn, account_id, new_status)
    messagebox.showinfo("Update", f"Status updated for account {account_id}")

def main(group_id):
    # Connect to the SQLite database
    conn = sqlite3.connect("fb_ads_database.db")  # Make sure to use your actual database path

    # Fetch the group name using the group_id
    group_name = get_group_name(conn, group_id)

    # Fetch all accounts in the group
    accounts = fetch_group_accounts(conn, group_id)

    # Create the Tkinter window
    root = tk.Tk()
    root.title(f"Accounts in Group: {group_name}")

    # Display the group name at the top
    tk.Label(root, text=f"Group: {group_name}", font=("Helvetica", 16, "bold")).pack(pady=10)

    # Display each account's email and is_active status
    for account_id, email, is_active in accounts:
        # Frame for each account
        account_frame = tk.Frame(root)
        account_frame.pack(pady=5, padx=10, fill="x")

        # Email label
        tk.Label(account_frame, text=email, width=30, anchor="w").pack(side="left", padx=5)

        # is_active dropdown (editable field)
        status_var = tk.StringVar(value=is_active)
        status_menu = tk.OptionMenu(account_frame, status_var, "True", "False")
        status_menu.pack(side="left", padx=5)

        # Button to save changes
        save_button = tk.Button(account_frame, text="Save", command=lambda acc_id=account_id, stat_var=status_var: on_is_active_change(acc_id, stat_var, conn))
        save_button.pack(side="left", padx=5)

    # Run the Tkinter main loop
    root.mainloop()

    # Close the database connection
    conn.close()


def active_unactive(group_id):
    #  if len(sys.argv) != 2:
    #     print("Usage: python active_unactive.py <group_id>")
    #     sys.exit(1)
    # group_id = int(sys.argv[1])
    
    main(group_id)


# if __name__ == "__main__":
   