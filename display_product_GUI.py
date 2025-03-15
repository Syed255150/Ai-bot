import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import execute_query
from delete_product import delete_product


def display_product_GUI():
    def select_data():
        query = "SELECT * FROM product"
        result = execute_query(query)
        return result

    def display_data():
        for row in tree.get_children():
            tree.delete(row)
        data = select_data()
        for index, row in enumerate(data):
            tree.insert("", "end", values=row)

    def delete_selected_product():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select a product to delete.")
            return

        product_id = tree.item(selected_item)["values"][0]  # Assuming the product ID is in the first column
        delete_product(product_id)
        display_data()

    # Create main Tkinter window
    root = tk.Tk()
    root.title("Display Product Data")

    # Create custom style for Treeview headings
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), borderwidth=1, relief="solid")
    style.configure("Treeview", rowheight=25, borderwidth=1, relief="solid")

    # Create Treeview to display product data
    columns = ("Product ID", "Product Name", "Image Path", "Video Path", "Title", "Price", "Category", "Description", "Tags", "Location")
    tree = ttk.Treeview(root, columns=columns, show="headings", style="Treeview")

    # Define column headings and set the width
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="w")

    # Add Treeview to window with vertical scrollbar
    tree.pack(expand=True, fill=tk.BOTH)
    scrollbar_y = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar_y.set)

    # Add horizontal scrollbar for the Title column
    scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    tree.configure(xscrollcommand=scrollbar_x.set)

    # Add scrollbar to Treeview
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Button to load and display data
    btn_load = tk.Button(root, text="Load Data", command=display_data)
    btn_load.pack(pady=10)

    # Button to delete selected product
    btn_delete = tk.Button(root, text="Delete Selected Product", command=delete_selected_product)
    btn_delete.pack(pady=10)

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    display_product_GUI()