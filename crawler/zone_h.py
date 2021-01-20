import datetime
import hashlib
import random
from helper import network, setup_es, rbmq
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_driver(headless):
    proxies = [
        "127.0.0.1:3130",
    ]
    options = webdriver.ChromeOptions()
    options.add_argument("--proxy-server={}".format(random.choice(proxies)))
    if headless:
        options.add_argument("--headless")

    # initialize driver
    driver = webdriver.Chrome(
        executable_path="C:\\Users\\toannd_vcs\\PycharmProjects\\crawler-zoneh\\driver\\chromedriver.exe",
        chrome_options=options)
    return driver


def connect_to_url(browser, page_number):
    base_url = f"http://www.zone-h.org/archive/special=1/page={page_number}"
    connection_attempts = 0
    while connection_attempts < 5:
        try:
            browser.get(base_url)
            WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.ID, "ldeface"))
            )
            return True
        except Exception as e:
            print(e)
            connection_attempts += 1
            print(f"Error connecting to {base_url}.")
            print(f"Attempt #{connection_attempts}.")
    return False


def parse_html(html):
    es = setup_es.connect_elasticsearch()
    connection, channel = rbmq.connect("zone_h_queue")
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
            date_time_str = list_of_cells[0].replace("/", " ")
            date_time_obj = datetime.datetime.strptime(date_time_str, "%Y %m %d")
            creation_date = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S")
            notifier = list_of_cells[1]
            domain = list_of_cells[8]
            os = list_of_cells[9]
            id_hash = hashlib.sha1(
                "{}-{}-{}".format(notifier, domain, os).encode("utf-8")).hexdigest()
            compromised = {
                "date": creation_date,
                "notifier": notifier,
                "location": country,
                "domain": domain,
                "os": os,
                "hash": id_hash,
            }
            print(compromised)
            rbmq.send(channel, compromised, "zone_h_queue")
            if es is not None:
                if setup_es.create_index_zone(es, "ti-zone_h"):
                    setup_es.store_record(es, "ti-zone_h", id_hash, compromised)
    connection.close()
