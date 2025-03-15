import sys
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import random
from db_connection import get_connection
import logging

# Configure logging
logger = logging.getLogger('fb_ads_logger')
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(log_handler)

def get_group_accounts(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email, password FROM na_group_accounts WHERE na_group_id = ?", (group_id,))
    accounts = cursor.fetchall()
    conn.close()
    return accounts

def get_group_products(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id FROM na_group_products WHERE na_group_id = ?", (group_id,))
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
    except Exception as e:
        logger.error(f"An error occurred during login: {e}")

def post_product(driver, product_details, last_used_title=None,tab_index=0):
    product_name, image_folder_path, video_path, title, price, category, description, tags, location = product_details
    # Switch to the appropriate tab
    driver.switch_to.window(driver.window_handles[tab_index])
    try:
        # driver.get("https://web.facebook.com/marketplace/create/item")
         # Navigate to the posting page if it's not already open
        if "marketplace/create/item" not in driver.current_url:
            driver.get("https://web.facebook.com/marketplace/create/item")
            time.sleep(3)

        time.sleep(7)
        driver.implicitly_wait(10)

        try:
            limit_reached_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Limit reached')]")))
            if limit_reached_element.is_displayed():
                logger.info("You have reached the listing limit.")
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
        

        available_titles = title.split('\n')
        if len(available_titles) > 1 and last_used_title in available_titles:
            available_titles.remove(last_used_title)
        selected_title = random.choice(available_titles) if available_titles else last_used_title
        last_used_title = selected_title

        title_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//label[contains(@aria-label, 'Title')]//input[contains(@class, 'x1i10hfl')]")))
        title_input.click()
        title_input.send_keys(selected_title)

        time.sleep(2)

        price_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//label[contains(@aria-label, 'Price')]//input[contains(@class, 'x1i10hfl')]")))
        price_input.click()
        price_input.send_keys(str(price))

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

        time.sleep(2)
    
        condition_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//label[contains(@aria-label, 'Condition')]")))
        condition_input.click()

        time.sleep(2)

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

        time.sleep(3)

        description_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//label[contains(@aria-label, 'Description')]//following::textarea")))
        description_input.click()
        description_input.send_keys(description)

        time.sleep(2)

        tags_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//label[contains(@aria-label, 'Product tags')]//following::textarea")))
        for tag in tags.split(','):
            tags_input.send_keys(tag.strip())
            tags_input.send_keys(Keys.ENTER)

        time.sleep(2)

        location_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//label[contains(@aria-label, 'Location')]//following::input[@type='text']")))
        location_input.send_keys(Keys.CONTROL + "a")
        location_input.send_keys(Keys.DELETE)
        time.sleep(1)
        location_input.send_keys(location)
    
        time.sleep(2)
        location = location.strip()
        dropdown_option = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//span[contains(text(), '{location}')]")))
        dropdown_option.click()

        time.sleep(3)

        upload_img()

        time.sleep(7)

        try:
            publish_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Publish']")))
            publish_button.click()
        except:
            time.sleep(1)
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']/ancestor::div[@role='button']")))
            next_button.click()
            time.sleep(3)
            publish_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Publish']")))
            publish_button.click()

        time.sleep(12)
        
        logger.info("Product Post Successfully.")

    except Exception as e:
        logger.error(f"An error occurred while posting product: {e}")



def na_fb_ads_automate(group_id):
    # if len(sys.argv) != 2:
    #     logger.info("Usage: python na_fb_ads_automate.py <group_id>")
    #     sys.exit(1)
    logger.info("Starting automation...")
    # group_id = int(sys.argv[1])
    group_id = int(group_id)
    accounts = get_group_accounts(group_id)
    product_ids = get_group_products(group_id)
    logger.info(f"{accounts}")
    logger.info(f"{product_ids}")
    # Initialize a dictionary to store logged-in sessions and last used title for each account
    logged_in_sessions = {}
    last_used_titles = {}

    for account in accounts:
        email, password = account

        # Check if the account session is already logged in
        if email not in logged_in_sessions:
            chrome_options = Options()
            chrome_options.add_argument("--disable-notifications")
            driver = webdriver.Chrome(options=chrome_options)
            login_facebook(driver, email, password)
            logged_in_sessions[email] = driver
            last_used_titles[email] = None
        else:
            driver = logged_in_sessions[email]

        # Post each product for the logged-in account
        count_products = len(product_ids)

        # Open tabs for each product
        for i in range(count_products):
            driver.execute_script("window.open('https://web.facebook.com/marketplace/create/item');")
            # time.sleep(5)
            driver.implicitly_wait(7)

        for index,product_id in enumerate(product_ids):
            product_details = get_product_details(product_id)
            post_product(driver, product_details, last_used_titles[email], tab_index=index + 1) ### , tab_index=index + 1
            # Update the last used title for this account
            last_used_titles[email] = product_details[3]

    # Clean up: Close all WebDriver instances
    time.sleep(200)
    for driver in logged_in_sessions.values():
        driver.quit()

# if __name__ == "__main__":
   