import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
from db_connection import get_connection
import logging
import threading
from fake_useragent import UserAgent 


# Configure logging
logger = logging.getLogger('fb_ads_logger')
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(log_handler)

def get_group_accounts(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email, password FROM group_accounts WHERE group_id = ? AND is_active = 'True'", (group_id,))
    accounts = cursor.fetchall()
    conn.close()
    return accounts


def login_facebook(driver, email, password, delete_relist):
    driver.get("https://www.facebook.com/login")
    time.sleep(5)
    try:
        email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
        email_field.click()
        email_field.send_keys(email)

        password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pass')))
        password_field.click()
        password_field.send_keys(password)
        time.sleep(3)

        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'loginbutton')))
        login_button.click()

        time.sleep(5)
        
        # Navigate to the dashboard page after login
        driver.get("https://web.facebook.com/marketplace/you/dashboard")

        time.sleep(5)

        # Extract the value from the dashboard
        extract_dashboard_value(driver, delete_relist)

    except Exception as e:
        logger.error(f"An error occurred during login: {e}")

def extract_dashboard_value(driver, delete_relist):
    try:

        time.sleep(3)

        try:
            to_delete_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//div[@role='listitem']//a[.//span[contains(text(), 'To delete & relist') or contains(text(), 'To delete and relist')]]//span[1]")))
            to_delete_value = to_delete_element.text
            print(f"delete and relist: {to_delete_value}")
        except:
            print("element not found")
        time.sleep(3)

        # print(f"to delete and relist: {to_delete_value}")
        if delete_relist == 0:
            pass
        elif int(to_delete_value) >=  delete_relist:

            to_delete_div = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='listitem']//a[.//span[contains(text(), 'To delete & relist') or contains(text(), 'To delete and relist')]]//span[1]")))
            to_delete_div.click()

            time.sleep(3)

            delete_relist_buttons = driver.find_elements(By.XPATH, "//div[@role='button']//span[text()='Delete & relist']")

            for delete_relist_button in delete_relist_buttons[:delete_relist]:
                try:
                    actions = ActionChains(driver)
                    actions.move_to_element(delete_relist_button).perform()
                    delete_relist_button.click()
                    
                    time.sleep(2)

                except Exception as e:
                    print(f"Failed to click on a delete & relist button: {e}")

            time.sleep(2)

            to_delete_done = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @tabindex='0']//span[text()='Done']")))
            to_delete_done.click()
            driver.refresh()     

            time.sleep(5)

        else:
            pass
        
        time.sleep(5)
    
    except Exception as e:
        logger.error(f"An error occurred while extracting the dashboard value: {e}")
        return None

##################### manage multiple account simultaneously #####################


def worker(email, password, delete_relist):
    """
    Worker function to handle posting for a single account.

    Args:
        email (str): Account email.
        password (str): Account password.
        product_ids (list): List of product IDs to post.
        last_used_titles (dict): Dictionary of last used titles.
    """
    ua = UserAgent()
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument(f"user-agent={ua.random}")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    
    # driver = webdriver.Chrome(options=chrome_options)
    try:
        # Check if ChromeDriver is available
        driver = webdriver.Chrome(options=chrome_options)
        print("ChromeDriver is already installed and available.")
    except Exception as e:
        print("ChromeDriver not found. Installing...")
        # Install ChromeDriver using webdriver-manager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        driver.quit()
        print("ChromeDriver installed successfully.")
    login_facebook(driver, email, password, delete_relist)

    time.sleep(5)
    # renew_list(driver)

    driver.quit()

def open_instances(num_instances, accounts, delete_relist):
    """
    Opens multiple instances of a web browser concurrently.

    Args:
        num_instances (int): Number of browser instances to open.
        product_ids (list): List of product IDs to post.
        last_used_titles (dict): Dictionary of last used titles.
        accounts (list): List of account credentials.
    """
    threads = []

    account_index = 0
    while account_index < len(accounts):
        for _ in range(min(num_instances, len(accounts) - account_index)):
            email, password = accounts[account_index]
            thread = threading.Thread(target=worker, args=(email, password, delete_relist))
            thread.start()
            threads.append(thread)
            account_index += 1

        for thread in threads:
            thread.join()


def delete_relist(group_id, additional_number, delete_relist):
    # if len(sys.argv) != 4:
    #     logger.info("Usage: python delete_and_relist.py <group_id> <additional_number> <delete relist>")
    #     sys.exit(1)
    # logger.info("Starting automation...")
    # group_id = int(sys.argv[1])
    # additional_number = int(sys.argv[2])
    # delete_relist = int(sys.argv[3])

    # logger.info(f"batch value received: {additional_number}")
    # logger.info(f"delete and relist value received: {delete_relist}")
    
    accounts = get_group_accounts(group_id)

    logged_in_sessions = {}
    last_used_titles = {}

    if additional_number <= 1:
        for account in accounts:
            email, password = account

            if email not in logged_in_sessions:
                try:
                    # Check if ChromeDriver is available
                    chrome_options = Options()
                    chrome_options.add_argument("--disable-notifications")
                    chrome_options.add_argument('--ignore-certificate-errors')
                    chrome_options.add_argument('--ignore-ssl-errors')
                    driver = webdriver.Chrome(options=chrome_options)
                    # print("ChromeDriver is already installed and available.")
                except Exception as e:
                    # print("ChromeDriver not found. Installing...")
                    # Install ChromeDriver using webdriver-manager
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
                    chrome_options = Options()
                    chrome_options.add_argument("--disable-notifications")
                    chrome_options.add_argument('--ignore-certificate-errors')
                    chrome_options.add_argument('--ignore-ssl-errors')
                    driver = webdriver.Chrome(options=chrome_options)
                    # print("ChromeDriver installed successfully.")
                login_facebook(driver, email, password, delete_relist)
                logged_in_sessions[email] = driver
                last_used_titles[email] = None
            else:
                driver = logged_in_sessions[email]
            
    else:
        open_instances(additional_number, accounts, delete_relist)

    time.sleep(10)
    for driver in logged_in_sessions.values():
        driver.quit()




if __name__ == "__main__":
   delete_relist()