import sys
import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
import random
from db_connection import get_connection
import logging
import threading
from fake_useragent import UserAgent 
import subprocess
import psutil

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

def get_group_products(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id FROM group_products WHERE group_id = ?", (group_id,))
    product_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return product_ids

def get_product_details(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, image_path, video_path, title, price, category, description, tags, location FROM product WHERE product_id = ?", (product_id,))
    product_details = cursor.fetchone()
    conn.close()
    return product_details

def login_facebook(driver, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_start_gap_in_sec FROM settings")
    account_delay_in_sec = cursor.fetchall()
    conn.close()

    account_delay_in_sec = account_delay_in_sec[0]
    account_delay_in_sec = int(account_delay_in_sec[0])
    
    time.sleep(account_delay_in_sec)

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
        
        url = driver.current_url
        if "blocked" in url or "disabled" in url:
            account_status = f"Account {email} is blocked/disabled"
            # print(account_status, flush=True)  # Flush output immediately
            logger.info(f"{account_status}")
            driver.quit()
            return
        elif "login_attempt" in  url: 
            driver.quit()
            return
        time.sleep(5)
    except ElementClickInterceptedException:
        decline_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Decline optional cookies')]")
        decline_button.click()
        time.sleep(3)
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
        
        url = driver.current_url
        if "blocked" in url or "disabled" in url:
            account_status = f"Account {email} is blocked/disabled"
            # print(account_status, flush=True)  # Flush output immediately
            logger.info(f"{account_status}")
            driver.quit()

        time.sleep(5)

    except Exception as e:
        logger.error(f"An error occurred during login {e}")


def post_product(driver, product_details, last_used_title=None, random_price = 0, time_speed = 3, tab_index=0):
    product_name, image_folder_path, video_path, title, price, category, description, tags, location = product_details
    # Switch to the appropriate tab
    driver.switch_to.window(driver.window_handles[tab_index])
    try:
        # driver.get("https://web.facebook.com/marketplace/create/item")
         # Navigate to the posting page if it's not already open
        time.sleep(3)
        url = driver.current_url
        if "blocked" in url or "disabled" in url:
            account_status = f"Account {email} is blocked/disabled"
            logger.info(f"{account_status}")  # Flush output immediately
            driver.quit()

        if "marketplace/create/item" not in driver.current_url:
            driver.get("https://web.facebook.com/marketplace/create/item")
            time.sleep(3)

        time.sleep(7)
        driver.implicitly_wait(10)

        # post_product = True

        try:
            limit_reached_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Limit reached')]")))
            if limit_reached_element.is_displayed():
                logger.info("You have reached the listing limit.")
                # post_product= False
                return
        except:
            pass

        def upload_img():

            file_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@accept='image/*,image/heif,image/heic' and @type='file']")))

            time.sleep(2)
            image_path = os.path.normpath(image_folder_path)
            images = []
            for file_name in os.listdir(image_path):
                file_path = os.path.join(image_path, file_name)
                if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    images.append(file_path)

            # Send the file path to the input element (without opening the file dialog)
            if images:
                file_input.send_keys(images[0])
        
        if title is None:
            print("Product title not Exist")
            return
       
        available_titles = title.split('\n')
        if len(available_titles) > 1 and last_used_title in available_titles:
            available_titles.remove(last_used_title)
        selected_title = random.choice(available_titles) if available_titles else last_used_title
        last_used_title = selected_title
        print(selected_title)
        title_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//label[contains(@aria-label, 'Title')]//input[contains(@class, 'x1i10hfl')]")))
        title_input.click()
        # title_input.send_keys(selected_title)

        time.sleep(time_speed)     

        title_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//label[contains(@aria-label, 'Title')]//input[contains(@class, 'x1i10hfl')]")))
        title_input.click()
        title_input.send_keys(selected_title)

        time.sleep(time_speed)
  
        price_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//label[contains(@aria-label, 'Price')]//input[contains(@class, 'x1i10hfl')]")))
        price_input.click()
        # price_input.send_keys(str(price))
        
        if random_price == 0:
            price_input.send_keys(str(price))
        else:
            price_input.send_keys(str(random_price))

        time.sleep(2)

        try:
            category_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//label[contains(@aria-label, 'Category')]")))
            category_dropdown.click()

            time.sleep(3)  

            furniture_category = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Furniture']")))
            furniture_category.click()

            time.sleep(3)

            input_category = category
            split_category = input_category.split(' > ')
            processed_category = split_category[1:]

            # Dictionary for category lookups
            furniture_categories = {
                'first': {
                    'Bedroom furniture', 'Dining room furniture', 'Living room furniture', 'Outdoor furniture',
                    'Bedroom Furniture', 'Dining Room Furniture', 'Living Room Furniture', 'Outdoor Furniture'
                },
                'first_single': {
                    'Armoires & wardrobe', 'Dressers', 'Armoires & Wardrobe'
                }
            }

            def select_category(category_name):
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{category_name}')]"))).click()
                    return True
                except Exception:
                    return False

            if len(processed_category) == 2:
                furniture_first_category = processed_category[0].strip().lower()
                furniture_second_category = processed_category[1].strip().lower()

                # Select first category
                for furniture_category in furniture_categories['first']:
                    if furniture_category.lower() == furniture_first_category:
                        if select_category(furniture_category):
                            break

                time.sleep(1)

                if "beds and bed frames" == furniture_second_category:
                    x = ["Beds and bed frames", "Beds & Bed Frames"]
                elif "mattresses" == furniture_second_category:
                    x = "Mattresses"
                elif "dining tables" == furniture_second_category:
                    x = ["Dining tables", "Dining Table"]
                elif "bar stools" == furniture_second_category:
                    x = ["Bar stools", "Bar Stools"]
                elif "coffee tables" == furniture_second_category:
                    x = ["Coffee tables", "Coffee Tables"]
                elif "sofas, love seats and sectionals" == furniture_second_category:
                    x = ["Sofas, love seats and sectionals", "Sofas, Loveseats & Sectionals"]
                elif "outdoor chairs, benches & swings" == furniture_second_category:
                    x = ["Outdoor chairs, benches & swings", "Outdoor Chairs, Benches & Swings"]
                elif "outdoor sofas" == furniture_second_category:
                    x = ["Outdoor sofas", "Outdoor Sofas"]
                else:
                    logger.info(f"Category '{furniture_second_category}' not found.")

                if isinstance(x, str):
                    select_category(x)
                elif isinstance(x, list):
                    for i in x:
                        if select_category(i):
                            break

            elif len(processed_category) == 1:

                furniture_first_category = processed_category[0].strip().lower()
                # Select single-level category
                for furniture_category in furniture_categories['first_single']:
                    if furniture_first_category in furniture_category.lower():
                        if select_category(furniture_category):
                            break
        except:
            pass

        time.sleep(time_speed)
    
        condition_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//label[contains(@aria-label, 'Condition')]")))
        condition_input.click()

        time.sleep(time_speed)

        # condition_option_text = "New"  
        condition_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@aria-selected='false' and @role='option']//span[text()='New']")))
        condition_option.click()

        time.sleep(3)

        try:
            # Wait until the "More details" button is present
            more_details_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'More details')]/ancestor::div[@role='button']")))
        
            # Check if the section is already expanded
            aria_expanded = more_details_button.get_attribute("aria-expanded")
            if aria_expanded == 'false':
                more_details_button.click()
        except Exception as e:
            logger.error(f"Exception occurred while trying to click 'More details': {e}")

        time.sleep(time_speed)

        description_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//label[contains(@aria-label, 'Description')]//following::textarea")))
        description_input.click()
        description_input.send_keys(description)

        time.sleep(time_speed)

        tags_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//label[contains(@aria-label, 'Product tags')]//following::textarea")))
        for tag in tags.split(','):
            tags_input.send_keys(tag.strip())
            tags_input.send_keys(Keys.ENTER)

        time.sleep(time_speed)

        location_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//label[contains(@aria-label, 'Location')]//following::input[@type='text']")))
        location_input.send_keys(Keys.CONTROL + "a")
        location_input.send_keys(Keys.DELETE)
        time.sleep(1)
        location_list = location.split('\n')
        random_location = random.choice([loc for loc in location_list if loc.strip()])
        location_input.send_keys(random_location)
    
        time.sleep(2)
        location = random_location.strip()
        try:
            dropdown_option = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, f"//span[contains(text(), '{location}')]")))
            dropdown_option.click()
        except:
            location_input.send_keys(Keys.ARROW_DOWN)  # Move to the first suggestion
            location_input.send_keys(Keys.ENTER) 

        time.sleep(time_speed)

        upload_img()

        time.sleep(2)
        time.sleep(time_speed)
        

        try:
            publish_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Publish']")))
            publish_button.click()
            time.sleep(3)
            time.sleep(time_speed)
            driver.implicitly_wait(10)
            logger.info("Product Post Successfully.")
            return True
        except:
            time.sleep(1)
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']/ancestor::div[@role='button']")))
            next_button.click()
            time.sleep(3)
            publish_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Publish']")))
            publish_button.click()
            time.sleep(3)
            time.sleep(time_speed)
            driver.implicitly_wait(10)
            logger.info("Product Post Successfully.")
            return True
        
    except Exception as e:
        logger.error(f"An error occurred while posting product: {e}")



##################### manage multiple account simultaneously #####################


def worker(email, password, product_ids, last_used_titles, random_price, time_speed, action_product):
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
    login_facebook(driver, email, password)
    last_used_titles[email] = None

    for index, product_id in enumerate(product_ids[:action_product]):
        product_details = get_product_details(product_id)
        driver.execute_script("window.open('https://web.facebook.com/marketplace/create/item');")
        driver.implicitly_wait(7)
        post_product(driver, product_details, last_used_titles[email], random_price, time_speed, tab_index=index + 1)
        last_used_titles[email] = product_details[3]

    time.sleep(5)
    # renew_list(driver)

    driver.quit()

def open_instances(num_instances, product_ids, last_used_titles, accounts, random_price, time_speed, action_product):
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
            thread = threading.Thread(target=worker, args=(email, password, product_ids, last_used_titles, random_price, time_speed, action_product))
            thread.start()
            threads.append(thread)
            account_index += 1

        for thread in threads:
            thread.join()


# ******************************
# ******************************
# ******************************
# ******************************
# ******************************

def main(group_id, additional_number, random_price, time_speed, post_action, shuffle_accounts):
     # if len(sys.argv) != 7:
    #     logger.info("Usage: python fb_ads_automate.py <group_id> <additional_number> <random price> <posting speed> <post action> <shuffle account>")
    #     sys.exit(1)
    logger.info("Starting automation...")
    # group_id = int(sys.argv[1])
    # additional_number = int(sys.argv[2])
    # random_price = int(sys.argv[3])
    # time_speed = int(sys.argv[4])
    # post_action = int(sys.argv[5])
    # shuffle_accounts = int(sys.argv[6])
    additional_number = int(additional_number)
    logger.info(f"batch value received: {additional_number}")
    logger.info(f"price received: {random_price}")
    accounts = get_group_accounts(group_id)

    if shuffle_accounts == 1:
        accounts = accounts[:]
        random.shuffle(accounts)
        logger.info(f"account position changed: {accounts}")

    product_ids = get_group_products(group_id)
    action_product = min(post_action,len(product_ids))

    logged_in_sessions = {}
    last_used_titles = {}

    if additional_number <= 1:
        for account in accounts:
            email, password = account

            if email not in logged_in_sessions:
                # chrome_options = Options()
                # chrome_options.add_argument("--disable-notifications")
                # chrome_options.add_argument('--ignore-certificate-errors')
                # chrome_options.add_argument('--ignore-ssl-errors')
                # driver = webdriver.Chrome(options=chrome_options)
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
                    chrome_options.add_argument("--disable-gpu") 
                    chrome_options.add_argument("--disable-software-rasterizer")
                    driver = webdriver.Chrome(options=chrome_options)
                    # print("ChromeDriver installed successfully.")
                login_facebook(driver, email, password)
                logged_in_sessions[email] = driver
                last_used_titles[email] = None
            else:
                driver = logged_in_sessions[email]

            count_products = len(product_ids)

            for i in range(count_products):
                driver.execute_script("window.open('https://web.facebook.com/marketplace/create/item');")
                driver.implicitly_wait(7)
            
            for index, product_id in enumerate(product_ids[:action_product]):
                product_details = get_product_details(product_id)
                post_product(driver, product_details, last_used_titles[email], random_price, time_speed, tab_index=index + 1)
                last_used_titles[email] = product_details[3]
        
    else:
        open_instances(additional_number, product_ids, last_used_titles, accounts, random_price, time_speed, action_product)

    time.sleep(10)
    for driver in logged_in_sessions.values():
        driver.quit()


if __name__ == "__main__":
   main()