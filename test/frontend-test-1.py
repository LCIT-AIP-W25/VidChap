import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Path to the audio file
AUDIO_FILE_PATH = os.path.join(os.getcwd(), "audio.mp3")

# Set up the WebDriver (Ensure chromedriver is in your PATH)
driver = webdriver.Chrome()



try:
    # Step 1: Open the index.html page of your frontend (make sure backend is running)
    driver.get('http://localhost:3000')  # Assuming the frontend is served here

    # Step 2: Find the input field and paste the YouTube link
    input_field = driver.find_element(By.ID, 'video-url')
    input_field.send_keys('https://youtu.be/IL2P1IB-2nc')

    # Step 3: Find the start button and click it
    start_button = driver.find_element(By.ID, 'start-download')
    start_button.click()

    # Step 4: Wait for the "Download complete!" message to appear
    notification = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'notification'))
    )

    # Step 5: Check if the download complete message is displayed
    message = notification.text
    assert message == 'Download complete!', f"Expected 'Download complete!', but got '{message}'"

    print('Download complete message appeared!')

finally:
    print("Check ther backend folder for saved audio file")
    # Close the browser window after the test
    driver.quit()
