import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sqlite3
import os
from db_connection import get_connection


def insert_product_GUI():
    # List of category options including "Select" as default
    categories = [
        "Select",
        "Furniture > Bedroom furniture > Beds and bed frames",
        "Furniture > Bedroom furniture > Mattresses",
        "Furniture > Dining room furniture > Dining tables",
        "Furniture > Dining room furniture > Bar stools",
        "Furniture > Living room furniture > Coffee tables",
        "Furniture > Living room furniture > Sofas, love seats and sectionals",
        "Furniture > Outdoor furniture > Outdoor chairs, benches & swings",
        "Furniture > Outdoor furniture > Outdoor sofas",
        "Furniture > Armoires & wardrobe",
        "Furniture > Dressers"
    ]

    def insert_data(product_name, image_path, video_path, title, price, category, description, tags, location):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Insert into product table
            cursor.execute('''
            INSERT INTO product (product_name, image_path, video_path, title, price, category, description, tags, location)
            VALUES (?,?,?,?,?,?,?,?,?)
            ''', (product_name, image_path, video_path, title, price, category, description, tags, location))

            conn.commit()
            messagebox.showinfo("Success", "Product Added Successfully")
        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to add product:\n{str(e)}")
        finally:
            conn.close()

    def browse_image_folder():
        global image_path
        image_folder = filedialog.askdirectory()
        if image_folder:
            image_path = image_folder
            lbl_image_path.config(text=image_path)
        root.lift()  # Bring back the root window to the top
        root.focus_force()
        
    def browse_video():
        global video_path
        video_path = filedialog.askopenfilename()
        lbl_video_path.config(text=video_path)
        root.lift()  # Bring back the root window to the top
        root.focus_force()
        
    def browse_title():
        global title
        title_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if title_file:
            with open(title_file, 'r') as file:
                title = file.read().strip()
            lbl_title_path.config(text=title_file)
        root.lift()  # Bring back the root window to the top
        root.focus_force()

    def browse_location():
        global location
        location_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if location_file:
            with open(location_file, 'r') as file:
                location = file.read().strip()
            lbl_location_path.config(text=location_file)
        root.lift()  # Bring back the root window to the top
        root.focus_force()
        
    def submit_data():
        # Get data from entry fields and dropdown
        global title
        global location
        global image_path
        product_name = entry_product_name.get()
        price = float(entry_price.get())
        category = var_category.get()  # Retrieve selected category from dropdown
        description = entry_description.get("1.0", tk.END).strip()
        tags = entry_tags.get()

        # Check if "Select" is chosen
        if category == "Select":
            messagebox.showerror("Error", "Please select a category.")
            return
        
       # Check if the title file has been selected
        if not lbl_title_path.cget("text") or lbl_title_path.cget("text").strip() == "":
            messagebox.showerror("Error", "Please provide a title by selecting a title file.")
            return

        # Call insert_data function with collected data
        insert_data(product_name, image_path, video_path, title, price, category, description, tags, location)

        # Clear entry fields after insertion
        entry_product_name.delete(0, tk.END)
        entry_price.delete(0, tk.END)
        entry_description.delete("1.0", tk.END)
        entry_tags.delete(0, tk.END)
        var_category.set(categories[0])  # Reset dropdown to "Select"
        lbl_image_path.config(text="")
        lbl_video_path.config(text="")
        lbl_title_path.config(text="")
        lbl_location_path.config(text="")

    # Create main Tkinter window
    root = tk.Tk()
    root.title("Insert Product Data")

    # Define variables for file paths
    image_path = None
    video_path = None
    title = None
    location = None

    # Create labels and entry fields for product data
    tk.Label(root, text="Product Name:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    entry_product_name = tk.Entry(root, width=80)
    entry_product_name.grid(row=0, column=1, columnspan=4, padx=10, pady=5)

    tk.Label(root, text="Title File:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    lbl_title_path = tk.Label(root, text="", width=80, anchor="w", wraplength=600)
    lbl_title_path.grid(row=1, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)

    btn_browse_title = tk.Button(root, text="Browse...", command=browse_title)
    btn_browse_title.grid(row=1, column=4, padx=10, pady=5, sticky=tk.W)
  
    tk.Label(root, text="Price:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
    entry_price = tk.Entry(root, width=80)
    entry_price.grid(row=2, column=1, columnspan=4, padx=10, pady=5)

    tk.Label(root, text="Category:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
    var_category = tk.StringVar(root)
    var_category.set(categories[0])  # Set default category to "Select"
    dropdown_category = ttk.OptionMenu(root, var_category, *categories)
    dropdown_category.grid(row=3, column=1, columnspan=4, padx=10, pady=5)

    tk.Label(root, text="Description:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
    entry_description = tk.Text(root, width=80, height=4)
    entry_description.grid(row=4, column=1, columnspan=4, padx=10, pady=5, sticky=tk.W)

    tk.Label(root, text="Tags:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
    entry_tags = tk.Entry(root, width=80)
    entry_tags.grid(row=5, column=1, columnspan=4, padx=10, pady=5)

    tk.Label(root, text="Location File:").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
    lbl_location_path = tk.Label(root, text="", width=80, anchor="w", wraplength=600)
    lbl_location_path.grid(row=6, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)

    btn_browse_location = tk.Button(root, text="Browse...", command=browse_location)
    btn_browse_location.grid(row=6, column=4, padx=10, pady=5, sticky=tk.W)

    tk.Label(root, text="Image Path:").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
    lbl_image_path = tk.Label(root, text="", width=80, anchor="w", wraplength=600)
    lbl_image_path.grid(row=7, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)

    btn_browse_image_folder = tk.Button(root, text="Browse Folder...", command=browse_image_folder)
    btn_browse_image_folder.grid(row=7, column=4, padx=10, pady=5, sticky=tk.W)

    tk.Label(root, text="Video Path:").grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)
    lbl_video_path = tk.Label(root, text="", width=80, anchor="w", wraplength=600)
    lbl_video_path.grid(row=8, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)

    btn_browse_video = tk.Button(root, text="Browse...", command=browse_video)
    btn_browse_video.grid(row=8, column=4, padx=10, pady=5, sticky=tk.W)

    btn_submit = tk.Button(root, text="Submit", command=submit_data)
    btn_submit.grid(row=9, column=0, columnspan=5, pady=10)

    # Start the Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    insert_product_GUI()
