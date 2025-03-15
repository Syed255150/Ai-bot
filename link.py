from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import tkinter as tk
from tkinter import messagebox

def scrape_linkedin_data(keyword):
    try:
        # Set up the Chrome browser options
        options = Options()
        options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"  # Replace with your Brave browser path

        # Path to chromedriver
        driver_path = 'C:/Users/abc/Desktop/linkedin bot/chromedriver-win64/chromedriver.exe'  # Replace with the path of chromedriver

        # Initialize the Service object with the chromedriver path
        service = Service(executable_path=driver_path)

        # Initialize the browser with Service and options
        driver = webdriver.Chrome(service=service, options=options)

        # Go to LinkedIn login page
        driver.get("https://www.linkedin.com/login")

        # Log in to LinkedIn (replace with your username and password)
        username = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password")
        username.send_keys("syedhassaan255@gmail.com")  # Replace with your email
        password.send_keys("Syed255@")  # Replace with your password
        password.send_keys(Keys.RETURN)

        # Wait for login to complete
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']")))

        # Search for the keyword
        search_box = driver.find_element(By.XPATH, "//input[@placeholder='Search']")
        search_box.send_keys(keyword)  # Use the keyword from the GUI
        search_box.send_keys(Keys.RETURN)

        # Wait for search results to load and click on People filter
        wait.until(EC.presence_of_element_located((By.XPATH, "//button[@aria-pressed='false'][normalize-space()='People']")))
        people_filter = driver.find_element(By.XPATH, "//button[@aria-pressed='false'][normalize-space()='People']")
        people_filter.click()

        # Scrape data from the search results
        data = []
        scroll_pause_time = 3  # Time to wait while scrolling

        # Scroll to load profiles
        previous_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            current_height = driver.execute_script("return document.body.scrollHeight")
            if current_height == previous_height:
                break
            previous_height = current_height

        # Extract profile data
        profiles = driver.find_elements(By.XPATH, "//span[contains(@class,'entity-result__title-text')]/a")
        for profile in profiles:
            try:
                # Extract profile link and navigate
                link = profile.get_attribute('href')
                driver.get(link)
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'pv-text-details__left-panel')]")))

                # Extract profile details
                try:
                    name = driver.find_element(By.XPATH, "//h1").text
                except:
                    name = "N/A"
                try:
                    headline = driver.find_element(By.XPATH, "//div[contains(@class,'text-body-medium')]" ).text
                except:
                    headline = "N/A"
                try:
                    location = driver.find_element(By.XPATH, "//span[contains(@class,'text-body-small')]" ).text
                except:
                    location = "N/A"

                # Append data to list
                data.append([name, headline, location])
                driver.back()
                time.sleep(2)
            except Exception as e:
                print(f"Error scraping profile: {e}")

        # Save data to CSV
        with open('linkedin_data.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Headline", "Location"])  # Column headers
            for row in data:
                writer.writerow(row)

        messagebox.showinfo("Success", "Data has been successfully scraped and saved to 'linkedin_data.csv'.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()

# GUI Functionality
def on_submit():
    keyword = search_entry.get()
    if keyword:
        scrape_linkedin_data(keyword)
    else:
        messagebox.showwarning("Input Error", "Please enter a keyword to search.")

# Create the main window
root = tk.Tk()
root.title("LinkedIn Scraper")
root.geometry("400x200")

# Add a heading
heading_label = tk.Label(root, text="LinkedIn Scraper", font=("Arial", 16), fg="blue")
heading_label.pack(pady=10)

# Add the search bar (entry widget)
search_entry = tk.Entry(root, font=("Arial", 14), width=30, bd=5, relief="solid")
search_entry.pack(pady=10)

# Add the submit button
submit_button = tk.Button(root, text="Submit", font=("Arial", 12), command=on_submit)
submit_button.pack(pady=10)

# Run the main loop
root.mainloop()
