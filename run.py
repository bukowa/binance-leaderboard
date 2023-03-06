import time
from dataclasses import dataclass
from pathlib import Path

import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait

PWD = Path(__file__).resolve().parent

def wait_for_button(id_):
    try:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, id_))
        )
    except:
        raise Exception("button not found")


# Leaderboard
url_leaderboard = 'https://www.binance.com/en/futures-activity/leaderboard/futures'

# Driver
# Create a new ChromeOptions object
chrome_options = Options()

# Add any desired options to the ChromeOptions object
# chrome_options.add_argument("--headless")

print("driver")
# Create a new WebDriver using the ChromeOptions object
driver = webdriver.Remote(
    command_executor="http://127.0.0.1:4991",
    options=chrome_options
)

print("navigating")
driver.maximize_window()

# Navigate to the Google homepage
driver.get(url_leaderboard)
driver.execute_script('localStorage.setItem("leaderboradTraderWagonBannerStatusKey", "hide")')
driver.get(url_leaderboard)

wait_for_button("next-page")
wait_for_button("onetrust-reject-all-handler")
# button = driver.find_element(By.ID, 'onetrust-reject-all-handler')
# button.click()
driver.execute_script("document.getElementById('onetrust-reject-all-handler').click()")
def get_next_page_button():
    wait_for_button('next-page')
    return driver.find_element(By.ID, 'next-page')

def is_last_page():
    wait_for_button('next-page')
    if get_next_page_button().get_attribute('disabled'):
        return True
    return False


def visit_page(number: int):
    driver.get(url_leaderboard)
    wait_for_button('next-page')
    if number == 1:
        return
    click_times = number - 1
    clicked = 0
    while clicked != click_times:
        wait_for_button('next-page')
        # scroll to bottom
        actions = ActionChains(driver)
        actions.send_keys(Keys.PAGE_DOWN).perform()
        # remove ugly things
        driver.execute_script('''
            var elements = document.getElementsByClassName('css-1bbc1pg');
            if (elements.length > 0) {
                elements[0].remove();
            }
        ''')
        # click next page
        driver.execute_script("document.getElementById('next-page').click()")
        clicked += 1
        wait_for_button('next-page')
        if is_last_page():
            break


@dataclass
class Trader:
    text: str
    uuid: str

traders = []
done = False
current_page = 0

while not done:
    current_page += 1
    visit_page(current_page)
    wait_for_button('next-page')
    data = driver.execute_script("return document.querySelectorAll('.TraderCard');")
    traders_count = len(data)

    for i in range(traders_count):
        x = data[i]
        text = x.text
        driver.execute_script(f"document.querySelectorAll('.TraderCard')[{i}].click()")
        print(driver.current_url)
        uuid = driver.current_url.split('encryptedUid=')[1]
        traders.append(
            Trader(
                text=text,
                uuid=uuid,
            )
        )
        visit_page(current_page)
        wait_for_button('next-page')
        data = driver.execute_script("return document.querySelectorAll('.TraderCard');")

    if is_last_page():
        done = True

print(traders)
# Close the browser
driver.quit()

import json

out = {}
for t in traders:
    out[t.uuid] = t.text

with open('traders.json', 'w') as f:
    json.dump(out, f, indent='\t')

