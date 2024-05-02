# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings
from myscrapy.db.base_mysql_db import BaseMySQLDB


class MyscrapyPipeline:
    def process_item(self, item, spider):
        return item

class EquipmentradarPipeline:

    def __init__(self):
        self.counter = 0

    def open_spider(self, spider):
        self.mysql_db = BaseMySQLDB()
        self.settings = get_project_settings()

    def close_spider(self, spider):
        if self.mysql_db:
            logging.debug('mysql_db been closed')
            self.mysql_db.close()

        logging.warning(f'Item >>>> {spider.name} >>>> {self.counter}')

    def process_item(self, item, spider):
        columns = [
            'dealer_name',
            'dealer_website',
            'dealer_domain',
        ]

        data = {}
        for column in columns:
            if column in item and item[column]:
                data[column] = str(item[column]).strip()

        self.mysql_db.insert('equipmentradar_table', data)

        logging.info(item)

        self.counter += 1

        return item
