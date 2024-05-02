import scrapy
import logging
from urllib.parse import urlparse
from myscrapy.items import EquipmentradarItem


def get_request_data(page_id):
    data = {
        'action': 'show_more',
        'view': 'directory',
        'id': f'{page_id}',
        'pvuuid': '171461080727355300',
        'muuid': '',
    }
    return data


class EquipmentradarSpider(scrapy.Spider):
    name = "equipmentradar"
    allowed_domains = ["equipmentradar.com"]

    custom_settings = {
        'ITEM_PIPELINES': {'myscrapy.pipelines.EquipmentradarPipeline': 300},
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,  # 单个域执行的并发（即同时）请求的最大数量
        # 'DOWNLOAD_DELAY': 8
    }

    url = "https://www.equipmentradar.com/en/directory"
    cookies = {
        'sd': '9583186',
        't': 'CpwIBsFInHuLlr7DudmxDWPmsr65ANdO',
        'ls': '{%22cd%22:null%2C%22jsc%22:null}',
    }

    headers = {
        # 'accept': 'application/json, text/javascript, */*; q=0.01',
        # 'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
        # 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # # 'cookie': 'sd=9583186; t=CpwIBsFInHuLlr7DudmxDWPmsr65ANdO; ls={%22cd%22:null%2C%22jsc%22:null}',
        # 'origin': 'https://www.equipmentradar.com',
        # 'priority': 'u=1, i',
        'referer': 'https://www.equipmentradar.com/en/directory',
        # 'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
        # 'sec-fetch-dest': 'empty',
        # 'sec-fetch-mode': 'cors',
        # 'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'x-csrftoken': 'bxNBsJ5lWgsdCdyo4KEHo6LWalymCs6pDM99T1AT9NMONuvRoNQ4RSq8sCuh2593',
        'x-requested-with': 'XMLHttpRequest',
    }

    def start_requests(self):
        # request first page
        yield scrapy.http.JsonRequest(url=self.url,
                                      callback=self.parse_main_page,
                                      headers=self.headers,
                                      cookies=self.cookies,
                                      )

    def parse_main_page(self, response, **kwargs):

        dealers = response.xpath('//*[@id="search-container"]/div')

        cookies = {
            'sd': '9583186',
            't': 'CpwIBsFInHuLlr7DudmxDWPmsr65ANdO',
            'ls': '{%22cd%22:null%2C%22jsc%22:null}',
        }

        headers = {
            # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            # 'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
            # # 'cookie': 'sd=9583186; t=CpwIBsFInHuLlr7DudmxDWPmsr65ANdO; ls={%22cd%22:null%2C%22jsc%22:null}',
            # 'priority': 'u=0, i',
            'referer': 'https://www.equipmentradar.com/en/directory',
            # 'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            # 'sec-ch-ua-mobile': '?0',
            # 'sec-ch-ua-platform': '"Windows"',
            # 'sec-fetch-dest': 'document',
            # 'sec-fetch-mode': 'navigate',
            # 'sec-fetch-site': 'same-origin',
            # 'sec-fetch-user': '?1',
            # 'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }

        for dealer in dealers:
            # logging.info('111111111111111111111111')
            dealer_name = dealer.xpath('.//h3/text()').extract_first().strip()
            dealer_link = dealer.xpath('.//a[contains(text(), "Visit Page")]/@href').extract_first().strip()

            dealer_link = 'https://www.equipmentradar.com' + dealer_link

            # logging.info(dealer_name)
            # logging.info(dealer_link)
            # logging.info('222222222222222222222222')

            yield scrapy.http.Request(url=dealer_link,
                                      callback=self.parse_detail_page,
                                      headers=headers,
                                      cookies=cookies,
                                      cb_kwargs={
                                          'dealer_name': dealer_name,
                                      },
                                      )

    def parse_detail_page(self, response, **kwargs):
        dealer_name = response.cb_kwargs['dealer_name']
        dealer_website = response.xpath('//span[contains(text(), "Visit Website")]/../@href').extract_first().strip()
        dealer_domain = urlparse(dealer_website).netloc

        logging.info(dealer_name)
        logging.info(dealer_website)
        logging.info(dealer_domain)

        item = EquipmentradarItem()

        item['dealer_name'] = dealer_name
        item['dealer_website'] = dealer_website
        item['dealer_domain'] = dealer_domain

        return item
