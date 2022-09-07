import os
import urllib.request

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time

# Loads the env variables
load_dotenv()


def login():
    """
    Performs login with email and password
    """
    element = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.LINK_TEXT, 'Sign in'))
    )

    element.click()

    email_input = driver.find_element(By.ID, "auth-id-input")
    email_input.send_keys(os.getenv('EMAIL'))
    # Return == Enter
    email_input.send_keys(Keys.RETURN)

    # Sleep for few seconds if you are prompted with verification
    # time.sleep(10)

    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(os.getenv('PASSWORD'))
    # Return == Enter
    password_input.send_keys(Keys.RETURN)


def get_and_sanitize_video_title():
    """
    Gets the video title from the html and removes any dangerous characters.
    """
    not_allowed_chars = ['?', ',', '.', ':', '!']
    heading = driver.find_element(By.CSS_SELECTOR, 'h2.clamp-1').text

    for char in not_allowed_chars:
        heading = heading.replace(char, '')

    # Transform the string into a file name and returns it
    final_title = f"{heading}.mp4"
    return final_title


def get_video_src():
    """
    Gets the video src and the video location and returns them.
    """
    video = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.TAG_NAME, "video"))
    )
    source = video.get_attribute("src")
    return source, video


if __name__ == '__main__':

    # Browser setup
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get(os.getenv('URL'))

    try:
        login()
        # Sleep for few seconds if you are prompted with verification
        # time.sleep(10)
        while True:

            time.sleep(2)
            title = get_and_sanitize_video_title()
            # If there is a heading with Quiz inside, it waits for the next video to load and start all over
            if 'Quiz' in title:
                time.sleep(15)
                continue

            src, video_location = get_video_src()

            # Saved the video with the title provided in the project
            urllib.request.urlretrieve(src, title)

            # We click on the video so the next button becomes visible for selenium
            video_location.click()

            next_btn = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.XPATH, "//button[@title='Next']"))
            )
            if next_btn.is_enabled():
                next_btn.click()
                time.sleep(2)
            else:
                driver.quit()
                break

    except Exception as e:
        print(e)
        driver.quit()
