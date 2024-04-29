import scrapy


class DianpingSpider(scrapy.Spider):
    name = "dianping"
    allowed_domains = ["dianping.com"]
    start_urls = ["https://dianping.com"]

    def parse(self, response):
        pass
