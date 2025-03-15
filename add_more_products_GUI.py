import tkinter as tk
from tkinter import messagebox
import sys
from db_connection import get_connection

# group_id = sys.argv[1]

def add_more_products_GUI(group_id):
    def fetch_products_not_in_group(group_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT product_id, product_name FROM product
        WHERE product_id NOT IN (
            SELECT product_id FROM group_products WHERE group_id = ?
        )
        ''', (group_id,))
        products = cursor.fetchall()
        conn.close()
        return products

    def add_products_to_group(group_id, product_ids):
        conn = get_connection()
        cursor = conn.cursor()
        for product_id in product_ids:
            cursor.execute('''
            INSERT INTO group_products (group_id, product_id)
            VALUES (?, ?)
            ''', (group_id, product_id))
        conn.commit()
        conn.close()

    def add_selected_products():
        selected_indices = product_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select at least one product.")
            return

        selected_product_ids = [product_ids[i] for i in selected_indices]
        add_products_to_group(group_id, selected_product_ids)
        messagebox.showinfo("Success", "Selected products added to the group.")
        root.destroy()

    # Create main Tkinter window
    root = tk.Tk()
    root.title("Add More Products to Group")

    tk.Label(root, text="Select Products to Add to Group:").pack(pady=10)

    # Fetch and display products not already in the group
    products = fetch_products_not_in_group(group_id)
    product_ids = [product[0] for product in products]
    product_names = [product[1] for product in products]

    product_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=10)
    for product_name in product_names:
        product_listbox.insert(tk.END, product_name)
    product_listbox.pack(pady=5)

    btn_add_products = tk.Button(root, text="Add Selected Products", command=add_selected_products)
    btn_add_products.pack(pady=5)

    # Start the Tkinter main loop
    root.mainloop()


