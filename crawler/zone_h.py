import random
from time import sleep

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_driver():
    # proxies = [
    #    "127.0.0.1:3131",
    # ]
    # firefox_option = webdriver.FirefoxOptions()
    # firefox_option.add_argument("--proxy-server={}".format(random.choice(proxies)))
    # driver = webdriver.Firefox(firefox_options=firefox_option)
    driver = webdriver.Firefox()
    return driver


def connect_to_url(browser, page_number):
    base_url = "http://www.zone-h.org/archive/special={page_number}"
    connection_attempts = 0
    while connection_attempts < 3:
        try:
            browser.get(base_url)
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "ldeface"))
            )
            return True
        except Exception as e:
            print(e)
            print(f"Error connecting to {base_url}.")
            print(f"Attempt #{connection_attempts}.")
    return False


def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    for row in table.find_all("tr"):
        list_of_cells = []
        list_of_country = []
        for cell in row.find_all("td"):
            text = cell.text
            list_of_cells.append(text)
            for img in cell.find_all("img"):
                if img.get("title") is not None:
                    location = img["title"]
                    list_of_country.append(location)
        for country in list_of_country:
            date = list_of_cells[0]
            notifier = list_of_cells[1]
            domain = list_of_cells[8]
            os = list_of_cells[9]
            compromised = {
                "date": date,
                "notifier": notifier,
                "location": country,
                "domain": domain,
                "os": os,
            }
            print(compromised)

