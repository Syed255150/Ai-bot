import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import threading
import logging
import random
from db_connection import get_connection
from tkinter import ttk
import uuid
import subprocess,psutil,time
import os,sys,re
from path import base_path
import sqlite3

from fb_ads_automate import main
from renew import renew
from delete_and_relist import delete_relist
from create_group_GUI import create_group_GUI
from insert_product_GUI import insert_product_GUI
from display_product_GUI import display_product_GUI
from add_more_products_GUI import add_more_products_GUI
from insert_accounts import insert_account
from active_unactive import active_unactive
from remove_products_GUI import remove_products_GUI
from na_GUI import na_GUI
from settings import fb_settings
# Configure logging
logger = logging.getLogger('fb_ads_logger')
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
logger.addHandler(log_handler)


def open_cmd_and_run_script(script_name):

    # Check if the script is an executable (.exe)
    if script_name.endswith('.exe'):
        command = f'start cmd /k {script_name}'
    else:
        command = f'start cmd /k python {script_name}'
    
    # Use subprocess to run the command
    subprocess.Popen(command, shell=True)
    
    # command = f'start cmd /k python {script_name}'
        
    # subprocess.Popen(command, shell=True)


account_status = []
def app(username,user_id):

    def fetch_groups():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT group_id, group_name FROM groups WHERE created_by=?",(user_id,))
        groups = cursor.fetchall()
        conn.commit()
        conn.close()
        return groups
    
    def fetch_access_items():
        conn = get_connection()
        cursor = conn.cursor()
        # cursor.execute("SELECT id,batch_size FROM settings")
        cursor.execute("SELECT id,batch_size FROM access WHERE username=?", (username,))
        items = cursor.fetchall()
        conn.close()
        return items
    
    items = fetch_access_items()
    batch_size = [i[1] for i in items]

    def fetch_settings():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT start_actions, end_actions FROM settings")
        settings = cursor.fetchall()
        conn.close()
        return settings
    settings = fetch_settings()
    action = settings[0]

    def post_products():
        selected_idx = group_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a group.")
            return
        group_name = group_listbox.get(selected_idx)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT group_id FROM groups WHERE group_name = ?', (group_name,))
        selected_group_id  = cursor.fetchall()
        conn.commit()
        conn.close()
        selected_group_id = selected_group_id[0][0]
        # selected_group_id = group_ids[selected_idx[0]]
      
        additional_number = additional_number_entry.get()
        price_start = price_start_entry.get()
        price_end = price_end_entry.get()
        time_speed1 = get_speed_value()
        start_action = start_action_entry.get()
        end_action = end_action_entry.get()
       

        if not additional_number.isdigit() or additional_number > batch_size[0]:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer or integer should not greater than default integer.")
            return
            
        if (price_start == "Start price" or not price_start) or (price_end == "End price" or not price_end):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT start_price, end_price FROM settings")
            prices = cursor.fetchall()
            conn.close()

            prices = prices[0]
            price1 ,price2 = prices
            random_price = (random.uniform(price1, price2))
            random_price = int(round(random_price, 0))
            logger.info(random_price)
        else:
            try:
                price_start = int(price_start)
                price_end = int(price_end)

                if price_start > price_end:
                    messagebox.showerror("Error", "Start price should be less than or equal to end price.")
                    return
                    
                # Generate a random number if inputs are valid
                divisible_by_5 = [i for i in range(price_start, price_end + 1) if i % 5 == 0]
                if divisible_by_5:
                    random_price = random.choice(divisible_by_5)
                else:
                    random_price = random.randint(price_start, price_end)

            except ValueError:
                messagebox.showwarning("Invalid Input", "start price and end price values must be valid integers.")
                return
            

        if (not start_action ) or (not end_action):
            start_action = 1
            end_action = 1
            post_action = random.randint(start_action, end_action)
        else:
            try:
                start_action = int(start_action)
                end_action = int(end_action)

                if start_action > end_action:
                    messagebox.showerror("Error", "Start action should be less than or equal to end action.")
                    return
                    
                # Generate a random number if inputs are valid
                post_action = random.randint(start_action, end_action)

            except ValueError:
                messagebox.showwarning("Invalid Input", "start and end actions be valid integers.")
                return
        
        start_logging()  # Start logging
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM group_accounts WHERE group_id = ? AND is_active = 'True'", (selected_group_id,))
        active_accounts = cursor.fetchall()
        cursor.execute("SELECT email FROM group_accounts WHERE group_id = ? AND is_active = 'False'", (selected_group_id,))
        unactive_accounts = cursor.fetchall()
        conn.close()

        # Clear the listboxes before populating
        active_listbox.delete(0, tk.END)
        inactive_listbox.delete(0, tk.END)

        # Populate the active accounts listbox
        for account in active_accounts:
            active_listbox.insert(tk.END, account[0])  # Insert only the email
        
        # Populate the inactive accounts listbox
        for account in unactive_accounts:
            inactive_listbox.insert(tk.END, account[0]) 

        shuffle_account = entry_var.get()


        threading.Thread(target=main, args=(selected_group_id, additional_number, random_price, time_speed1, post_action,shuffle_account), daemon=True).start()

    # def fb_ads(group_id, additional_number, random_price, time_speed1, post_action,shuffle_account):
    #     try: 
    #         post_path = os.path.join(base_path, 'fb_ads_automate.exe')
    #         process = subprocess.Popen([post_path, str(group_id), str(additional_number), str(random_price), str(time_speed1), str(post_action),str(shuffle_account)], 
    #                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,creationflags=subprocess.CREATE_NO_WINDOW)
            
    #         for line in iter(process.stdout.readline, ''):
    #             if "blocked/disabled" in line:
    #                 account_status.append(line.strip())
    #                 account_status_listbox.delete(0, tk.END)
    #                 account_status_listbox.insert(tk.END, account_status[-1])  
    #             elif "VPN" in line:
    #                 vpn_label.config(text=f"{line}")
    #             elif "account position changed:" in line:
    #                 import ast
    #                 line = line.split("account position changed:")[1]
    #                 line = ast.literal_eval(line)
    #                 line1 = [account[0] for account in line]
    #                 active_listbox.delete(0, tk.END)
    #                 for line in line1:
    #                     active_listbox.insert(tk.END,line)
    #             else:
    #                 update_log(line)
            
    #         process.stdout.close()
    #         process.stderr.close()
    #         process.wait()

    #         if process.returncode != 0:
    #             update_log(f"Error running fb_ads_automate.py with return code {process.returncode}")

    #     except subprocess.CalledProcessError as e:
    #         logger.error(f"Error running fb_ads_automate.py: {e}")  
    #         logger.error(e.stderr)
    #     except Exception as e:
    #         logger.error(f"Unexpected error: {e}")


    # ********************************

    def products_renew():
        selected_idx = group_listbox.curselection()
        additional_number = additional_number_entry.get()
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a group.")
            return

        renew_start = renew_start_entry.get() 
        renew_end = renew_end_entry.get()

        if (renew_start == "Start renew" or not renew_start) or (renew_end == "End renew" or not renew_end):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT renew_lower_limit,renew_upper_limit FROM settings")
            renew_numbers = cursor.fetchall()
            conn.close()

            renew_numbers = renew_numbers[0]
            renew_number1 , renew_number2 = renew_numbers
            random_renew_number = (random.randint(renew_number1, renew_number2))
            logger.info(random_renew_number)
        else:
            try:
                renew_start_number = int(renew_start)
                renew_end_number = int(renew_end)

                if renew_start_number > renew_end_number:
                    messagebox.showerror("Error", "Start renew should be less than or equal to end renew.")
                    return
                    
                    # Generate a random number if inputs are valid
                random_renew_number = random.randint(renew_start_number, renew_end_number)

            except ValueError:
                messagebox.showwarning("Invalid Input", "Renew start and end values must be valid integers.")
                return
            
        selected_group_id = group_ids[selected_idx[0]]
        start_logging()  # Start logging
        
        threading.Thread(target=renew, args=(selected_group_id, additional_number, random_renew_number), daemon=True).start()

    # def renew(group_id, additional_number, random_renew):
    #     try:
    #         post_path = os.path.join(base_path, 'renew.exe')
    #         process = subprocess.Popen([post_path, str(group_id), str(additional_number), str(random_renew)], 
    #             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,creationflags=subprocess.CREATE_NO_WINDOW )

    #         for line in iter(process.stdout.readline, ''):
    #             update_log(line)
                
    #         process.stdout.close()
    #         process.stderr.close()
    #         process.wait()

    #         if process.returncode != 0:
    #             update_log(f"Error running renew.py with return code {process.returncode}")
    #     except subprocess.CalledProcessError as e:
    #         logger.error(f"Error running renew.py: {e}")
    #         logger.error(e.stderr)
    #     except Exception as e:
    #         logger.error(f"Unexpected error: {e}")

    # ********************************                                                                            

    def products_delete_relist():
        selected_idx = group_listbox.curselection()
        additional_number = additional_number_entry.get()
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a group.")
            return

        to_delete_start = to_delete_start_entry.get()
        to_delete_end = to_delete_end_entry.get()

        if (to_delete_start == "Start delete&relist" or not to_delete_start) or (to_delete_end == "End delete&relist" or not to_delete_end):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT delete_and_relist_lower_limit,delete_and_relist_upper_limit FROM settings")
            delete_relist_numbers = cursor.fetchall()
            conn.close()
            
            delete_relist_numbers = delete_relist_numbers[0]
            delete_relist_number1 , delete_relist_number2 = delete_relist_numbers
            random_delete_relist = (random.randint(delete_relist_number1, delete_relist_number2))
            logger.info(random_delete_relist)
        else:
            try:
                to_delete_start = int(to_delete_start)
                to_delete_end = int(to_delete_end)

                if to_delete_start > to_delete_end:
                    messagebox.showerror("Error", "Start delete&relist should be less than or equal to end delete&relist.")
                    return
                        
                    # Generate a random number if inputs are valid
                random_delete_relist = random.randint(to_delete_start, to_delete_end)

            except ValueError:
                messagebox.showwarning("Invalid Input", "start and end to delete and relist must be valid integers.")
                return
        
        selected_group_id = group_ids[selected_idx[0]]
        start_logging()  # Start logging
        
        threading.Thread(target=delete_relist, args=(selected_group_id, additional_number, random_delete_relist), daemon=True).start()
    # def delete_relist(group_id, additional_number, random_delete_relist):
    #     try:
    #         post_path = os.path.join(base_path, 'delete_and_relist.exe')
    #         process = subprocess.Popen([post_path , str(group_id), str(additional_number), str(random_delete_relist)], 
    #             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,creationflags=subprocess.CREATE_NO_WINDOW)

    #         for line in iter(process.stdout.readline, ''):
    #             update_log(line)
                
    #         process.stdout.close()
    #         process.stderr.close()
    #         process.wait()

    #         if process.returncode != 0:
    #             update_log(f"Error running delete_and_relist.py with return code {process.returncode}")
    #     except subprocess.CalledProcessError as e:
    #         logger.error(f"Error running delete_and_relist.py: {e}")
    #         logger.error(e.stderr)
    #     except Exception as e:
    #         logger.error(f"Unexpected error: {e}")


# *************************

    def call_selected_function():
        selected_action = selected_option.get()

        if selected_action == "Post":
            post_products()
        elif selected_action == "Renew":
            products_renew()
        elif selected_action == "Delete and Relist":
            products_delete_relist()


    def delete_selected_group():
        selected_group = group_listbox.curselection()
        if selected_group:
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this group?")
            if confirm:
                group_name = group_listbox.get(selected_group)
                conn = sqlite3.connect('fb_ads_database.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM groups WHERE group_name = ?', (group_name,))
                conn.commit()
                conn.close()
                messagebox.showinfo("success","group deleted successfully")
                refresh_groups()
        else:
            messagebox.showwarning("Warning", "Please select a group to delete.")
        # selected_idx = group_listbox.curselection()
        # global group_ids
        # if not selected_idx:
        #     messagebox.showwarning("No Selection", "Please select a group.")
        #     return
        
        # selected_group_id = group_ids[selected_idx[0]]
        # confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this group?")

        # if confirm:
        #     conn = get_connection()
        #     cursor = conn.cursor()
        #     cursor.execute("DELETE FROM groups WHERE group_name=?", (selected_group_id,))
        #     conn.commit()
        #     conn.close()
        #     messagebox.showinfo("Success", "Group deleted successfully.")
        #     refresh_groups()

    def add_new_group():
        try:
            create_group_GUI(user_id,refresh_groups)

            # create_group = os.path.join(base_path, 'create_group_GUI.exe')
            # subprocess.Popen([create_group],creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            logger.error(f"the error is {e}")

    def add_new_product():
        insert_product_GUI()
        # insert_product = os.path.join(base_path, 'insert_product_GUI.exe')
        # subprocess.Popen([insert_product],creationflags=subprocess.CREATE_NO_WINDOW)

    def open_display_product():
        display_product_GUI()
        # display_product = os.path.join(base_path, "display_product_GUI.exe")
        # subprocess.Popen([display_product],creationflags=subprocess.CREATE_NO_WINDOW)

    def add_more_products():
        selected_idx = group_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a group.")
            return

        group_id = group_ids[selected_idx[0]]
        add_more_products_GUI(group_id)
        # add_more_products = os.path.join(base_path, 'add_more_products_GUI.exe')
        # subprocess.Popen([add_more_products, str(group_id)],creationflags=subprocess.CREATE_NO_WINDOW)
    
    def insert_accounts():
        selected_idx = group_listbox.curselection()
        if not selected_idx:               
            messagebox.showwarning("No Selection", "Please select a group.")
            return
        group_id = group_ids[selected_idx[0]]
        insert_account(group_id)
        # add_accounts = os.path.join(base_path, 'insert_accounts.exe')
        # subprocess.Popen([add_accounts, str(group_id)],creationflags=subprocess.CREATE_NO_WINDOW)

    def is_active():
        selected_idx = group_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a group.")
            return
        group_id = group_ids[selected_idx[0]]
        active_unactive(group_id)
        # active_unactive = os.path.join(base_path, 'active_unactive.exe')
        # subprocess.Popen([active_unactive, str(group_id)],creationflags=subprocess.CREATE_NO_WINDOW)

    def remove_products():
        selected_idx = group_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a group.")
            return

        group_id = group_ids[selected_idx[0]]
        remove_products_GUI(group_id)
        # remove_products = os.path.join(base_path, 'remove_products_GUI.exe')
        # subprocess.Popen([remove_products, str(group_id)],creationflags=subprocess.CREATE_NO_WINDOW)

    def refresh_groups():
        group_listbox.delete(0, tk.END)
        groups = fetch_groups()
        global group_ids, group_names
        group_ids = [group[0] for group in groups]
        group_names = [group[1] for group in groups]
        for group_name in group_names:
            group_listbox.insert(tk.END, group_name)
        # group_listbox.delete(0, tk.END)  # Clear existing list
        # conn = sqlite3.connect('fb_ads_database.db')
        # cursor = conn.cursor()
        # cursor.execute('SELECT * FROM groups')
        # for row in cursor.fetchall():
        #     group_listbox.insert(tk.END, row[1])  # Display the group name
        # conn.close()

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

    def open_new_account_window():
        # subprocess.Popen(['python', 'na_GUI.py'])
        na_GUI()
        # na_gui= os.path.join(base_path, 'na_GUI.exe')
        # subprocess.Popen([na_gui],creationflags=subprocess.CREATE_NO_WINDOW)

    def setting():
        # settings= os.path.join(base_path, 'settings.exe')
        # subprocess.Popen([settings],creationflags=subprocess.CREATE_NO_WINDOW)
        fb_settings()    


    # ******* ******* ******* schedule ******* ******* *******
    

    def schedule():
        selected_idx = group_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a group.")
            return

        additional_number = additional_number_entry.get()
        price_start = price_start_entry.get()
        price_end = price_end_entry.get()
        time_speed1 = get_speed_value()
        start_action = start_action_entry.get()
        end_action = end_action_entry.get()
       

        if not additional_number.isdigit() or additional_number > batch_size[0]:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer or integer should not greater than default integer.")
            return
            
        if (price_start == "Start price" or not price_start) or (price_end == "End price" or not price_end):
            # cursor.execute("SELECT start_price, end_price FROM settings")
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT price FROM product")
            prices = cursor.fetchall()
            print(prices)
            conn.close()

            random_price = prices
            # prices = prices[0]
            # price1 ,price2 = prices
            # random_price = (random.uniform(price1, price2))
            # random_price = int(round(random_price, 0))
            # logger.info(random_price)
        else:
            try:
                price_start = int(price_start)
                price_end = int(price_end)

                if price_start > price_end:
                    messagebox.showerror("Error", "Start price should be less than or equal to end price.")
                    return
                
                divisible_by_5 = [i for i in range(price_start, price_end + 1) if i % 5 == 0]
                # Check if there are any numbers divisible by 5 in the range
                if divisible_by_5:
                    random_price = random.choice(divisible_by_5)
                    # Generate a random number if inputs are valid
                else:    
                    random_price = random.randint(price_start, price_end)

            except ValueError:
                messagebox.showwarning("Invalid Input", "start price and end price values must be valid integers.")
                return
            

        if (not start_action ) or (not end_action):
            start_action = 1
            end_action = 1
            post_action = random.randint(start_action, end_action)
        else:
            try:
                start_action = int(start_action)
                end_action = int(end_action)

                if start_action > end_action:
                    messagebox.showerror("Error", "Start action should be less than or equal to end action.")
                    return
                    
                # Generate a random number if inputs are valid
                post_action = random.randint(start_action, end_action)

            except ValueError:
                messagebox.showwarning("Invalid Input", "start and end actions be valid integers.")
                return

        selected_group_id = group_ids[selected_idx[0]]
        start_logging()  # Start logging
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM group_accounts WHERE group_id = ? AND is_active = 'True'", (selected_group_id,))
        active_accounts = cursor.fetchall()
        cursor.execute("SELECT email FROM group_accounts WHERE group_id = ? AND is_active = 'False'", (selected_group_id,))
        unactive_accounts = cursor.fetchall()
        conn.close()

        # Clear the listboxes before populating
        active_listbox.delete(0, tk.END)
        inactive_listbox.delete(0, tk.END)

        # Populate the active accounts listbox
        for account in active_accounts:
            active_listbox.insert(tk.END, account[0])  # Insert only the email
        
        # Populate the inactive accounts listbox
        for account in unactive_accounts:
            inactive_listbox.insert(tk.END, account[0]) 

        shuffle_account = entry_var.get()


        threading.Thread(target=run_schedule, args=(selected_group_id, additional_number, random_price, time_speed1, post_action, shuffle_account), daemon=True).start()

    def run_schedule(group_id, additional_number, random_price, time_speed1, post_action, shuffle_account):
        try:
            post_path = os.path.join(base_path, 'schedule.exe')
            process = subprocess.Popen([post_path, str(group_id), str(additional_number), str(random_price), str(time_speed1), str(post_action), str(shuffle_account)], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,creationflags=subprocess.CREATE_NO_WINDOW)

            for line in iter(process.stdout.readline, ''):
                update_log(line)
            
            process.stdout.close()
            process.stderr.close()
            process.wait()

            if process.returncode != 0:
                update_log(f"Error running schedule.exe with return code {process.returncode}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running schedule.exe: {e}")
            logger.error(e.stderr)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")


################


    def set_placeholder(entry, placeholder):
        entry.insert(0, placeholder)
        entry.config(fg='grey')
        entry.bind("<FocusIn>", lambda event: clear_placeholder(event, placeholder))
        entry.bind("<FocusOut>", lambda event: add_placeholder(event, placeholder))

    def clear_placeholder(event, placeholder):
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.config(fg='black')

    def add_placeholder(event, placeholder):
        if not event.widget.get():
            event.widget.insert(0, placeholder)
            event.widget.config(fg='grey')

    # Function to toggle the "always on top" state
    def toggle_pin():
        if root.attributes("-topmost"):
            root.attributes("-topmost", False)
            pin_button.config(text="Pin")
        else:
            root.attributes("-topmost", True)
            pin_button.config(text="Unpin")

    # Create main Tkinter window
    root = tk.Tk()
    root.title("Facebook Marketplace Automation")

    # Define validation function to accept only integers
    def validate_input(value_if_allowed):
        # Allow only digits and an empty string (for clearing the entry)
        if value_if_allowed.isdigit() or value_if_allowed == "":
            return True
        else:
            return False

    vcmd = (root.register(validate_input), '%P')

    input_frame = tk.Frame(root)
    input_frame.pack(side=tk.TOP, anchor="w", padx=10, pady=10)

    # Create labels for input fields
    tk.Label(input_frame, text="Batch size:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
    tk.Label(input_frame, text="Plateform type:").grid(row=0, column=1, padx=5, pady=5, sticky='w')
    tk.Label(input_frame, text="Action type:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
    tk.Label(input_frame, text="Start Action:").grid(row=0, column=3, padx=5, pady=5, sticky='w')
    tk.Label(input_frame, text="End Action:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
    tk.Label(input_frame, text="Start renew:").grid(row=0, column=5, padx=5, pady=5, sticky='w')
    tk.Label(input_frame, text="End renew:").grid(row=0, column=6, padx=5, pady=5, sticky='w')
    tk.Label(input_frame, text="Start delete&relist:").grid(row=0, column=7, padx=5, pady=5, sticky='w')
    tk.Label(input_frame, text="End delete&relist:").grid(row=0, column=8, padx=5, pady=5, sticky='w')
    tk.Label(input_frame, text="Start price:").grid(row=0, column=9, padx=5, pady=5, sticky='w')
    tk.Label(input_frame, text="End price:").grid(row=0, column=10, padx=5, pady=5, sticky='w')
    tk.Label(input_frame, text="Post speed:").grid(row=0, column=11, padx=5, pady=5, sticky='w')

    # Create input fields
    additional_number_entry = tk.Entry(input_frame, width=10)
    additional_number_entry.insert(0, batch_size[0])
    additional_number_entry.grid(row=1, column=0, padx=5, pady=5)
    additional_number_entry.config(state=tk.DISABLED)

    plateform = tk.Entry(input_frame, width=15)
    plateform.insert(0,"Facebook")
    plateform .grid(row=1, column=1, padx=5, pady=5)   
    plateform.config(state=tk.DISABLED)
    
    # Create options
    options = ["Post", "Renew", "Delete and Relist"]

    # Create a StringVar to store the selected value
    selected_option = tk.StringVar()
    default_value = "Post"  # Set default value to "Selection"
    selected_option.set(default_value)

    # Create the combobox
    combobox = ttk.Combobox(input_frame, textvariable=selected_option, values=options, width=12)
    combobox.grid(row=1, column=2, padx=5, pady=5)
    combobox.config(state='readonly')

    start_action_entry = tk.Entry(input_frame, width=12, validate="key", validatecommand=vcmd)
    start_action_entry.insert(0,action[0])
    start_action_entry.grid(row=1, column=3, padx=5, pady=5)    

    end_action_entry = tk.Entry(input_frame, width=12, validate="key", validatecommand=vcmd)
    end_action_entry.insert(0,action[1])
    end_action_entry.grid(row=1, column=4, padx=5, pady=5)   

    renew_start_entry = tk.Entry(input_frame, validate="key", validatecommand=vcmd)
    # set_placeholder(renew_start_entry, "Start renew")
    renew_start_entry.grid(row=1, column=5, padx=5, pady=5)

    renew_end_entry = tk.Entry(input_frame, validate="key", validatecommand=vcmd)
    # set_placeholder(renew_end_entry, "End renew")
    renew_end_entry.grid(row=1, column=6, padx=5, pady=5)

    to_delete_start_entry = tk.Entry(input_frame)
    # set_placeholder(to_delete_start_entry, "Start delete&relist")
    to_delete_start_entry.grid(row=1, column=7, padx=5, pady=5)

    to_delete_end_entry = tk.Entry(input_frame, validate="key", validatecommand=vcmd)
    # set_placeholder(to_delete_end_entry, "End delete&relist")
    to_delete_end_entry.grid(row=1, column=8, padx=5, pady=5)

    price_start_entry = tk.Entry(input_frame, validate="key", validatecommand=vcmd)
    # set_placeholder(price_start_entry, "Start price")
    price_start_entry.grid(row=1, column=9, padx=5, pady=5)

    price_end_entry = tk.Entry(input_frame, validate="key", validatecommand=vcmd)
    # set_placeholder(price_end_entry, "End price")
    price_end_entry.grid(row=1, column=10, padx=5, pady=5)

    def get_speed_value():
        selected_text = selected_speed.get()
        for text, value in speed_options:
            if text == selected_text:
                return value
        return None

    speed_options = [
    ("Calm", 5),
    ("Normal", 3),
    ("2x", 2),
    ("Fast", 1)]

    # Create a StringVar to store the selected value
    selected_speed = tk.StringVar()
    default_value = "Normal"  # Set default value to "Normal"
    selected_speed.set(default_value)

    # Create the combobox
    combobox = ttk.Combobox(input_frame, textvariable=selected_speed, values=[text for text, _ in speed_options],width=7)
    combobox.grid(row=1, column=11,padx=5, pady=5)
    combobox.config(state='readonly')

    # Frame for the label and listbox layout
    listboxes_frame = tk.Frame(root)
    listboxes_frame.pack(side=tk.TOP, anchor="w", padx=10, pady=10)

    # Label for Group Listbox
    group_label = tk.Label(listboxes_frame, text="Select a Group:")
    group_label.grid(row=0, column=0, sticky="w")

    # Listbox for Groups
    groups = fetch_groups()
    group_ids = [group[0] for group in groups]
    group_names = [group[1] for group in groups]
    group_listbox = tk.Listbox(listboxes_frame, selectmode=tk.SINGLE, width=30, height=8)
    for group_name in group_names:
        group_listbox.insert(tk.END, group_name)
    group_listbox.grid(row=1, column=0, padx=5, pady=5)
    
    # Label for Active Accounts Listbox
    active_label = tk.Label(listboxes_frame, text="Active Accounts")
    active_label.grid(row=0, column=1, sticky="w")

    # Listbox for Active Accounts
    active_listbox = tk.Listbox(listboxes_frame, width=30, height=8)
    active_listbox.grid(row=1, column=1, padx=5, pady=5)

    # Label for Inactive Accounts Listbox
    inactive_label = tk.Label(listboxes_frame, text="Inactive Accounts")
    inactive_label.grid(row=0, column=2, sticky="w")

    # Listbox for Inactive Accounts
    inactive_listbox = tk.Listbox(listboxes_frame, width=30, height=8)
    inactive_listbox.grid(row=1, column=2, padx=5, pady=5)

    account_status_listbox = tk.Label(listboxes_frame, text="Blocked/disabled")
    account_status_listbox.grid(row=0, column=3, sticky="w")

    account_status_listbox = tk.Listbox(listboxes_frame, width=30, height=8)
    account_status_listbox.grid(row=1, column=3, padx=5, pady=5)



    # Create a frame for buttons below the group list
    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.TOP, anchor="w", padx=10, pady=10)

    btn_run_group = tk.Button(button_frame, text="Start", command=call_selected_function)
    btn_run_group.pack(side=tk.LEFT, padx=5, pady=5)

    btn_delete_group = tk.Button(button_frame, text="Delete Selected Group", command=delete_selected_group)
    btn_delete_group.pack(side=tk.LEFT, padx=5, pady=5)

    btn_add_group = tk.Button(button_frame, text="Add New Group", command=add_new_group)
    btn_add_group.pack(side=tk.LEFT, padx=5, pady=5)

    btn_add_product = tk.Button(button_frame, text="Add Product", command=add_new_product)
    btn_add_product.pack(side=tk.LEFT, padx=5, pady=5)

    btn_display_products = tk.Button(button_frame, text="Display Products", command=open_display_product)
    btn_display_products.pack(side=tk.LEFT, padx=5, pady=5)

    btn_add_more_products = tk.Button(button_frame, text="Add More Products", command=add_more_products)
    btn_add_more_products.pack(side=tk.LEFT, padx=5, pady=5)

    btn_remove_products = tk.Button(button_frame, text="Remove Products", command=remove_products)
    btn_remove_products.pack(side=tk.LEFT, padx=5, pady=5)

    btn_new_account = tk.Button(button_frame, text="New Account", command=open_new_account_window)
    btn_new_account.pack(side=tk.LEFT, padx=5, pady=5)

    btn_new_account = tk.Button(button_frame, text="Setting", command=setting)
    btn_new_account.pack(side=tk.LEFT, padx=5, pady=5)


    btn_schedule = tk.Button(button_frame, text="Schedule", command=schedule)
    btn_schedule.pack(side=tk.LEFT, padx=5, pady=5)

    btn_refresh_groups = tk.Button(button_frame, text="Refresh Database", command=refresh_groups)
    btn_refresh_groups.pack(side=tk.LEFT, padx=5, pady=5)

    btn_insert_accounts = tk.Button(button_frame, text="Add More Accounts", command=insert_accounts)
    btn_insert_accounts.pack(side=tk.LEFT, padx=5, pady=5)

    btn_isActive_accounts = tk.Button(button_frame, text="Active/un-active", command=is_active)
    btn_isActive_accounts.pack(side=tk.RIGHT, padx=5, pady=5)

    # Create a frame for the input fields and pin button
    input_frame = tk.Frame(root)
    input_frame.pack(side=tk.TOP, anchor="w", padx=10, pady=10)

    # Add the "Pin" button
    pin_button = tk.Button(input_frame, text="Pin", command=toggle_pin)
    pin_button.grid(row=0, column=9, padx=5, pady=5)

    def connect_vpn():
        try:
            vpn_command = [
                r"C:\Program Files\OpenVPN\bin\openvpn.exe",  # Adjust the path as necessary
                "--config", "uk-lon.prod.surfshark.comsurfshark_openvpn_udp.ovpn",
                "--auth-user-pass", "auth.txt"
            ]
            vpn_process = subprocess.Popen(vpn_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            vpn_label.config(text="VPN is connected.")
            time.sleep(10)  # Give it some time to connect to the VPN
            return vpn_process.pid  # Return the process ID to later disconnect the VPN
        except:
            vpn_label.config(text="VPN is not connected.")

    def disconnect_vpn(vpn_pid):
        # Find the process using the given PID and terminate it
        try:
            vpn_process = psutil.Process(vpn_pid)
            vpn_process.terminate()  # Graceful termination
            vpn_process.wait(timeout=5)  # Wait up to 5 seconds for termination
            vpn_label.config(text="VPN disconnected.")
        except psutil.NoSuchProcess:
            vpn_label.config(text=f"No process found with PID {vpn_pid}.")
        except psutil.TimeoutExpired:
            vpn_label.config(f"Failed to gracefully terminate process with PID {vpn_pid}, forcing termination.")
            vpn_process.kill()  # Force termination if it didn't stop gracefully


    def enable_vpn():
        global vpn_pid
        if entry_var.get() == "":
            entry_var.set("1")
            vpn_pid  = connect_vpn()
        else:
            entry_var.set("")
            try:
                disconnect_vpn(vpn_pid)
            except NameError:
                vpn_label.config(text="VPN is not running.")

    entry_var = tk.StringVar()
    vpn_button = tk.Button(input_frame, text="Enable VPN", command=enable_vpn)
    vpn_button.grid(row=0, column=10, padx=5, pady=5)
    vpn_label = tk.Label(input_frame, text="VPN disconnected.")
    vpn_label.grid(row=1, column=10)

    def update_value():
        value = var.get()
        if value:
            entry_var.set("1")
        else:
            entry_var.set("0")

    var = tk.BooleanVar()

    # Create a Tkinter StringVar to hold the processed value
    entry_var = tk.StringVar(value="0") 

    # Create a checkbox and link it to the Tkinter variable
    checkbox = tk.Checkbutton(input_frame, text="Shuffle", variable=var, command=update_value)
    checkbox.grid(row=0, column=11, padx=5, pady=5)



    # Create a Text widget for log display at the bottom
    log_display = scrolledtext.ScrolledText(root, width=100, height=15, wrap=tk.WORD, state=tk.DISABLED)
    log_display.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10)

    root.mainloop()

# Function to handle login
def login():
    def authenticate():
        username = username_entry.get()
        password = password_entry.get()
        mac = uuid.getnode()
        mac_address = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM users WHERE username=? AND password=? AND validated=1 AND machine_address =?", (username, password, mac_address))
            user = cursor.fetchone()
            if user:
                user_id = user[0]
                login_window.destroy()  # Close the login window
                open_cmd_and_run_script('scheduler.exe')
                app(username,user_id)  # Open the main app window
            else:
                messagebox.showerror("Login Failed", "Invalid username/password or account not validated or you are not able to login from this machine.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry('300x300')

    tk.Label(login_window, text="Username:").pack(padx=10, pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(padx=10, pady=5)

    tk.Label(login_window, text="Password:").pack(padx=10, pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(padx=10, pady=5)

    login_button = tk.Button(login_window, text="Login",width=15, command=authenticate)
    login_button.pack(pady=10)

    register_button = tk.Button(login_window, text="Register",width=15, command=register)
    register_button.pack(pady=5)

    login_window.mainloop()

# Function to handle registration

# Function to validate email and phone number
def validate_input(username):
    # Regex pattern for validating email
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    # Regex pattern for validating a phone number with exactly 11 digits
    phone_pattern = r'^\d{11}$'
    
    # Check if it matches email format
    if re.match(email_pattern, username):
        return "email"
    
    # Check if it matches 11-digit phone number format
    elif re.match(phone_pattern, username):
        return "phone"
    
    # If neither email nor phone number is valid, return False
    return False

# Function to validate password
def validate_password(password):
    # Password must be at least 8 characters long
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    
    # Password must contain at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter."
    
    # Password must contain at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter."
    
    # Password must contain at least one digit
    if not re.search(r'\d', password):
        return "Password must contain at least one digit."
    
    # Password must contain at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character."
    
    # If all conditions are met, return True
    return True

def register():
    def create_account():
        username = username_entry.get()
        password = password_entry.get()

        # Perform validation
        validation_result = validate_input(username)
        if validation_result == False:
            messagebox.showerror("Invalid Input", "The input must be a valid email address or 11-digit phone number!")
            return  # Exit the function if validation fails

         # Perform validation for password
        password_validation_result = validate_password(password)
        if password_validation_result != True:
            messagebox.showerror("Invalid Password", password_validation_result)
            return  # Exit the function if password validation fails

        mac = uuid.getnode()
        mac_address = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Insert new user with validated=1
            cursor.execute("INSERT INTO users (username, password, machine_address, validated) VALUES (?, ?, ?, 1)", (username, password, mac_address))
            cursor.execute("INSERT INTO access (username, batch_size) VALUES (?, '1')", (username,))
            conn.commit()
            messagebox.showinfo("Registration Successful", "Your account has been created successfully. You can now login.")
            register_window.destroy()
            login()  # Automatically open login window
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    register_window = tk.Tk()
    register_window.title("Register")
    register_window.geometry('300x300')

    tk.Label(register_window, text="Username:").pack(padx=10, pady=5)
    username_entry = tk.Entry(register_window)
    username_entry.pack(padx=10, pady=5)

    tk.Label(register_window, text="Password:").pack(padx=10, pady=5)
    password_entry = tk.Entry(register_window, show="*")
    password_entry.pack(padx=10, pady=5)

    register_button = tk.Button(register_window, text="Register", command=create_account)
    register_button.pack(pady=10)

    register_window.mainloop()

# Main script execution
if __name__ == "__main__":
    login()