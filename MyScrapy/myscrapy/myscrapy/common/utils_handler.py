# -*- coding:utf-8 -*-
import datetime
import hashlib
import json
import logging
import os
import re
from logging.handlers import RotatingFileHandler
import html2text
import requests
from w3lib import html


class utils_date_encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


# 获取时间格式row24/42
def utils_get_strtime(text):
    if text == '' or text == None or text == []:
        return text
    text = text.replace("年", "-").replace("月", "-").replace("日", " ").replace("/", "-").replace(".", "-").strip()
    text = re.sub("\s+", " ", text)
    t = ""
    regex_list = [  # 2013年8月15日 22:46:21
        "(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2})",  # "2013年8月15日 22:46"
        "(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2})",  # "2014年5月11日"
        "(\d{4}-\d{1,2}-\d{1,2})",  # "2014年5月"
        "(\d{4}-\d{1,2})", "(\d{2}-\d{1,2}-\d{1,2})", ]
    for regex in regex_list:
        t = re.search(regex, text)
    if t:
        t = t.group(1)
        return t
    else:
        t = ''
    return t


def utils_init_log(log_file, log_level):
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('seleniumwire').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(filename)s,%(lineno)d] [%(threadName)s,%(thread)d] - %(message)s')

    rotating_file_log = RotatingFileHandler(log_file, maxBytes=100 * 1024 * 1024, backupCount=100, encoding='UTF-8')
    rotating_file_log.setLevel(logging.INFO)
    rotating_file_log.setFormatter(formatter)
    root_logger.addHandler(rotating_file_log)

    stream_log = logging.StreamHandler()
    stream_log.setFormatter(formatter)
    root_logger.addHandler(stream_log)


def utils_rm_html(content: str):
    if content:
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        s = converter.handle(content)
        if s:
            s = s.replace('*', '').replace('#', '').strip()
        return s


def utils_date_time(content: str):
    if content:
        rl = [
            ['发文日期：', ''],
            ['发文时间：', ''],
            ['发布日期：', ''],
            ['发布日期', ''],
            ['发布时间：', ''],
            ['发布时间:', ''],
            ['日期：', ''],
            ['时间：', ''],
            ['年', '-'],
            ['月', '-'],
            ['日', ''],
            ['\r\n', ''],
            ['\t', ''],
            [' -', '-'],
            ['- ', '-'],
            ['—', '-'],
            ['：', ''],
            [': ', ''],
            ['/', '-'],
        ]
        for r in rl:
            content = content.replace(r[0], r[1])

        match = re.compile(r'(\d{4})[ |-]+(\d{2})[ |-]+(\d{2})[ |-]+(\d{2})[ |:]+(\d{2})').match(content)
        if match:
            content = f"{match[1]}-{match[2]}-{match[3]} {match[4]}:{match[5]}"
        else:
            match = re.compile(r'.+(\d{4})[ |-|/]+(\d{2})[ |-|/]+(\d{2}).?').match(content)
            if match:
                content = f"{match[1]}-{match[2]}-{match[3]}"

    return content.strip()


def utils_filter_html(content: str,
                      which_ones=('span', 'br', 'p', 'strong', 'li', 'a', 'h1', 'div', 'img', 'ul', 'li')):
    content = html.remove_tags(content, which_ones=which_ones)
    content = re.sub(r'[　|\t]', '', content, flags=re.M)
    content = re.sub(r'>\s+<', '><', content)
    return content.strip()


def utils_rm_space(content: str):
    if content:
        content = re.sub(r'[ |　|\t|\n|\r]', ' ', content, flags=re.M)
        return content


def utils_rm_space_strip(content: str):
    if content:
        content = re.sub(r'[ |　|\t|\n|\r]', ' ', content, flags=re.M)
        return content.strip()


def download_file(url: str, name, headers={}, timeout=0, filet_ype=''):
    if filet_ype == '':
        file_type = url.split('.')[-1].lower()
    else:
        file_type = filet_ype

    file_name = hashlib.md5(url.encode()).hexdigest() + '.' + file_type
    file_path = os.path.join('download', name)

    file_dir = os.path.join(os.getcwd(), file_path)
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)

    abs_path = os.path.join(os.getcwd(), file_path, f"{file_name}")

    myfile = requests.get(url, allow_redirects=True, verify=False, headers=headers, timeout=timeout)  # https报错直接设置不验证
    open(abs_path, 'wb').write(myfile.content)
    return os.path.join(file_path, f"{file_name}")


def utils_mk(response, rules):
    ruls_list = {}
    if type(rules) == str:
        ruls_list = {rules: 'xpath'}

    elif type(rules) == list:
        for k in rules:
            ruls_list[k] = 'xpath'

    else:
        ruls_list = rules

    for key in ruls_list:
        content = None
        function = ruls_list[key]
        if function == 'xpath':
            content = response.xpath(key)
        elif function == 'css':
            content = response.css(key)
        elif function == 'text':
            content = key

        if content:
            return content

    return content


def utils_mk_phone(response, css):
    phone = response.css(css)
    if phone:
        phone = utils_rm_space(utils_rm_html(phone.extract_first()))
        if phone:
            phone = phone.replace('Phone:', '').strip()
            return phone


def utils_mk_company_link(response, css):
    company_link = response.css(css)
    if company_link:
        company_link = utils_rm_space(utils_filter_html(company_link.extract_first()))
        if company_link:
            company_link = company_link.replace('Phone:', '').strip()
            return company_link


# 拼接字符串
def utils_contact(keys, json):
    '''
    按照keys顺序提前value并拼接为字符串
    :param keys:
    :param json:
    :return:
    '''
    array = []
    for key in keys:
        if key in json and json[key]:
            array.append(json[key].strip())

    if array:
        return ', '.join(array).replace('None', '')


def utils_extra_phone(text):
    phone = re.findall('(1\d{10}|0\d{2,3}-?\d{7,8})', text)
    if phone:
        return ' | '.join(phone)
