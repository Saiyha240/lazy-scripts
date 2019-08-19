"""
Python/Selenium script to automate an auction event in a website.

Can run multiple instances at the same time for multiple items
Only bids when the auction time is near the end
Bid price protection
Needs editing for use with different websites

Requirements:
    Requires chromedriver to be used with Selenium

Parameters:
    --user The username of account
    --password The password of account for login
    --email The email of account for login
    --url The URL of the auction item
    --max-price The max price allowed for the script to bid
    --end-time The end time of the auction item
    --delay The delay before a page refresh is executed
    --headless Runs the browser in headless mode
    --real If set, bids for the item. If not, simulates bid only
"""
import argparse
import datetime
import json
import logging
import os
import re
import sys
import time
from argparse import Namespace

from dateutil.parser import parse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException, \
    NoAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL = ''
PASSWORD = ''
USER = ''

CRUNCH_TIME = 10


def handle_alert(browser, max_attempts=3):
    attempts = 0
    while attempts <= max_attempts:
        try:
            WebDriverWait(browser, 2).until(
                expected_conditions.alert_is_present()
            )

            alert = browser.switch_to.alert
            alert.accept()

            return True
        except NoAlertPresentException:
            pass
        except TimeoutException:
            return False

        attempts += 1

    return False


def wait(browser, xpath, delay=10, max_attempts=3):
    attempts = 0

    while attempts <= max_attempts:
        try:
            WebDriverWait(browser, delay).until(
                expected_conditions.presence_of_element_located((By.XPATH, xpath))
            )

            return True
        except StaleElementReferenceException:
            pass
        except TimeoutException:
            return False

        attempts += 1

    return False


def login(browser):
    xpath_login_input_email = "//input[@id='email']"
    # xpath_login_input_password = "//input[@id='passwd']"
    xpath_login_submit_credentials = "//input[@id='auth_button']"
    xpath_login_logout = "//input[@id='logout_button']"

    input_email = browser.find_element(By.XPATH, xpath_login_input_email)
    # input_pass = browser.find_element(By.XPATH, xpath_login_input_password)
    input_auth_button = browser.find_element(By.XPATH, xpath_login_submit_credentials)

    input_email.click()
    input_email.send_keys(EMAIL)

    browser.execute_script(f"document.getElementById('passwd').value='{PASSWORD}'")

    input_auth_button.click()

    return wait(browser, xpath_login_logout, 5)


def get_current_price(browser) -> int:
    pass


def get_price_bidder(browser) -> (int, str):
    xpath_table_name_price_node = "//*[@id='product_table']//tbody//tr[last()-1]//td[last()]"

    text = browser.find_element(By.XPATH, xpath_table_name_price_node).text
    text_match = re.match(r'^([0-9,]+)円\(最高入札者:(.+)\)', text)

    return int(text_match.group(1).replace(',', '')), text_match.group(2)


def place_bet(browser):
    xpath_login_submit_bid = "//input[@id='bid_button']"

    button_node = browser.find_element(By.XPATH, xpath_login_submit_bid)
    button_node.click()


def get_delay(time_left: int, default_delay: float = 10) -> float:
    if -15 < time_left <= CRUNCH_TIME:
        return 0
    else:
        return default_delay


def is_bid_by_time(end_time: datetime) -> (bool, int):
    now = datetime.datetime.now()
    time_left = int(end_time.timestamp() - now.timestamp())

    if -15 <= time_left <= CRUNCH_TIME:
        return True, time_left
    else:
        return False, time_left


def is_finished(browser) -> bool:
    xpath_table_name_price_node = "//*[@id='mes_end_bid']"

    try:
        browser.find_element(By.XPATH, xpath_table_name_price_node)

        return True
    except NoSuchElementException:
        return False


def run(args: Namespace):
    end_time = parse(args.end_time)
    chrome_options = Options()

    if args.headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--chrome-frame")
    chrome_options.add_argument("--window-size=1024,576")

    if os.name == 'nt':
        chrome_options.add_argument("--disable-gpu")

    browser = webdriver.Chrome(
        options=chrome_options,
        executable_path=os.path.abspath('chromedriver')
    )

    browser.get(args.url)

    login(browser)

    logger.info("Logged In!")

    while wait(browser, "//*[@id='product_title']"):
        price, bidder = get_price_bidder(browser)
        is_bid_time, time_left = is_bid_by_time(end_time)

        if is_finished(browser) or price > 8000:
            sys.exit()

        logger.info((price, bidder, bidder != USER, price < args.max_price, f'{time_left}s left'))

        if bidder != USER and price < args.max_price and is_bid_time:
            if args.real:
                logger.info("Betting!")
                place_bet(browser)

                if handle_alert(browser):
                    browser.refresh()
            else:
                logger.info("Fake Betting!")
        else:
            logger.info("Refreshing!")
            browser.refresh()

        time.sleep(get_delay(time_left, default_delay=args.delay))

    browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('--user', type=str, required=True, action='store', dest='user')

    parser.add_argument('--password', type=str, required=True, action='store', dest='password')

    parser.add_argument('--email', type=str, required=True, action='store', dest='email')

    parser.add_argument('-u', '--url', type=str, required=True, action='store', dest='url')

    parser.add_argument('-m', '--max-price', type=int, required=True, action='store', dest='max_price')

    parser.add_argument('-e', '--end-time', type=str, action='store', dest='end_time', default='2019-06-18T18:35:00')

    parser.add_argument('-d', '--delay', type=float, action='store', dest='delay', default=5)

    parser.add_argument('--headless', dest='headless', action='store_true')

    parser.add_argument('--real', dest='real', action='store_true')

    args = parser.parse_args()

    logger.info(json.dumps(vars(args), indent=4))

    EMAIL = args.email
    PASSWORD = args.password
    USER = args.user

    run(args)
