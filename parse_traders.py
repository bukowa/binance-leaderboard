import json
import os.path
from dataclasses import dataclass
from pathlib import Path
from leaderboard.futures import TimeFilter, TypeFilter
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
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
url_leaderboard = "https://www.binance.com/en/futures-activity/leaderboard/futures"

# Driver
# Create a new ChromeOptions object
chrome_options = Options()

# Add any desired options to the ChromeOptions object
# chrome_options.add_argument("--headless")

print("driver")
# Create a new WebDriver using the ChromeOptions object
driver = webdriver.Remote(
    command_executor="http://127.0.0.1:4991", options=chrome_options
)

print("navigating")
driver.maximize_window()

# Navigate to the Google homepage
driver.get(url_leaderboard)
driver.execute_script(
    'localStorage.setItem("leaderboradTraderWagonBannerStatusKey", "hide")'
)
driver.get(url_leaderboard)

wait_for_button("next-page")
wait_for_button("onetrust-reject-all-handler")
driver.execute_script("document.getElementById('onetrust-reject-all-handler').click()")


def get_next_page_button():
    wait_for_button("next-page")
    return driver.find_element(By.ID, "next-page")


def is_last_page():
    wait_for_button("next-page")
    if get_next_page_button().get_attribute("disabled"):
        return True
    return False


def visit_page(number: int, _timeframe: TimeFilter, _typefilter: TypeFilter):
    """"""
    driver.get(url_leaderboard)
    _typefilter.click(driver)
    _timeframe.click(driver)
    wait_for_button("next-page")

    if number == 1:
        return
    click_times = number - 1
    clicked = 0
    while clicked != click_times:
        wait_for_button("next-page")
        # scroll to bottom
        actions = ActionChains(driver)
        actions.send_keys(Keys.PAGE_DOWN).perform()
        # remove ugly things
        driver.execute_script(
            """
            var elements = document.getElementsByClassName('css-1bbc1pg');
            if (elements.length > 0) {
                elements[0].remove();
            }
        """
        )
        # click next page
        driver.execute_script("document.getElementById('next-page').click()")
        clicked += 1
        wait_for_button("next-page")
        if is_last_page():
            break


@dataclass
class Trader:
    uuid: str
    typefilter: str


traders = []
for typefilter in TypeFilter.__members__.values():
    print(f"visiting {typefilter.value}")

    for timefilter in TimeFilter.__members__.values():
        print(f"visiting {' '.join([typefilter.value, timefilter.value])}")

        done = False
        current_page = 0

        while not done:
            current_page += 1
            visit_page(current_page, timefilter, typefilter)
            wait_for_button("next-page")
            data = driver.execute_script(
                "return document.querySelectorAll('.TraderCard');"
            )
            traders_count = len(data)

            for i in range(traders_count):
                print(f"visiting trader {i} on page {current_page}")

                x = data[i]
                driver.execute_script(
                    f"document.querySelectorAll('.TraderCard')[{i}].click()"
                )
                print(driver.current_url)
                uuid = driver.current_url.split("encryptedUid=")[1]
                traders.append(
                    Trader(
                        uuid=uuid,
                        typefilter=typefilter.value,
                    )
                )
                visit_page(current_page, timefilter, typefilter)
                wait_for_button("next-page")
                data = driver.execute_script(
                    "return document.querySelectorAll('.TraderCard');"
                )

            if is_last_page():
                done = True

# Close the browser
driver.quit()

# Read old traders
if os.path.isfile("traders.json"):
    with open("traders.json", "r") as f:
        old_traders = json.load(f)
else:
    old_traders = {}

# Update with new traders
output_traders = old_traders.copy()
for t in traders:
    output_traders[t.uuid] = t.typefilter

# Save all traders
with open("traders.json", "w") as f:
    json.dump(output_traders, f, indent="\t")
