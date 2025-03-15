import tkinter as tk
from tkinter import messagebox
import sys
from db_connection import get_connection

# group_id = sys.argv[1]

def na_remove_products_GUI(group_id):

    def fetch_products_in_group(group_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT product.product_id, product.product_name FROM product
        INNER JOIN na_group_products ON product.product_id = na_group_products.product_id
        WHERE na_group_products.na_group_id = ?
        ''', (group_id,))
        products = cursor.fetchall()
        conn.close()
        return products

    def remove_products_from_group(group_id, product_ids):
        conn = get_connection()
        cursor = conn.cursor()
        for product_id in product_ids:
            cursor.execute('''
            DELETE FROM na_group_products WHERE na_group_id = ? AND product_id = ?
            ''', (group_id, product_id))
        conn.commit()
        conn.close()

    def remove_selected_products():
        selected_indices = product_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select at least one product.")
            return

        selected_product_ids = [product_ids[i] for i in selected_indices]
        remove_products_from_group(group_id, selected_product_ids)
        messagebox.showinfo("Success", "Selected products removed from the group.")
        root.destroy()

    # Create main Tkinter window
    root = tk.Tk()
    root.title("Remove Products from Group")

    tk.Label(root, text="Select Products to Remove from Group:").pack(pady=10)

    # Fetch and display products already in the group
    products = fetch_products_in_group(group_id)
    product_ids = [product[0] for product in products]
    product_names = [product[1] for product in products]

    product_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=10)
    for product_name in product_names:
        product_listbox.insert(tk.END, product_name)
    product_listbox.pack(pady=5)

    btn_remove_products = tk.Button(root, text="Remove Selected Products", command=remove_selected_products)
    btn_remove_products.pack(pady=5)

    # Start the Tkinter main loop
    root.mainloop()
