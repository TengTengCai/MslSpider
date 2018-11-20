# -*- coding: utf-8 -*-
import hashlib
import re
from urllib.parse import urljoin

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from MslSpider.items import MslspiderItem
from MslSpider.settings import binbaz_settings


class BinbazSpider(CrawlSpider):
    name = 'binbaz'
    allowed_domains = ['binbaz.org.sa']
    start_urls = ['https://binbaz.org.sa/']
    custom_settings = binbaz_settings

    rules = (
        # Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'https://binbaz.org.sa/fatwas/\d+/.*?'), callback='parse_fatwas', follow=True),
        Rule(LinkExtractor(allow=r'/fatwas/\d+/.*?'), callback='parse_fatwas', follow=True),
        Rule(LinkExtractor(allow=r'https://binbaz.org.sa/categories/fiqhi/\d+?page=\d+'), callback='parse_page',
             follow=True),
        Rule(LinkExtractor(allow=r'/categories/fiqhi/\d+?page=\d+'), callback='parse_page',
             follow=True),
        # Rule(LinkExtractor(allow=r'https://binbaz.org.sa/audios/\d+/.*?'), callback='parse_audios', follow=True),
    )

    def start_requests(self):
        """
        动态添加Scrapy的爬取初始链接

        :return Request: 请求对象
        """
        for i in range(1, 400):
            new_url = f'https://binbaz.org.sa/categories/fiqhi/{i}'
            print("当前抓取的 Url 是：" + new_url)
            yield Request(new_url)

    def parse_fatwas(self, response):
        """
        页面解析方法
        title, tag, categories, question, answer, mark

        :param response:    响应对象
        :return MslspiderItem: 爬取的数据对象
        """
        m = hashlib.md5()
        m.update(str(response.url).encode('utf-8'))
        i = MslspiderItem()
        title = response.xpath('//h1[@class="article-title article-title--primary"]/text()').extract_first(default='')
        i['title'] = ''.join(title).replace('\n', '').replace('n\\', '').replace('   ', '')
        i['tag'] = response.xpath('//div[@class="categories"]/*[4]/text()').extract_first(default='')
        i['categories'] = response.xpath('//div[@class="categories"]/*[2]/text()').extract_first(default='')
        question_list = response.xpath(
            '//p[@itemprop="articleBody"][1]/preceding-sibling::p//text()|'
            '//p[@itemprop="articleBody"][1]/preceding-sibling::h2//text()').extract()
        i['question'] = ' '.join(question_list).replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ") \
            .replace("\r", " ").replace("   ", '')
        answer_list = response.xpath('//p[@itemprop="articleBody"][1]/following-sibling::*//text()').extract()
        i['answer'] = ' '.join(answer_list).replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ") \
            .replace("\r", " ").replace("   ", '')
        i['qa_id'] = re.search('https://binbaz.org.sa/fatwas/(\d+)/.*?', response.url).group(1)
        i['url_mark'] = m.hexdigest()
        i['r_type'] = "binbaz"
        i['lang'] = "ar"

        # i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        # i['name'] = response.xpath('//div[@id="name"]').extract()
        # i['description'] = response.xpath('//div[@id="description"]').extract()
        return i

    def parse_page(self, response):
        """
        将链接添加到访问队列中

        :param response:    响应对象
        :return Request:    页面中的请求对象
        """
        a_link = response.xpath('//a/@href').extract()
        for link in a_link:
            link = urljoin('https://binbaz.org.sa/', link)
            yield Request(link)
