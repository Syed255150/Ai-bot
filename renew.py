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

def login_facebook(driver, email, password, renew_number):
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
        extract_dashboard_value(driver, renew_number)

    except Exception as e:
        logger.error(f"An error occurred during login: {e}")

def extract_dashboard_value(driver, renew_number):
    try:
        
        renew_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='listitem']//a[.//span[contains(text(), 'To renew')]]//span[1]")))
        renew_value = renew_element.text
        print(f"renew value:{renew_value}")

        time.sleep(3)

        if renew_number == 0:
            pass
        elif int(renew_value) >= renew_number:
            renew_div = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='listitem']//a[.//span[text()='To renew']]")))
            renew_div.click()

            time.sleep(7)

            renew_buttons = driver.find_elements(By.XPATH, "//div[@role='button']//span[text()='Renew']")
            # print(f"Number of listing found: {len(renew_buttons)}")
            time.sleep(3)
    
            for renew_button in renew_buttons[:renew_number]:
                try:
                    actions = ActionChains(driver)
                    actions.move_to_element(renew_button).perform()
                    
                    renew_button.click()
                    
                    time.sleep(2)

                except Exception as e:
                    print(f"Failed to click on a Renew button: {e}")

            time.sleep(2)

            renew_done = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @tabindex='0']//span[text()='Done']")))
            renew_done.click()

            driver.refresh()     

            time.sleep(3)
            
        else:
            pass

        time.sleep(5)
    
    except Exception as e:
        logger.error(f"An error occurred while extracting the dashboard value: {e}")
        return None

##################### manage multiple account simultaneously #####################


def worker(email, password, renew_number):
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
    login_facebook(driver, email, password, renew_number)
    last_used_titles[email] = None

    time.sleep(5)
    # renew_list(driver)

    driver.quit()

def open_instances(num_instances, accounts, renew_number):
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
            thread = threading.Thread(target=worker, args=(email, password, renew_number))
            thread.start()
            threads.append(thread)
            account_index += 1

        for thread in threads:
            thread.join()


# ***********************
# ***********************
# ***********************

def renew(group_id, additional_number, random_renew_number):
    # if len(sys.argv) != 4:
    #     logger.info("Usage: python renew.py <group_id> <additional_number> <random_renew_number>")
    #     sys.exit(1)
    # logger.info("Starting automation...")
    # group_id = int(sys.argv[1])
    # additional_number = int(sys.argv[2])
    # renew_number = int(sys.argv[3])

    logger.info(f"batch value received: {additional_number}")
    logger.info(f"renew value received: {random_renew_number}")

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
                login_facebook(driver, email, password, random_renew_number)
                logged_in_sessions[email] = driver
                last_used_titles[email] = None
            else:
                driver = logged_in_sessions[email]
            
    else:
        open_instances(additional_number, accounts, random_renew_number)

    time.sleep(10)
    for driver in logged_in_sessions.values():
        driver.quit()




if __name__ == "__main__":
   renew()