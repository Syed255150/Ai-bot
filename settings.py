import tkinter as tk
from tkinter import ttk
import sqlite3
import logging
import sys


def fb_settings():
    # Configure logging
    logger = logging.getLogger('fb_ads_logger')
    logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(log_handler)

    # Function to save the settings
    def save_settings():
        # Connect to the SQLite database
        conn = sqlite3.connect('fb_ads_database.db')
        cursor = conn.cursor()

        # Update the settings in the table
        cursor.execute('''UPDATE settings SET
            start_actions = ?,
            end_actions = ?,
            start_price = ?,
            end_price = ?,
            batch_size = ?,
            shuffle = ?,
            posting_lower_limit = ?,
            posting_upper_limit = ?,
            min_seconds_to_post = ?,
            max_seconds_to_post = ?,
            delete_and_relist_lower_limit = ?,
            delete_and_relist_upper_limit = ?,
            renew_lower_limit = ?,
            renew_upper_limit = ?,
            deleting_lower_limit = ?,
            deleting_upper_limit = ?,
            no_of_browser_can_launch_parallely = ?,
            no_of_tabs_to_load_parallely = ?,
            account_start_gap_in_sec = ?,
            retry_count_before_quitting = ?,
            skip_images_used_in_no_of_days = ?,
            gap_between_turns_mins = ?
            WHERE id = ?''', (
            int(entries["Start Actions"].get()),
            int(entries["End Actions"].get()),
            float(entries["Start Price"].get() or None),
            float(entries["End Price"].get() or None),
            int(entries["Batch Size"].get()),
            shuffle_var.get(),
            int(entries["Posting Lower Limit"].get()),
            int(entries["Posting Upper Limit"].get()),
            int(entries["Min Seconds To Post"].get()),
            int(entries["Max Seconds To Post"].get()),
            int(entries["Delete And Relist Lower Limit"].get()),
            int(entries["Delete And Relist Upper Limit"].get()),
            int(entries["Renew Lower Limit"].get()),
            int(entries["Renew Upper Limit"].get()),
            int(entries["Deleting Lower Limit"].get()),
            int(entries["Deleting Upper Limit"].get()),
            int(entries["No Of Browser Can Launch Parallely"].get()),
            int(entries["No Of Tabs To Load Parallely"].get()),
            int(entries["Account Start Gap In Sec"].get()),
            int(entries["Retry Count Before Quitting"].get()),
            int(entries["Skip Images Used In No Of Days"].get()),
            int(entries["Gap Between Turns (mins)"].get()),
            1  # Assuming you want to update the settings with id=1
        ))

        # Commit and close the connection
        conn.commit()
        conn.close()

        logger.info("Settings updated")

    # Function to load settings from the database
    def load_settings():
        # Connect to the SQLite database
        conn = sqlite3.connect('fb_ads_database.db')
        cursor = conn.cursor()

        # Fetch the settings from the table
        cursor.execute('SELECT * FROM settings WHERE id = ?', (1,))
        settings = cursor.fetchone()

        # Close the connection
        conn.close()

        if settings:
            (start_actions, end_actions, start_price, end_price, batch_size, shuffle,
            posting_lower_limit, posting_upper_limit, min_seconds_to_post, max_seconds_to_post,
            delete_and_relist_lower_limit, delete_and_relist_upper_limit, renew_lower_limit,
            renew_upper_limit, deleting_lower_limit, deleting_upper_limit,
            no_of_browser_can_launch_parallely, no_of_tabs_to_load_parallely,
            account_start_gap_in_sec, retry_count_before_quitting, skip_images_used_in_no_of_days,
            gap_between_turns_mins) = settings[1:]  # Skip the ID column

            # Populate the input fields with the settings values
            entries["Start Actions"].delete(0, tk.END)
            entries["Start Actions"].insert(0, start_actions)

            entries["End Actions"].delete(0, tk.END)
            entries["End Actions"].insert(0, end_actions)

            entries["Start Price"].delete(0, tk.END)
            entries["Start Price"].insert(0, start_price)

            entries["End Price"].delete(0, tk.END)
            entries["End Price"].insert(0, end_price)

            entries["Batch Size"].delete(0, tk.END)
            entries["Batch Size"].insert(0, batch_size)

            shuffle_var.set(bool(shuffle))

            entries["Posting Lower Limit"].delete(0, tk.END)
            entries["Posting Lower Limit"].insert(0, posting_lower_limit)

            entries["Posting Upper Limit"].delete(0, tk.END)
            entries["Posting Upper Limit"].insert(0, posting_upper_limit)

            entries["Min Seconds To Post"].delete(0, tk.END)
            entries["Min Seconds To Post"].insert(0, min_seconds_to_post)

            entries["Max Seconds To Post"].delete(0, tk.END)
            entries["Max Seconds To Post"].insert(0, max_seconds_to_post)

            entries["Delete And Relist Lower Limit"].delete(0, tk.END)
            entries["Delete And Relist Lower Limit"].insert(0, delete_and_relist_lower_limit)

            entries["Delete And Relist Upper Limit"].delete(0, tk.END)
            entries["Delete And Relist Upper Limit"].insert(0, delete_and_relist_upper_limit)

            entries["Renew Lower Limit"].delete(0, tk.END)
            entries["Renew Lower Limit"].insert(0, renew_lower_limit)

            entries["Renew Upper Limit"].delete(0, tk.END)
            entries["Renew Upper Limit"].insert(0, renew_upper_limit)

            entries["Deleting Lower Limit"].delete(0, tk.END)
            entries["Deleting Lower Limit"].insert(0, deleting_lower_limit)

            entries["Deleting Upper Limit"].delete(0, tk.END)
            entries["Deleting Upper Limit"].insert(0, deleting_upper_limit)

            entries["No Of Browser Can Launch Parallely"].delete(0, tk.END)
            entries["No Of Browser Can Launch Parallely"].insert(0, no_of_browser_can_launch_parallely)

            entries["No Of Tabs To Load Parallely"].delete(0, tk.END)
            entries["No Of Tabs To Load Parallely"].insert(0, no_of_tabs_to_load_parallely)

            entries["Account Start Gap In Sec"].delete(0, tk.END)
            entries["Account Start Gap In Sec"].insert(0, account_start_gap_in_sec)

            entries["Retry Count Before Quitting"].delete(0, tk.END)
            entries["Retry Count Before Quitting"].insert(0, retry_count_before_quitting)

            entries["Skip Images Used In No Of Days"].delete(0, tk.END)
            entries["Skip Images Used In No Of Days"].insert(0, skip_images_used_in_no_of_days)

            entries["Gap Between Turns (mins)"].delete(0, tk.END)
            entries["Gap Between Turns (mins)"].insert(0, gap_between_turns_mins)

    # Create the main window
    root = tk.Tk()
    root.title("SettingsForm")

    # Create a frame to hold all the widgets
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Create the widgets based on the layout in the image with labels on top
    widgets = [
        ("Start Actions", "45", 0, 0), ("End Actions", "65", 0, 1), ("Start Price", "", 0, 2), ("End Price", "", 0, 3),
        ("Batch Size", "3", 2, 0),  # Shuffle is a checkbox
        ("Posting Lower Limit", "10", 4, 0), ("Posting Upper Limit", "20", 4, 1),
        ("Min Seconds To Post", "60", 4, 2), ("Max Seconds To Post", "80", 4, 3),
        ("Delete And Relist Lower Limit", "100", 6, 0), ("Delete And Relist Upper Limit", "200", 6, 1),
        ("Renew Lower Limit", "50", 6, 2), ("Renew Upper Limit", "90", 6, 3),
        ("Deleting Lower Limit", "40", 8, 0), ("Deleting Upper Limit", "60", 8, 1),
        ("No Of Browser Can Launch Parallely", "5", 8, 2), ("No Of Tabs To Load Parallely", "10", 8, 3),
        ("Account Start Gap In Sec", "5", 10, 0), ("Retry Count Before Quitting", "3", 10, 1),
        ("Skip Images Used In No Of Days", "8", 10, 2), ("Gap Between Turns (mins)", "0", 10, 3)
    ]

    entries = {}
    shuffle_var = tk.BooleanVar(value=True)

    for label_text, default_value, row, col in widgets:
        ttk.Label(frame, text=label_text).grid(row=row, column=col, padx=5, pady=(5, 0), sticky=tk.W)
        
        if label_text == "Shuffle":
            shuffle_check = ttk.Checkbutton(frame, variable=shuffle_var)
            shuffle_check.grid(row=row+1, column=col, padx=5, pady=5, sticky=tk.W)
        else:
            entry = ttk.Entry(frame, width=15)
            entry.insert(0, default_value)
            entry.grid(row=row+1, column=col, padx=5, pady=5, sticky=tk.W)
            entries[label_text] = entry

    # Save button
    save_button = ttk.Button(frame, text="Save", command=save_settings)
    save_button.grid(row=12, column=1, padx=5, pady=10, sticky=tk.W)

    # Load settings from the database and populate the fields
    load_settings()

    # Run the application
    root.mainloop()
