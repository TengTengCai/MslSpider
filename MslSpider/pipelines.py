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
        table_name = spider.settings.get('TABLE_NAME')
        my_item = dict(item)
        time.sleep(random.randint(1, 3))
        try:
            if not self.is_exist(my_item["url_mark"], table_name):
                self.add_content(item, table_name)
        except Exception as e:
            print(e)
            raise e
        return item

    def is_exist(self, mark, table_name):
        sql = f'SELECT count(*) FROM {table_name} WHERE url_mark =\'{mark}\';'
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

    def add_content(self, item, table_name):
        # sql = f'INSERT INTO religion6(title, tag, categories, question, answer, qa_id, url_mark, r_type, lang) ' \
        #       f'values (\'{escape_string(item["title"])}\', \'{escape_string(item["tag"])}\', ' \
        #       f'\'{escape_string(item["categories"])}\', \'{escape_string(item["question"])}\', ' \
        #       f'\'{item["answer"]}\', \'{item["qa_id"]}\', \'{item["url_mark"]}\', \'{item["r_type"]}\', ' \
        #       f'\'{item["lang"]}\')'
        sql = "INSERT INTO " + table_name + " (title, tag, categories, question, answer, qa_id, url_mark, r_type, " \
                                            "lang) values (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        print("Do Insert ...")
        try:
            self.db.ping(reconnect=True)
            with self.db.cursor() as cursor:
                cursor.execute(sql, (item['title'], item['tag'], item['categories'], item['question'],
                                     item['answer'], item['qa_id'], item['url_mark'], item['r_type'], item['lang']))
            self.db.commit()
        except DBError as e:
            # print(e)
            raise e
