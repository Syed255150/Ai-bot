import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sqlite3
from db_connection import get_connection
# from group_product_schema import setup_extended_schema

# setup_extended_schema()

def na_create_group_GUI(): 

    def insert_group(group_name):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
            INSERT INTO na_groups (na_group_name) VALUES (?)
            ''', (group_name,))
            group_id = cursor.lastrowid
            conn.commit()
            return group_id
        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to create group:\n{str(e)}")
        finally:
            conn.close()

    def insert_group_account(group_id, email, password):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
            INSERT INTO na_group_accounts (na_group_id, email, password) VALUES (?, ?, ?)
            ''', (group_id, email, password))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to add account:\n{str(e)}")
        finally:
            conn.close()

    def insert_group_product(group_id, product_id):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
            INSERT INTO na_group_products (na_group_id, product_id) VALUES (?, ?)
            ''', (group_id, product_id))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to add product:\n{str(e)}")
        finally:
            conn.close()

    def read_accounts(file_path):
        accounts = []
        with open(file_path, 'r') as file:
            for line in file:
                email, password = line.strip().split(';')
                accounts.append((email, password))
        return accounts

    def create_group():
        group_name = entry_group_name.get()
        group_id = insert_group(group_name)

        accounts = read_accounts(file_path)
        for email, password in accounts:
            insert_group_account(group_id, email, password)

        selected_products = [product_listbox.get(idx) for idx in product_listbox.curselection()]
        for product_name in selected_products:
            product_id = product_dict[product_name]
            insert_group_product(group_id, product_id)

        messagebox.showinfo("Success", "Group created successfully")

    # Fetch products from the database
    def fetch_products():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, product_name FROM product")
        products = cursor.fetchall()
        conn.close()
        return products

    # Create main Tkinter window
    root = tk.Tk()
    root.title("Create Group for new accounts")

    tk.Label(root, text="Group Name:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    entry_group_name = tk.Entry(root, width=50)
    entry_group_name.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Accounts File:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    lbl_file_path = tk.Label(root, text="", width=50, anchor="w")
    lbl_file_path.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

    def browse_file():
        global file_path
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        lbl_file_path.config(text=file_path)

    btn_browse_file = tk.Button(root, text="Browse...", command=browse_file)
    btn_browse_file.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)

    tk.Label(root, text="Select Products:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

    # Fetch and display products in a Listbox
    products = fetch_products()
    product_dict = {product_name: product_id for product_id, product_name in products}

    product_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=10)
    for product_name in product_dict.keys():
        product_listbox.insert(tk.END, product_name)
    product_listbox.grid(row=2, column=1, padx=10, pady=5, columnspan=2)

    btn_create_group = tk.Button(root, text="Create Group", command=create_group)
    btn_create_group.grid(row=3, column=0, columnspan=3, pady=10)

    # Start the Tkinter main loop
    root.mainloop()
