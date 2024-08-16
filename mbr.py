import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode if needed
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the WebDriver using webdriver-manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # Navigate to the given URL
    url = "https://register.mbr.mt/app/query/search_for_company"
    driver.get(url)

    # Wait for the input field to be available
    wait = WebDriverWait(driver, 30)
    input_field = wait.until(EC.presence_of_element_located((By.ID, "ef1ha9-companyId")))

    # Loop through the specified range of company IDs
    for company_id in range(107614, 108986):  # Adjust range for testing
        company_id_str = f"C {company_id}"
        input_field.clear()
        input_field.send_keys(company_id_str)
        
        # Wait for the search button to be clickable and click it
        search_button = wait.until(EC.element_to_be_clickable((By.NAME, "data[search]")))
        search_button.click()
        
        # Wait for the results to be visible
        wait.until(EC.presence_of_element_located((By.ID, "query_results")))
        
        # Optionally wait for results to load (adjust the time as needed)
        time.sleep(5)  # Sleep to ensure the page loads results before proceeding

        try:
            # Find the first td element within the query_results div and click the link
            result_link = driver.find_element(By.CSS_SELECTOR, "#query_results td a")
            result_link.click()
            
            # Wait for the card element to load on the new page
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
            
            # Save the company details to the results list
            result = {
                "company_id": company_id_str, 
                "Registration Number": reg_number_value, 
                "Full Name": fullname_value, 
                "Registration Date": reg_date_value, 
                "State": state_value, 
                "Registered Address": reg_address_values
            }
            
            # Open the CSV file for writing
            with open("company_results.csv", mode="a", newline='', encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=["company_id", "Registration Number", "Full Name", "Registration Date", "State", "Registered Address"])
                
                # Write the header if the file is empty
                if file.tell() == 0:
                    writer.writeheader()
                
                # Write the result to the CSV file
                writer.writerow(result)
            
            # Print the result
            print(result)
            
            # Navigate back to the search page
            time.sleep(5)
            driver.back()
            time.sleep(5)
            
            # Reinitialize the input field and search button
            input_field = wait.until(EC.presence_of_element_located((By.ID, "ef1ha9-companyId")))
            search_button = wait.until(EC.element_to_be_clickable((By.NAME, "data[search]")))

        except Exception as e:
            print(f"No results for company ID {company_id_str}: {e}")

finally:
    # Close the WebDriver
    driver.quit()

print("Scraping completed. Results saved to company_results.csv")
