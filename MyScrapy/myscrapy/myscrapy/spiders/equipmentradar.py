import re
import json
import scrapy
import logging
from parsel import Selector
from urllib.parse import urlparse
from myscrapy.items import EquipmentradarItem


def get_request_data(search_id, pvuuid):
    data = {
        'action': 'show_more',
        'view': 'directory',
        'id': f'{search_id}',
        'pvuuid': f'{pvuuid}',
        'muuid': '',
    }
    return data


def create_header(t=''):
    if t:
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.equipmentradar.com',
            'priority': 'u=1, i',
            'referer': 'https://www.equipmentradar.com/en/directory',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'x-csrftoken': f'{t}',
            'x-requested-with': 'XMLHttpRequest',
        }
    else:
        headers = {
            'referer': 'https://www.equipmentradar.com/en/directory',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }

    return headers


class EquipmentradarSpider(scrapy.Spider):
    name = "equipmentradar"
    allowed_domains = ["equipmentradar.com"]
    detail_count = 0
    total_count = 0
    t = ''
    pvuuid = ''
    cookie_t = ''
    dealers = ''
    url = "https://www.equipmentradar.com/en/directory"

    custom_settings = {
        'ITEM_PIPELINES': {'myscrapy.pipelines.EquipmentradarPipeline': 300},
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,  # 单个域执行的并发（即同时）请求的最大数量
        # 'DOWNLOAD_DELAY': 8
    }

    def start_requests(self):
        logging.info(f'Start request first page - no search id')
        yield scrapy.http.Request(url=self.url,
                                  callback=self.parse_main_page,
                                  headers=create_header(),
                                  cb_kwargs={
                                      'first_page': True,
                                  },
                                  )

    def parse_main_page(self, response, **kwargs):
        res_dict = None
        if response.cb_kwargs['first_page']:
            # get token and pvuuid,
            script_info = response.xpath('//script[@id="app_config"]/text()').extract_first().strip()
            session_dict = json.loads(script_info)
            self.t = session_dict['session']['t']
            self.pvuuid = session_dict['session']['pvuuid']

            # get response header, then get set-cookies, token is in cookies.
            set_cookie_str = response.headers.get('Set-Cookie').decode('utf-8')
            m = re.match(r'^.*t=([^;]+);.*$', set_cookie_str)
            if m:
                self.cookie_t = m.group(1)
                logging.info(f'Got token from response header: {self.cookie_t}')
            else:
                logging.error('ERROR: token is not found in response header.')

            self.dealers = response.xpath('//div[@class="list-group-item list-group-item-action dcard"]')
            logging.info('Got dealers in the first page ')
        else:
            res_dict = json.loads(response.text)
            html = Selector(res_dict['results'])
            self.dealers = html.xpath('//div[@class="list-group-item list-group-item-action dcard"]')
            logging.info('Got dealers in the non-first page ')

        for dealer in self.dealers:
            self.detail_count += 1
            dealer_name = dealer.xpath('.//h3/text()').extract_first().strip()
            dealer_link = dealer.xpath('.//a[contains(text(), "Visit Page")]/@href').extract_first().strip()

            dealer_link = 'https://www.equipmentradar.com' + dealer_link
            logging.info(f'{self.detail_count}: start request detail url: {dealer_link}')
            yield scrapy.http.Request(url=dealer_link,
                                      callback=self.parse_detail_page,
                                      headers=create_header(),
                                      cb_kwargs={
                                          'dealer_name': dealer_name,
                                      },
                                      )

        if not self.total_count:
            self.total_count = response.xpath('//*[@id="search-map-text"]/b/text()').extract_first().strip()
            self.total_count = int(self.total_count.replace(',', ''))
            logging.info(f'Found total count is: {self.total_count}')

        if self.detail_count < self.total_count:
            logging.info(f'Please note that detail_count < total_count, {self.detail_count}, {self.total_count}')

            if response.cb_kwargs['first_page']:
                search_str = response.xpath('//*[@id="page_data"]/text()').extract_first().strip()
                search_json = json.loads(search_str)
                search_id = search_json['view_context']['search_id']
                logging.info(f'Got first page search_id: {search_id}')
            else:
                search_id = str(res_dict['search_id']).strip()
                logging.info(f'Got not-first page search_id: {search_id}')

            if not search_id:
                logging.error(f'ERROR: search_id not found.')

            cookies = {
                'sd': '9583186',
                't': f'{self.cookie_t}',
                'ls': '{%22cd%22:null%2C%22jsc%22:null}',
                '_gid': 'GA1.2.1703916774.1714629682',
                '__gads': 'ID=43c4a204b596faa2:T=1714629676:RT=1714646583:S=ALNI_MZCAI1HLnkGtKJtqqgK_Owq6zyhvg',
                '__gpi': 'UID=00000df78dcaa651:T=1714629676:RT=1714646583:S=ALNI_MYxoXa-O4QMd2lNvMHhccI_fDeDnQ',
                '__eoi': 'ID=c7735e0d6a45b816:T=1714629676:RT=1714646583:S=AA-AfjbT77N7ipSWvRbmQ-dwsiVX',
                '_gat_UA-166234337-3': '1',
                '_ga': 'GA1.1.904000137.1714629675',
                '_ga_G8LEFZSZ1G': 'GS1.1.1714644948.5.1.1714646744.0.0.0',
            }

            header = create_header(self.t)
            form_data = get_request_data(search_id, self.pvuuid)

            logging.info(f'Start request next pages with search id: {search_id} ')
            yield scrapy.http.FormRequest(url=self.url,
                                          callback=self.parse_main_page,
                                          formdata=form_data,
                                          headers=header,
                                          cookies=cookies,
                                          cb_kwargs={
                                              'first_page': False,
                                          },
                                          )

    def parse_detail_page(self, response, **kwargs):
        logging.info(f'NOTE: Got response from: {response.url}')
        dealer_name = response.cb_kwargs['dealer_name']
        dealer_website = response.xpath('//span[contains(text(), "Visit Website")]/../@href').extract_first().strip()
        dealer_domain = urlparse(dealer_website).netloc

        item = EquipmentradarItem()
        item['dealer_name'] = dealer_name
        item['dealer_website'] = dealer_website
        item['dealer_domain'] = dealer_domain

        return item
