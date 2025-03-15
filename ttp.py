import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

def scrape_coaching_data(keyword):
    # Configure the ChromeDriver path
    service = Service("chromedriver-win64/chromedriver.exe")  # Update the path if needed
    driver = webdriver.Chrome(service=service)
    
    # Open the target URL
    url = "https://coachingfederation.org/find-a-coach"
    driver.get(url)
    
    # Wait for the page to load completely
    wait = WebDriverWait(driver, 10)
    
    # Click "Accept" button for cookies
    try:
        accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[9]/div/div/div/a')))
        accept_button.click()
        print("Clicked on 'Accept' button.")
        time.sleep(2)
    except Exception as e:
        print(f"No 'Accept' button found or couldn't click it: {e}")

    # Accept cookies if the "I agree" button appears
    try:
        agree_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div[2]/a")))
        agree_button.click()
        time.sleep(2)
    except Exception as e:
        print("No 'I agree' button found or clicked.")
    
    # Perform search using the provided keyword
    try:
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="keywords"]')))
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)  # Wait for results to load
    except Exception as e:
        print(f"Error interacting with the search box: {e}")
        driver.quit()
        return

    # Initialize CSV file
    with open("coaching_data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Name", "Specialty", "Location", "Email", "Phone"])
        writer.writeheader()
        
        # Loop through all pages
        page_number = 1
        while True:
            print(f"Scraping page {page_number}...")
            
            # Scroll down the page to load more results
            scroll_pause_time = 2  # Seconds
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Scrape coach data
            try:
                # Locate all coach cards
                coach_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="cards"]/div')))  # XPath for all cards

                for index in range(len(coach_cards)):
                    try:
                        # Re-locate the cards before clicking, as the DOM may change
                        coach_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="cards"]/div')))
                        coach_card = coach_cards[index]

                        # Scroll into view and click the card
                        driver.execute_script("arguments[0].scrollIntoView();", coach_card)
                        coach_card.click()
                        time.sleep(3)  # Wait for the card details to load

                        # Scrape details
                        name = driver.find_element(By.XPATH, '/html/body/div[2]/form/div[3]/div[5]/table/tbody/tr/td/div[2]/div[2]/div[2]/div/h2').text
                        specialty = driver.find_element(By.XPATH, '/html/body/div[2]/form/div[3]/div[5]/table/tbody/tr/td/div[2]/div[2]/div[4]/div[1]/div/div[1]/a').text
                        location = driver.find_element(By.XPATH, '/html/body/div[2]/form/div[3]/div[5]/table/tbody/tr/td/div[2]/div[2]/div[4]/div[1]/div/div[4]/span').text
                        email = driver.find_element(By.XPATH, '/html/body/div[2]/form/div[3]/div[5]/table/tbody/tr/td/div[2]/div[2]/div[4]/div[1]/div/div[2]/a').text
                        phone = driver.find_element(By.XPATH, '/html/body/div[2]/form/div[3]/div[5]/table/tbody/tr/td/div[2]/div[2]/div[4]/div[1]/div/div[3]/span').text

                        # Append data to CSV
                        writer.writerow({
                            "Name": name,
                            "Specialty": specialty,
                            "Location": location,
                            "Email": email,
                            "Phone": phone,
                        })

                        # Go back to the main page
                        driver.back()
                        time.sleep(3)  # Wait for the page to reload
                    except Exception as e:
                        print(f"Error scraping card {index + 1}: {e}")
                        continue
            except Exception as e:
                print(f"Error locating coach cards on page {page_number}: {e}")

            # Check for the "Next" button and navigate to the next page
            try:
                next_button = driver.find_element(By.XPATH, '//*[@id="paging"]/div[1]/a[8]')  # Adjust XPath if necessary
                next_button.click()
                time.sleep(5)  # Wait for the next page to load
                page_number += 1
            except Exception as e:
                print("No more pages to scrape or error navigating to the next page.")
                break

    print("Scraping complete! Data saved to 'coaching_data.csv'.")
    driver.quit()

def on_submit():
    # Function to handle the submit button click
    entered_text = search_entry.get()
    print(f"You searched for: {entered_text}")
    scrape_coaching_data(entered_text)

# Create the main window
root = tk.Tk()
root.title("Search Bar")
root.geometry("300x200")  # Set the size of the window

# Add a heading
heading_label = tk.Label(root, text="Search Bar", font=("Arial", 16), fg="red")
heading_label.pack(pady=10)

# Add the search bar (entry widget)
search_entry = tk.Entry(root, font=("Arial", 14), width=20, bd=5, relief="solid")
search_entry.pack(pady=10)

# Add the submit button
submit_button = tk.Button(root, text="Submit", font=("Arial", 12), command=on_submit)
submit_button.pack(pady=10)

# Run the main loop
root.mainloop()
