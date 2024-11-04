# %%
##!hostname -I
##!cat /opt/mirthconnect/logs/mirth.log

# %%
#!pip install python-dotenv --upgrade
#!pip install requests --upgrade
#!pip install lxml --upgrade
#!pip install mirthpy --upgrade
#!pip install pandas --upgrade
#!pip install selenium --upgrade
#!pip install webdriver_manager --upgrade

# %%
import time
start_time = time.time()

from datetime import datetime

import subprocess
import requests
import os
import shutil
from dotenv import load_dotenv
import lxml.etree as ET
import pandas as pd
import re
import sys

import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress the warning
warnings.simplefilter('ignore', InsecureRequestWarning)

load_dotenv()

# %%
def print_step(step_description):
    # Get the current time and format it
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print a separator and the step description in a formatted way
    print("\n" + "-" * 70)
    print(f"{' ' * 10}{step_description} - {current_time}")
    print("-" * 70 + "\n")

# %% [markdown]
# # Response file: set the ports + the license key
# 
# ![image-3.png](attachment:image-3.png) ![image-2.png](attachment:image-2.png)

# %% [markdown]
# ### Get Mirth https/https ports from .env file
# ![image-2.png](attachment:image-2.png)

# %%
print_step("Prepare response file: Ports / License key")

HttpPort = os.getenv("http.port")
HttpSport = os.getenv("https.port")
key = os.getenv("INSTALL_KEY_URL")
databaseUrl = os.getenv("databaseUrl")
databaseType = os.getenv("database")

# %% [markdown]
# ## Using Access Hosting Encrypting portal for Mirth authentication + sharing the License Key

# %% [markdown]
# ### Function to extract encrupted content from: https://ssshh.accesshosting.co.uk/
# ![image-3.png](attachment:image-3.png)
# 

# %%
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def extract_secret_text(url):
    # Setup Edge options for headless mode
    edge_options = Options()
    edge_options.add_argument("--headless")  # Run in headless mode
    edge_options.add_argument("--no-sandbox")  # Overcome limited resource problems
    edge_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    edge_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    edge_options.add_argument("--window-size=1920x1080")  # Set a specific window size
    edge_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # Set user-agent
    edge_options.add_argument("--log-level=3")  # Suppress warnings and errors in logs
    edge_options.add_argument("--disable-extensions")  # Disable extensions for more lightweight operation

    # Start the EdgeDriver in headless mode using EdgeChromiumDriverManager
    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=edge_options)
    
    # Optional: Set implicit wait
    driver.implicitly_wait(10)

    try:
        # Open the URL
        driver.get(url)

        # Wait for the loading message to disappear (prefer WebDriverWait over time.sleep)
        loading_message_xpath = "//h4[contains(text(), 'Fetching from database')]"
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((By.XPATH, loading_message_xpath))
        )

        # After loading is complete, wait for the specific content to appear
        content_xpath = "//p[@data-test-id='preformatted-text-secret']"  # XPath for the desired element
        secret_text_element = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, content_xpath))
        )

        # Extract the text from the specified element
        secret_text = secret_text_element.text

        return secret_text

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        # Close the browser
        driver.quit()




print_step("Extract Mirth credentials from ssshh.accesshosting.co.uk")
credentialsUrl = os.getenv("MIRTH_CREDENTIALS_URL")

extracted_credentials = extract_secret_text(credentialsUrl)
if extracted_credentials:
    print("Credentials extracted:", extracted_credentials)
else:
    print("Failed to extract the credentials.")

# Splitting the string using '///' as the separator
username = extracted_credentials.split("///")[0]
password = extracted_credentials.split("///")[1]
del credentialsUrl
del extracted_credentials
username, password



mirth_host = "https://localhost"
mirth_url = mirth_host + ":" + HttpSport

# Function to get the API session token
def get_session_token(username, password, retries=5, delay=10):
    url = f"{mirth_url}/api/users/_login"
    print(f"Attempting to log in at: {url}")
    payload = "username=" + username + "&password=" + password
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest"
    }


    response = None  # Initialize response to None to avoid UnboundLocalError

    # Try to log in up to 'retries' times based on exceptions
    for attempt in range(1, retries + 1):
        try:
            print("We are going to try: ")
            print("payload: " + payload)
            response = requests.post(url, headers=headers, data=payload, verify=False)  # SSL verification disabled
            print("response.status_code: " + str(response.status_code))
            # If request succeeds without raising an exception, return session token
            if response.status_code in [200, 204]:
                print(f"Login successful on attempt {attempt}.")
                return response.cookies["JSESSIONID"]
            else:
                print(f"Failed to log in (HTTP error) on attempt {attempt}: {response.status_code}")

        except requests.exceptions.RequestException as e:  # Catch network-related errors
            if response is not None:
                print(f"Error occurred on attempt {attempt} with HTTP status code {response.status_code}: {e}")
            else:
                print(f"Error occurred on attempt {attempt}: {e}")

        if attempt < retries:
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)  # Wait for 'delay' seconds before retrying

    print("All login attempts failed.")
    return None


# Use the function with retry logic
session_token = get_session_token(username, password)

# Optionally clean up sensitive data from memory
# del username
# del password

session_token  # The result will be None if all attempts fail, or the session token if successful
