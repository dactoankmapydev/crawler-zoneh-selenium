from time import sleep

from crawler.zone_h import connect_to_url, get_driver, parse_html


def run_process(page_number, browser):
    if connect_to_url(browser, page_number):
        sleep(2)
        html = browser.page_source
        output = parse_html(html)
    else:
        print("Error connecting to zone-h")


if __name__ == '__main__':
    current_page = 1

    # init browser
    browser = get_driver()

    # crawler
    while current_page <= 30:
        print(f"Scraping page #{current_page}...")
        run_process(current_page, browser)
        current_page = current_page + 1

    # exit
    browser.quit()
