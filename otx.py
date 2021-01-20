import math
from datetime import datetime

import threading
import pytz

from helper import network, setup_es, rbmq

OTX_API_KEY = "779cc51038ddb07c5f6abe0832fed858a6039b9e8cdb167d3191938c1391dbba"

headers = {
    "X-OTX-API-KEY": OTX_API_KEY
}


def get_total_page_otx():
    results = network.requests_retry_session().get("https://otx.alienvault.com/api/v1/pulses/subscribed",
                                                   headers=headers, timeout=60).json()
    total_page = math.ceil(results["count"] / 50)
    return total_page


def crawler_otx(start_page, end_page):
    es = setup_es.connect_elasticsearch()
    connection, channel = rbmq.connect("ioc_queue")
    ist = pytz.timezone("Asia/Ho_Chi_Minh")
    # total_page = get_total_page_otx()
    sample = {"sample": ["FileHash-MD5", "FileHash-PEHASH", "FileHash-SHA256", "FileHash-IMPHASH", "FileHash-MD5"]}
    url = {"url": ["URL", "URI"]}
    domain = {"domain": ["hostname", "domain"]}
    ipaddress = {"ipaddress": ["IPv6", "IPv4", "BitcoinAddress"]}

    for page in range(start_page, end_page):
        data = network.requests_retry_session().get(
            "https://otx.alienvault.com/api/v1/pulses/subscribed?limit=50&page={}".format(page),
            headers=headers, timeout=60).json()
        for item in data["results"]:
            pulse_id = item["id"]
            name = item["name"]
            description = item["description"]
            author_name = item["author_name"]
            modified = item["modified"]
            created = item["created"]
            category = item["tags"]
            targeted_countries = item["targeted_countries"]
            industries = item["industries"]
            malware_families = item["malware_families"]
            attack_ids = item["attack_ids"]
            references = item["references"]

            post = {
                "pulse_id": pulse_id,
                "name": name,
                "description": description,
                "author_name": author_name,
                "modified": modified,
                "created": created,
                "targeted_countries": targeted_countries,
                "industries": industries,
                "malware_families": malware_families,
                "attack_ids": attack_ids,
                "references": references,
                "category": category
            }
            if es is not None:
                if setup_es.create_index_post(es, "post"):
                    setup_es.store_record(es, "post", pulse_id, post)

            for value in item["indicators"]:
                ioc_id = value["id"]
                ioc = value["indicator"]
                created_time = value["created"]
                ioc_type = value["type"]

                if ioc_type in sample["sample"]:
                    ioc_type = "sample"
                if ioc_type in url["url"]:
                    ioc_type = "url"
                if ioc_type in domain["domain"]:
                    ioc_type = "domain"
                if ioc_type in ipaddress["ipaddress"]:
                    ioc_type = "ipaddress"

                indicator = {
                    "ioc_id": ioc_id,
                    "ioc": ioc,
                    "ioc_type": ioc_type,
                    "created_time": created_time,
                    "crawled_time": datetime.now(ist).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                    "source": "otx",
                    "category": category
                }
                rbmq.send(channel, indicator, "ioc_queue")
                if es is not None:
                    if setup_es.create_index_ioc(es, "ioc"):
                        setup_es.store_record(es, "ioc", ioc_id, indicator)
    connection.close()


if __name__ == '__main__':
    threads = []
    for i in range(0, get_total_page_otx(), 3):
        start_page = i
        end_page = start_page + 2
        if start_page == 0:
            start_page = 1
            if end_page >= get_total_page_otx():
                end_page = get_total_page_otx()
        thread = threading.Thread(target=crawler_otx, args=(start_page, end_page + 1))
        threads.append(thread)
        thread.start()
