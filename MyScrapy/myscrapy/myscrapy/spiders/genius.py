import logging
import scrapy


class GeniusSpider(scrapy.Spider):
    name = "genius"
    allowed_domains = ["genius.com"]
    start_urls = ["https://genius.com/Twenty-one-pilots-backslide-lyrics"]
    lyrics = ''

    def parse(self, response, **kwargs):
        logging.info('111111111111111111')
        # logging.info(response.text)

        selector_list = response.xpath('//*[@id="lyrics-root"]/div[@class="Lyrics__Container-sc-1ynbvzw-1 kUgSbL"]//text()')
        logging.info(type(selector_list))
        # logging.info(selector_list)

        for selector in selector_list:
            logging.info(type(selector))
            logging.info(selector)
            # for txt in selector.itertext():
            self.lyrics = self.lyrics + '\n' + selector.get()

        logging.info(f'''\n\n---------------Please see the desired lyrics as follows: ---------------
                {self.lyrics}
        ''')
