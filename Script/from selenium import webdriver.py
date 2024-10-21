from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_secret_text(url):
    # Setup Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--window-size=1920x1080")  # Set a specific window size
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # Set user-agent
    chrome_options.add_argument("--log-level=3")  # Suppress warnings and errors in logs
    chrome_options.add_argument("--disable-extensions")  # Disable extensions for more lightweight operation
    
    # Start the ChromeDriver in headless mode
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    
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