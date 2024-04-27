import logging
import re
import scrapy


class DianpingSpider(scrapy.Spider):
    name = "dianping"
    allowed_domains = ["dianping.com"]
    custom_settings = {
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8, #单个域执行的并发（即同时）请求的最大数量
        'DOWNLOAD_DELAY': 8
    }

    url = 'https://www.dianping.com/search/keyword/8/0_%E5%85%BB%E5%8F%91'
    shop_count = 0
    page = 0

    cookies = {
        'cy': '1609',
        'cityid': '1609',
        'cye': 'shuangliu',
        '_lxsdk_cuid': '18f1f9f58ddc8-0a972e5335acbe-26001d51-e1000-18f1f9f58ddc8',
        '_lxsdk': '18f1f9f58ddc8-0a972e5335acbe-26001d51-e1000-18f1f9f58ddc8',
        '_hc.v': '62092e6b-b4d4-b617-cdb6-afe1f1232e06.1714222489',
        'WEBDFPID': '1z46895822975u20y66y44411uy900uu81u8u0u4x2797958277zv8vz-2029582488967-1714222488240CYGAKMKfd79fef3d01d5e9aadc18ccd4d0c95071658',
        'qruuid': 'fcb56190-515e-4d52-9d93-c256ff238826',
        'dper': '0202942235044afb6dda647cbee1d7a313d30c6e858749da7fc936b6168f404e2dd96393972892732c6d9456592158a304bce752d7c83dcbda8500000000a71f00001553da06b86472ba959892a16f7bdc3044b9ce645f7841e0269bdef87e1f16e9dd4905cb64c0ebae891465e4b0172c05',
        'll': '7fd06e815b796be3df069dec7836c3df',
        '_lxsdk_s': '18f1f9f58de-093-128-eec%7C%7C8',
        'Hm_lvt_602b80cf8079ae6591966cc70a3940e7': '1714222525',
        'Hm_lpvt_602b80cf8079ae6591966cc70a3940e7': '1714222525',
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
        self.page += 1
        logging.info(f"Start request page {self.page}: {self.url}")
        yield scrapy.Request(url=self.url,
                             callback=self.request_shop_url,
                             headers=self.headers,
                             cookies=self.cookies,
                             )

    def request_shop_url(self, response):
        elements = response.xpath('''//a[@onclick="LXAnalytics('moduleClick', 'shoppic')"]''')

        cookies = {
            'cy': '1609',
            'cityid': '1609',
            'cye': 'shuangliu',
            '_lxsdk_cuid': '18f1f9f58ddc8-0a972e5335acbe-26001d51-e1000-18f1f9f58ddc8',
            '_lxsdk': '18f1f9f58ddc8-0a972e5335acbe-26001d51-e1000-18f1f9f58ddc8',
            '_hc.v': '62092e6b-b4d4-b617-cdb6-afe1f1232e06.1714222489',
            'WEBDFPID': '1z46895822975u20y66y44411uy900uu81u8u0u4x2797958277zv8vz-2029582488967-1714222488240CYGAKMKfd79fef3d01d5e9aadc18ccd4d0c95071658',
            'qruuid': 'fcb56190-515e-4d52-9d93-c256ff238826',
            'dper': '0202942235044afb6dda647cbee1d7a313d30c6e858749da7fc936b6168f404e2dd96393972892732c6d9456592158a304bce752d7c83dcbda8500000000a71f00001553da06b86472ba959892a16f7bdc3044b9ce645f7841e0269bdef87e1f16e9dd4905cb64c0ebae891465e4b0172c05',
            'll': '7fd06e815b796be3df069dec7836c3df',
            '_lxsdk_s': '18f1f9f58de-093-128-eec%7C%7C8',
            'Hm_lvt_602b80cf8079ae6591966cc70a3940e7': '1714222525',
            'Hm_lpvt_602b80cf8079ae6591966cc70a3940e7': '1714222525',
        }

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            # 'Cookie': 'cy=8; cityid=8; cye=chengdu; fspop=test; s_ViewType=10; _lxsdk_cuid=18f1f0cdbdbc8-08a88c584bcd69-26001d51-e1000-18f1f0cdbdbc8; _lxsdk=18f1f0cdbdbc8-08a88c584bcd69-26001d51-e1000-18f1f0cdbdbc8; _hc.v=11cdc63f-9e20-b3dd-fc29-c9b658ae900c.1714212888; WEBDFPID=x4188xwx14465286z8uzw3zv1x77776y81u8u9xvw57979587x35961u-2029572892448-1714212892448GSWQUKKfd79fef3d01d5e9aadc18ccd4d0c95071513; dper=0202aa205d885bf541dbcd1b6417b264b3a67c3e3afaf6aac0905d06c1ee886a499c04ebbac179e2d04a7c431738095654a28f0d276cc23b417500000000a71f00005053f5dfa3a89a848bc433b0059b894f5101fcdf280647232c98f0ee2ffabbb2058e79845e9dd42e38c9a4f99e0dbd0f; qruuid=5888d555-0010-42aa-9692-38f9bf0c0bb2; cy=8; cye=chengdu; ll=7fd06e815b796be3df069dec7836c3df; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1714215520; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1714215548; _lxsdk_s=18f1f350358-350-dc-ce0%7C%7C27',
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

        if elements:
            for element in elements:
                self.shop_count += 1
                href = element.xpath('@href').get()

                yield scrapy.Request(url=href,
                                     callback=self.detail_parse,
                                     headers=headers,
                                     cookies=cookies,
                                     )

        next_page = response.xpath('//a[@class="next"]')
        if next_page:
            self.page += 1

            url = response.xpath('//a[@class="next"]/@href').get().strip()
            logging.info(f"Start request page {self.page}: {url}")
            yield scrapy.Request(url=url,
                                 callback=self.request_shop_url,
                                 headers=self.headers,
                                 cookies=self.cookies,
                                 )

    def detail_parse(self, response):

        shop_name = response.xpath('//*[@id="basic-info"]/h1/text()').get().strip()
        city = response.xpath('//*[@id="top-nav"]/div/div[1]/a/span[2]/text()').get().strip()

        address = ""
        elements = response.xpath('//div[@class="expand-info address"]//*')
        for addr in elements:
            address = address + addr.xpath('text()').get().strip()

        phone = ""
        p_list = response.xpath('//p[@class="expand-info tel"]//*')
        for e in p_list:
            if phone:
                phone = phone + ' ' + e.xpath('text()').get().strip()
            else:
                phone = e.xpath('text()').get().strip()

        business_hours = response.xpath('//*[@id="basic-info"]/div[3]/p[1]/span[2]/text()').get().strip()
        business_hours = re.sub(r'\r|\n', ' ', business_hours)

        overall_rating = response.xpath('//*[@id="basic-info"]/div[1]/span[1]/@class').get().strip()
        # "mid-rank-stars mid-str45"
        m = re.match(r'^mid-rank-stars mid-str(\d+)$', overall_rating)
        if m:
            overall_rating = str(m.group(1))

        per_capita_consumption = response.xpath('//*[@id="basic-info"]/div[1]/span[3]/text()').get().strip()
        number_of_comments = response.xpath('//*[@id="basic-info"]/div[1]/span[2]/text()').get().strip()

        if response.xpath('//*[@id="comment"]/h2/span/a[4]/span/text()'):
            number_of_bad_comments = response.xpath('//*[@id="comment"]/h2/span/a[4]/span/text()').get().strip()
        else:
            number_of_bad_comments = " "

        logging.info(shop_name)
        logging.info(city)
        logging.info(address)
        logging.info(phone)
        logging.info(business_hours)
        logging.info(overall_rating)
        logging.info(per_capita_consumption)
        logging.info(number_of_comments)
        logging.info(number_of_bad_comments)
