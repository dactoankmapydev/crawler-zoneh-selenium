import sys
from time import sleep

from crawler.zone_h import connect_to_url, get_driver, parse_html


def run_process(page_number, browser):
    if connect_to_url(browser, page_number):
        sleep(2)
        html = browser.page_source
        parse_html(html)
    else:
        print("Error connecting to zone-h")


if __name__ == '__main__':
    # headless mode
    headless = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "headless":
            print("Running in headless mode")
            headless = True

    current_page = 1

    # init browser
    browser = get_driver(headless=headless)

    # crawler
    while current_page <= 50:
        print(f"Scraping page #{current_page}...")
        run_process(current_page, browser)
        current_page += 1

    # exit
    browser.quit()
