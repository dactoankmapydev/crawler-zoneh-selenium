- [building-a-concurrent-web-scraper-with-python-and-selenium](https://testdriven.io/blog/building-a-concurrent-web-scraper-with-python-and-selenium/)
- [concurrent-web-scraping](https://github.com/testdrivenio/concurrent-web-scraping)
- [cai-dat-moi-truong-selenium-voi-python](https://nguyenvanhieu.vn/cai-dat-moi-truong-selenium-voi-python/)

>>> from datetime import datetime, time
>>> import pytz
>>> ist = pytz.timezone("Asia/Ho_Chi_Minh")
>>> datetime.now(ist).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
'2021-01-20T19:02:21.369'
>>> datetime.now(ist).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"00:00"
'2021-01-20T19:06:02.71700:00'
>>> datetime.now(ist).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+00:00
  File "<stdin>", line 1
SyntaxError: illegal target for annotation
>>> datetime.now(ist).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"+00:00"
'2021-01-20T19:06:28.009+00:00'
