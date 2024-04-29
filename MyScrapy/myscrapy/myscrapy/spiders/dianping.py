import logging

import scrapy


class DianpingSpider(scrapy.Spider):
    name = "dianping"
    allowed_domains = ["dianping.com"]
    url = 'https://www.dianping.com/search/keyword/8/0_%E5%85%BB%E5%8F%91'
    page = 1

    cookies = {
        'cy': '4425',
        'cityid': '4425',
        'cye': 'wenjiang',
        '_lx_utm': 'utm_source%3Dgoogle%26utm_medium%3Dorganic',
        '_lxsdk_cuid': '18f1fb39ca3c8-05248e537f3c7e-26001d51-e1000-18f1fb39ca3c8',
        '_lxsdk': '18f1fb39ca3c8-05248e537f3c7e-26001d51-e1000-18f1fb39ca3c8',
        '_hc.v': '87813fef-1954-53c3-bf25-7b1e3435919a.1714223816',
        'WEBDFPID': '603u034xvwzv5860y3633y045y336y9981u8uy6y086979587z423100-2029583823647-1714223808079MYIQAOOfd79fef3d01d5e9aadc18ccd4d0c95079233',
        's_ViewType': '10',
        'qruuid': '0128a1d6-8ad0-451a-b305-6d8c6e88fbf6',
        'dper': '0202c1257774cd68add73886b49502879710941a95671a8efedeac0e536fbe37a0a022affe54a22ace3c5bd1c13b475fe265d808bf4cd9f465dd00000000a71f0000503fa972a1553e5651b033fde0cd7f0de2d473782ed1ccabad9ddcb6e6c3a79ae973cf88f0385f10347424d02b33f95d',
        'll': '7fd06e815b796be3df069dec7836c3df',
        'Hm_lvt_602b80cf8079ae6591966cc70a3940e7': '1714224512',
        'Hm_lpvt_602b80cf8079ae6591966cc70a3940e7': '1714224517',
        '_lxsdk_s': '18f1fb39ca4-5f7-a12-590%7C%7C73',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie': 'fspop=test; s_ViewType=10; _lxsdk_cuid=18f1f0cdbdbc8-08a88c584bcd69-26001d51-e1000-18f1f0cdbdbc8; _lxsdk=18f1f0cdbdbc8-08a88c584bcd69-26001d51-e1000-18f1f0cdbdbc8; _hc.v=11cdc63f-9e20-b3dd-fc29-c9b658ae900c.1714212888; WEBDFPID=x4188xwx14465286z8uzw3zv1x77776y81u8u9xvw57979587x35961u-2029572892448-1714212892448GSWQUKKfd79fef3d01d5e9aadc18ccd4d0c95071513; dper=0202aa205d885bf541dbcd1b6417b264b3a67c3e3afaf6aac0905d06c1ee886a499c04ebbac179e2d04a7c431738095654a28f0d276cc23b417500000000a71f00005053f5dfa3a89a848bc433b0059b894f5101fcdf280647232c98f0ee2ffabbb2058e79845e9dd42e38c9a4f99e0dbd0f; qruuid=5888d555-0010-42aa-9692-38f9bf0c0bb2; ll=7fd06e815b796be3df069dec7836c3df; cy=8; cye=chengdu; _lxsdk_s=18f1f0cdbdc-8ce-0d8-e72%7C%7C11',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    def start_requests(self):

        logging.info(f"Start request page {self.page}: {self.url}")
        yield scrapy.Request(url=self.url,
                             callback=self.parse,
                             headers=self.headers,
                             cookies=self.cookies,
                             )

    def parse(self, response, **kwargs):
        logging.info('111111111111111111')
        logging.info(response.text)
