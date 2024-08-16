import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import time

def create_driver():
    # Set Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode if needed
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver using webdriver-manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Apply stealth settings to the driver
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

    return driver

def scrape_company_details(driver, urls, max_retries=3):
    results = []

    for url in urls:
        for attempt in range(max_retries):
            try:
                # Navigate to the URL
                driver.get(url)

                # Wait for the card element to load on the new page
                wait = WebDriverWait(driver, 30)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card")))

                # Extract the registration number from the page
                reg_number_header = driver.find_element(By.XPATH, "//h2[text()='Registration Number']")
                reg_number_value = reg_number_header.find_element(By.XPATH, "../p[@class='data']").text
                fullname_header = driver.find_element(By.XPATH, "//h2[text()='Full Name']")
                fullname_value = fullname_header.find_element(By.XPATH, "../p[@class='data']").text
                reg_date_header = driver.find_element(By.XPATH, "//h2[text()='Registration Date']")
                reg_date_value = reg_date_header.find_element(By.XPATH, "../p[@class='data']").text
                state_header = driver.find_element(By.XPATH, "//h2[text()='State']")
                state_value = state_header.find_element(By.XPATH, "../p[@class='data']").text
                reg_address_header = driver.find_element(By.XPATH, "//h2[text()='Registered Address']")
                reg_address_elements = reg_address_header.find_elements(By.XPATH, "../p[@class='data']")
                reg_address_values = [reg_address_element.text for reg_address_element in reg_address_elements]

                # Save the extracted data to the results list
                results.append({
                    "Registration Number": reg_number_value,
                    "Full Name": fullname_value,
                    "Registration Date": reg_date_value,
                    "State": state_value,
                    "Registered Address": reg_address_values
                })

                print({
                    "Registration Number": reg_number_value,
                    "Full Name": fullname_value,
                    "Registration Date": reg_date_value,
                    "State": state_value,
                    "Registered Address": reg_address_values
                })

                break  # Break out of the retry loop if successful

            except Exception as e:
                print(f"Error for URL {url} on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    print(f"Failed to get results for URL {url} after {max_retries} attempts.")
                time.sleep(5)  # Optional: wait a bit before retrying

    return results

if __name__ == "__main__":
    # Read the URLs from the CSV file
    df = pd.read_csv("company_links.csv")
    urls = df['Link'].tolist()

    # Initialize the WebDriver using webdriver-manager
    driver = create_driver()

    try:
        # Scrape company details
        results = scrape_company_details(driver, urls)

    finally:
        driver.quit()

    # Convert the results to a DataFrame and save to a new CSV file
    results_df = pd.DataFrame(results)
    results_df.to_csv("extracted_company_details.csv", index=False)
    print("Results saved to extracted_company_details.csv")
