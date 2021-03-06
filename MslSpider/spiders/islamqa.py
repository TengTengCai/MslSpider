# -*- coding: utf-8 -*-
import hashlib
import re
from urllib.parse import urljoin

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from MslSpider.items import MslspiderItem
from MslSpider.settings import islamqa_settings


class IslamqaSpider(CrawlSpider):
    """ islamqa.info问答爬虫 """
    name = 'islamqa'
    allowed_domains = ['islamqa.info']
    start_urls = ['https://islamqa.info/']
    custom_settings = islamqa_settings

    rules = (
        # Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
        # Rule(LinkExtractor(allow=r'https://islamqa.info/ar/answers/\d+/.*'), callback='parse_ar', follow=True),
        # Rule(LinkExtractor(allow=r'https://islamqa.info/zh/answers/\d+/.*'), callback='parse_zh', follow=True),
        # Rule(LinkExtractor(allow=r'https://islamqa.info/en/answers/\d+/.*'), callback='parse_en', follow=True),
        # Rule(LinkExtractor(allow=r'https://islamqa.info/bn/answers/\d+/.*'), callback='parse_bn', follow=True),
        Rule(LinkExtractor(allow=r'https://islamqa.info/[a-z]{2}/answers/\d+/.*'), callback='parse_normal',
             follow=True),
        # Rule(LinkExtractor(allow=r'/[a-z]{2}/answers/\d+/.*'), callback='parse_normal',
        #      follow=True),
        Rule(LinkExtractor(allow=r'https://islamqa.info/[a-z]{2}/categories/topics/\d+/.*[?page=\d+]?'),
             callback='parse_new_page', follow=True),
        # Rule(LinkExtractor(allow=r'/[a-z]{2}/categories/topics/\d+/.*'), callback='parse_new_page',
        #      follow=True),
    )

    def start_requests(self):
        """
        动态添加Scrapy的爬取初始链接

        :return Request:  请求对象
        """
        lang_list = [
            'ar',   # 阿拉伯语
            'zh',   # 中文
            'en',   # 英文
            'bn',   # 孟加拉语
            'ug',   # 维吾尔族语
            'tr',   # 土耳其语
            'ru',   # 俄语
            'pt',   # 葡萄牙语
            'id',   # 印度尼西亚语
            'hi',   # 菲律宾语
            'ge',   # 德语
            'fr',   # 法语
            'fa',   # 波斯语
            'es',   # 西班牙语
            'ur',   # 乌尔都语
        ]
        for k in lang_list:
            for i in range(1, 300):
                new_url = f'https://islamqa.info/{k}/categories/topics/{i}'
                print("当前抓取的 Url 是：" + new_url)
                yield Request(new_url)

    def parse_normal(self, response):
        """
        解析爬取的问答页面

        :param response: 响应对象
        :return MslspiderItem: 数据对象
        """
        m = hashlib.md5()
        m.update(str(response.url).encode('utf-8'))
        i = MslspiderItem()
        i['title'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first(default='').replace('\n', '') \
            .replace('   ', '')
        nav = response.xpath('//nav[@aria-label="breadcrumbs"]')
        if len(nav) > 0:
            i['tag'] = str(response.xpath('//span[@itemprop="name"]/text()').extract()[-1]).replace('\n', '') \
                .replace('  ', '')
            i['categories'] = response.xpath('//span[@itemprop="name"]/text()').extract()[1].replace('\n', '') \
                .replace('  ', '')
        else:
            i['tag'] = ''
            i['categories'] = ''
        question_list = response.xpath('/html/body/section/div[1]/div/section/div/section[2]/div//text()').extract()
        q_list = [q.strip("\n\r").replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
                  .replace("   ", '') for q in question_list]
        # i['question'] = ' '.join(question_list).replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ") \
        #     .replace("\r", " ")
        i['question'] = '\r\n'.join(q_list).replace('\r\n\r\n', '')
        answer_list = response.xpath(
            '/html/body/section/div[1]/div/section/div/div[2]/section/section/div//text()').extract()
        a_list = [a.strip("\n\r").replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
                  .replace("   ", '') for a in answer_list]
        # answer = ' '.join(answer_list).replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ") \
        #     .replace("\r", " ")
        answer = '\r\n'.join(a_list).replace('\r\n\r\n', '')
        i['answer'] = answer
        qa_id = response.xpath('/html/body/section/div[1]/div/section/div/div[1]/div/div[1]/div[1]/p/text()') \
            .extract()[1].split()[0]
        i['qa_id'] = qa_id
        i['url_mark'] = m.hexdigest()
        i['r_type'] = "islamqa"
        lang = re.search('https://islamqa.info/([a-z]{2})/answers/\d+/.*', response.url).group(1)
        i['lang'] = lang
        del m
        return i

    def parse_new_page(self, response):
        """
        将链接添加到访问队列中

        :param response:    响应对象
        :return Request:    页面中的请求对象
        """
        a_link = response.xpath('//a/@href').extract()
        for link in a_link:
            link = urljoin('https://islamqa.info/', link)
            yield Request(link)
