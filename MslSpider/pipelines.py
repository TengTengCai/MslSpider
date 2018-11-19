# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import random
import time

import pymysql
from pymysql import Error as DBError


class MslspiderPipeline(object):
    def __init__(self):
        self.db = pymysql.connect(host='127.0.0.1',
                                  user='root',
                                  password='123456',
                                  port=3306,
                                  db='msl_spider')
        self.db.set_charset('utf8')
        # self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        my_item = dict(item)
        time.sleep(random.randint(1, 3))
        try:
            if not self.is_exist(my_item["url_mark"]):
                self.add_content(item)
        except Exception as e:
            print(e)
            raise e
        return item

    def is_exist(self, mark):
        sql = f'SELECT count(*) FROM religion3 WHERE url_mark =\'{mark}\';'
        print(sql)
        try:
            self.db.ping(reconnect=True)
            with self.db.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
                return True if result[0] > 0 else False
        except DBError as e:
            # print(e)
            raise e

    def add_content(self, item):
        sql = f'INSERT INTO religion3(title, tag, categories, question, answer, url_mark, r_type, lang) ' \
              f'values (\'{item["title"]}\', \'{item["tag"]}\', \'{item["categories"]}\', \'{item["question"]}\', ' \
              f'\'{item["answer"]}\',\'{item["url_mark"]}\', \'{item["r_type"]}\', \'{item["lang"]}\')'
        print(sql)
        try:
            self.db.ping(reconnect=True)
            with self.db.cursor() as cursor:
                cursor.execute(sql)
            self.db.commit()
        except DBError as e:
            # print(e)
            raise e
