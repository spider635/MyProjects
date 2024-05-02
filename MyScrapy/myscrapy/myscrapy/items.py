# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class EquipmentradarItem(scrapy.Item):
    # define the fields for your item here like:
    dealer_name = scrapy.Field()
    dealer_website = scrapy.Field()
    dealer_domain = scrapy.Field()
