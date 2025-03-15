import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import threading
import logging

from na_fb_ads_automate import na_fb_ads_automate
from na_create_group_GUI import na_create_group_GUI
from display_product_GUI import display_product_GUI
from na_add_more_products_GUI import na_add_more_products_GUI
from na_remove_products_GUI import na_remove_products_GUI

from db_connection import get_connection

# Configure logging
logger = logging.getLogger('new_account_logger')
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
logger.addHandler(log_handler)

def na_GUI():
    def fetch_groups():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT na_group_id, na_group_name FROM na_groups")
        groups = cursor.fetchall()
        conn.close()
        return groups

    def run_selected_group():
        selected_idx = group_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a group.")
            return

        selected_group_id = group_ids[selected_idx[0]]
        start_logging()  # Start logging
        threading.Thread(target=na_fb_ads_automate, args=(selected_group_id,), daemon=True).start()

    # def run_fb_ads(group_id):
    #     try:
    #         process = subprocess.Popen(['python', 'na_fb_ads_automate.py', str(group_id)], 
    #                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    #         for line in iter(process.stdout.readline, ''):
    #             update_log(line)
            
    #         process.stdout.close()
    #         process.stderr.close()
    #         process.wait()

    #         if process.returncode != 0:
    #             update_log(f"Error running na_fb_ads_automate.py with return code {process.returncode}")
    #     except subprocess.CalledProcessError as e:
    #         logger.error(f"Error running na_fb_ads_automate.py: {e}")
    #         logger.error(e.stderr)
    #     except Exception as e:
    #         logger.error(f"Unexpected error: {e}")

    def delete_selected_group():
        selected_idx = group_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a group.")
            return

        selected_group_id = group_ids[selected_idx[0]]
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this group?")

        if confirm:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM na_groups WHERE na_group_id=?", (selected_group_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Group deleted successfully.")
            refresh_groups()

    def add_new_group():
        # subprocess.Popen(['python', 'na_create_group_GUI.py'])
        na_create_group_GUI()

    # def add_new_product():
    #     subprocess.Popen(['python', 'insert_product_GUI.py'])

    def open_display_product():
        # subprocess.Popen(["python", "display_product_GUI.py"])
        display_product_GUI()

    def add_more_products():
        selected_idx = group_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a group.")
            return

        group_id = group_ids[selected_idx[0]]
        na_add_more_products_GUI(group_id)
        # subprocess.Popen(['python', 'na_add_more_products_GUI.py', str(group_id)])

    def remove_products():
        selected_idx = group_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a group.")
            return

        group_id = group_ids[selected_idx[0]]
        na_remove_products_GUI(group_id)
        # subprocess.Popen(['python', 'na_remove_products_GUI.py', str(group_id)])

    def refresh_groups():
        group_listbox.delete(0, tk.END)
        groups = fetch_groups()
        global group_ids, group_names
        group_ids = [group[0] for group in groups]
        group_names = [group[1] for group in groups]
        for group_name in group_names:
            group_listbox.insert(tk.END, group_name)

    def start_logging():
        # Clear previous logs
        log_display.config(state=tk.NORMAL)
        log_display.delete(1.0, tk.END)
        log_display.config(state=tk.DISABLED)

    def update_log(msg):
        log_display.config(state=tk.NORMAL)
        log_display.insert(tk.END, msg)
        log_display.yview(tk.END)
        log_display.config(state=tk.DISABLED)

    # Create new Tkinter window
    new_account_root = tk.Tk()
    new_account_root.title("New Account - Facebook Marketplace Automation")

    tk.Label(new_account_root, text="Select a Group for new accounts:").pack(pady=10)

    # Fetch and display groups in a Listbox
    groups = fetch_groups()
    group_ids = [group[0] for group in groups]
    group_names = [group[1] for group in groups]

    group_listbox = tk.Listbox(new_account_root, selectmode=tk.SINGLE, width=50, height=10)
    for group_name in group_names:
        group_listbox.insert(tk.END, group_name)
    group_listbox.pack(pady=5)

    btn_run_group = tk.Button(new_account_root, text="Run Selected Group", command=run_selected_group)
    btn_run_group.pack(pady=5)

    btn_delete_group = tk.Button(new_account_root, text="Delete Selected Group", command=delete_selected_group)
    btn_delete_group.pack(pady=5)

    btn_add_group = tk.Button(new_account_root, text="Add New Group", command=add_new_group)
    btn_add_group.pack(pady=5)

    # btn_add_product = tk.Button(new_account_root, text="Add Product", command=add_new_product)
    # btn_add_product.pack(pady=5)

    btn_display_products = tk.Button(new_account_root, text="Display Products", command=open_display_product)
    btn_display_products.pack(pady=5)

    btn_add_more_products = tk.Button(new_account_root, text="Add More Products", command=add_more_products)
    btn_add_more_products.pack(pady=5)

    btn_remove_products = tk.Button(new_account_root, text="Remove Products", command=remove_products)
    btn_remove_products.pack(pady=5)

    # Create a Text widget for log display
    log_display = scrolledtext.ScrolledText(new_account_root, width=80, height=10, wrap=tk.WORD, state=tk.DISABLED)
    log_display.pack(pady=10)

    # Start the Tkinter main loop
    new_account_root.mainloop()
