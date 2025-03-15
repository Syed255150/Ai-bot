import logging
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import sqlite3

# Setup logging
logger = logging.getLogger('fb_ads_logger')
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(log_handler)

# Function to save schedule
def save_schedule():
    try:
        schedule_date = date_entry.get()
        schedule_time = time_entry.get()
        schedule_datetime = f"{schedule_date} {schedule_time}"
        schedule_datetime_obj = datetime.strptime(schedule_datetime, '%Y-%m-%d %H:%M:%S')

        # Connect to database and insert schedule
        conn = sqlite3.connect('fb_ads_database.db')
        cursor = conn.cursor()

        # Insert into Schedule table
        cursor.execute('''
            INSERT INTO schedule (group_id, additional_number, random_price, posting_speed, post_action, shuffle_accounts, schedule_datetime)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (group_id, additional_number, random_price, time_speed, post_action, shuffle_accounts, schedule_datetime_obj))
        
        conn.commit()
        conn.close() 

        logger.info(f"Scheduled task saved for {schedule_datetime}")
        messagebox.showinfo("Success", "Scheduling saved successfully.")
    
    except Exception as e:
        logger.error(f"Error saving schedule: {e}")
        messagebox.showerror("Error", f"Error saving schedule: {e}")

# Get current date and time
now = datetime.now()
current_date = now.strftime('%Y-%m-%d')
current_time = now.strftime('%H:%M:%S')

# Create Tkinter GUI
if __name__ == "__main__":
    if len(sys.argv) != 7:
        logger.info("Usage: python fb_ads_automate.py <group_id> <additional_number> <random price> <posting speed> <post action> <shuffle account>")
        sys.exit(1)

    group_id = int(sys.argv[1])
    additional_number = int(sys.argv[2])
    random_price = int(sys.argv[3])
    time_speed = int(sys.argv[4])
    post_action = int(sys.argv[5])
    shuffle_accounts = int(sys.argv[6])

    # Create Tkinter window
    root = tk.Tk()
    root.title("Schedule Task")

    # Display values
    tk.Label(root, text=f"Group ID: {group_id}").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(root, text=f"Additional Number: {additional_number}").grid(row=1, column=0, padx=10, pady=5)
    tk.Label(root, text=f"Post Action: {post_action}").grid(row=2, column=0, padx=10, pady=5)
    tk.Label(root, text=f"Random Price: {random_price}").grid(row=3, column=0, padx=10, pady=5)
    if time_speed == 5:
        tk.Label(root, text=f"Posting Speed: Calm").grid(row=4, column=0, padx=10, pady=5)
    elif time_speed == 3:
        tk.Label(root, text=f"Posting Speed: Normal").grid(row=4, column=0, padx=10, pady=5)
    elif time_speed == 2:
        tk.Label(root, text=f"Posting Speed: 2x").grid(row=4, column=0, padx=10, pady=5)
    elif time_speed == 1:
        tk.Label(root, text=f"Posting Speed: Calm").grid(row=4, column=0, padx=10, pady=5)

    # Date and time entry
    tk.Label(root, text="Schedule Date (YYYY-MM-DD):").grid(row=5, column=0, padx=10, pady=5)
    date_entry = tk.Entry(root)
    date_entry.grid(row=5, column=1, padx=10, pady=5)
    date_entry.insert(0, current_date)  # Set default date

    tk.Label(root, text="Schedule Time (HH:MM:SS):").grid(row=6, column=0, padx=10, pady=5)
    time_entry = tk.Entry(root)
    time_entry.grid(row=6, column=1, padx=10, pady=5)
    time_entry.insert(0, current_time)  # Set default time

    # Save button
    save_button = tk.Button(root, text="Save Schedule", command=save_schedule)
    save_button.grid(row=7, column=0, columnspan=2, padx=10, pady=20)

    root.mainloop()
