import tkinter as tk
from tkinter import messagebox
from db_connection import get_connection

def fetch_groups():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id, group_name FROM groups")
    groups = cursor.fetchall()
    conn.close()
    return groups

def delete_selected_group(selected_group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM groups WHERE group_id=?", (selected_group_id,))
    conn.commit()
    conn.close()

# Create main Tkinter window
root = tk.Tk()
root.title("Delete Group")

tk.Label(root, text="Select a Group to Delete:").pack(pady=10)

# Fetch and display groups in a Listbox
groups = fetch_groups()
group_ids = [group[0] for group in groups]
group_names = [group[1] for group in groups]

group_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=10)
for group_name in group_names:
    group_listbox.insert(tk.END, group_name)
group_listbox.pack(pady=5)

def delete_group():
    selected_idx = group_listbox.curselection()
    if not selected_idx:
        messagebox.showwarning("No Selection", "Please select a group.")
        return

    selected_group_id = group_ids[selected_idx[0]]
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this group?")

    if confirm:
        delete_selected_group(selected_group_id)
        messagebox.showinfo("Success", "Group deleted successfully.")
        refresh_groups()

def refresh_groups():
    group_listbox.delete(0, tk.END)
    groups = fetch_groups()
    global group_ids, group_names
    group_ids = [group[0] for group in groups]
    group_names = [group[1] for group in groups]
    for group_name in group_names:
        group_listbox.insert(tk.END, group_name)

btn_delete_group = tk.Button(root, text="Delete Selected Group", command=delete_group)
btn_delete_group.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()
