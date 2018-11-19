# -*- coding: utf-8 -*-
import hashlib
import re

import scrapy
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from MslSpider.items import MslspiderItem


class BinbazSpider(CrawlSpider):
    name = 'binbaz'
    allowed_domains = ['binbaz.org.sa']
    start_urls = ['https://binbaz.org.sa/']

    rules = (
        # Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'https://binbaz.org.sa/fatwas/\d+/.*?'), callback='parse_fatwas', follow=True),
        Rule(LinkExtractor(allow=r'https://binbaz.org.sa/categories/fiqhi/\d+?page=\d+'), callback='parse_page',
             follow=True),
        # Rule(LinkExtractor(allow=r'https://binbaz.org.sa/audios/\d+/.*?'), callback='parse_audios', follow=True),
    )

    def start_requests(self):
        for i in range(1, 400):
            newUrl = f'https://binbaz.org.sa/categories/fiqhi/{i}'
            print("当前抓取的 Url 是：" + newUrl)
            yield Request(newUrl)

    def parse_fatwas(self, response):
        """
        title, tag, categories, question, answer, mark


        :param response:
        :return:
        """
        m = hashlib.md5()
        m.update(str(response.url).encode('utf-8'))
        i = MslspiderItem()
        title = response.xpath('//h1[@class="article-title article-title--primary"]/text()').extract_first()
        i['title'] = ''.join(title).replace('\n', '').replace('n\\', '').replace('   ', '')
        i['tag'] = response.xpath('//div[@class="categories"]/*[4]/text()').extract_first()
        i['categories'] = response.xpath('//div[@class="categories"]/*[2]/text()').extract_first()
        # question_list = response.xpath('//h2[@itemprop="alternativeHeadline"]//text()').extract()
        question_list = response.xpath(
            '//p[@itemprop="articleBody"][1]/preceding-sibling::p//text()|'
            '//p[@itemprop="articleBody"][1]/preceding-sibling::h2//text()').extract()
        # q_list = [' '.join(q.strip("\n\r").replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ")
        #           .replace("\r", " ").split()) for q in question_list]
        # i['question'] = ' '.join(q_list)
        i['question'] = ' '.join(question_list).replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ") \
            .replace("\r", " ").replace("   ", '')
        answer_list = response.xpath('//p[@itemprop="articleBody"][1]/following-sibling::*/text()').extract()
        if len(answer_list) == 0:
            answer_list = response.xpath('//p[@itemprop="articleBody"]/text()').extract()
        # a_list = [a.strip("\n\r").replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
        #           .replace("   ", '')for a in answer_list
        # i['answer'] = ' '.join(a_list)
        i['answer'] = ' '.join(answer_list).replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ") \
            .replace("\r", " ")
        i['qa_id'] = re.search('https://binbaz.org.sa/fatwas/(\d+)/.*?', response.url).group(1)
        i['url_mark'] = m.hexdigest()
        i['r_type'] = "binbaz"
        i['lang'] = "ar"

        # i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        # i['name'] = response.xpath('//div[@id="name"]').extract()
        # i['description'] = response.xpath('//div[@id="description"]').extract()
        return i

    def parse_page(self, response):
        a_link = response.xpath('//a/@href').extract()
        for link in a_link:
            yield Request(link)

    def parse_audios(self, response):
        """
        title, tag, categories, question, answer, mark
        :param response:
        :return:
        """
        m = hashlib.md5()
        m.update(response.url)
        i = MslspiderItem()
        i.title = response.xpath('')
        i.categories = response.xpath('')
        i.tag = i.categories
        i.question = i.title
        i.answer = response.xpath('')
        i.url_mark = m.hexdigest()
        i.r_type = "audios"
        # i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        # i['name'] = response.xpath('//div[@id="name"]').extract()
        # i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
