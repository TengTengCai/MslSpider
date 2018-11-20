# -*- coding: utf-8 -*-
from hashlib import md5
import re
from urllib.parse import urljoin

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from MslSpider.items import MslspiderItem
from MslSpider.settings import islamweb_settings


class IslamwebSpider(CrawlSpider):
    name = 'islamweb'
    allowed_domains = ['fatwa.islamweb.net']
    start_urls = ['http://fatwa.islamweb.net/']

    custom_settings = islamweb_settings

    rules = (
        Rule(LinkExtractor(allow=r'/[a-z]{2}/fatwa/\d+/.*'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'/[a-z]{2}/fatawa/\d+/.*[?pageno=\d+.*]?'), callback='parse_page', follow=True),
        # Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def start_requests(self):
        lang_list = [
            'ar',  # 阿拉伯语
            'es',  # 西班牙语
            'en',  # 英文
            'ge',  # 德语
            'fr',  # 法语
        ]
        for k in lang_list:
            for i in range(1, 10):
                new_url = f'http://fatwa.islamweb.net/{k}/fatawa/?tab={i}'
                print("当前抓取的 Url 是：" + new_url)
                yield Request(new_url)

    def parse_item(self, response):
        # item_tree = response.xpath('//ul[@class="tree"]').extract()
        # if len(item_tree) > 0:
        #     a_link = response.xpath('//a/@href').extract()
        #     for link in a_link:
        #         yield Request(link)

        item_title = response.xpath('//h3[@class="mainitemtitle2"]').extract()
        if len(item_title) > 0:
            m = md5()
            m.update(str(response.url).encode('utf-8'))
            i = MslspiderItem()
            title_list = response.xpath('/html/body/div/div[1]/section/div[1]/div[1]/h1/text()').extract()
            i["title"] = ' '.join(title_list).replace('\r\n', '').replace('\t', '').replace('   ', '')
            i["tag"] = response.xpath('//ol/li/a/text()').extract()[-1].replace('\r\n', '')
            i["categories"] = response.xpath('//ol/li/a/text()').extract()[1].replace('\r\n', '')
            q_list = response.xpath('/html/body/div/div[1]/section/div[1]/div[3]/p//text()').extract()
            i["question"] = '   '.join(q_list).replace('\r\n', '').replace('\t', '')
            a_list = response.xpath('/html/body/div/div[1]/section/div[1]/div[5]/p//text()').extract()
            i['answer'] = '   '.join(a_list).replace('\xa0', ' ').replace('\r\n', '').replace('\t', '')
            i['qa_id'] = re.search('http://fatwa.islamweb.net/[a-z]{2}/fatwa/(\d+)/.*', response.url).group(1)
            i['url_mark'] = m.hexdigest()
            i['r_type'] = 'islamweb'
            lang = re.search('http://fatwa.islamweb.net/([a-z]{2})/fatwa/(\d+)/.*', response.url).group(1)
            i['lang'] = 'ge' if lang == 'de' else lang
            del m
            return i

    def parse_page(self, response):
        item_list = response.xpath('//ul[@class="oneitems"]').extract()
        if len(item_list) > 0:
            a_link = response.xpath('//a/@href').extract()
            for link in a_link:
                link = urljoin('http://fatwa.islamweb.net/', link)

                yield Request(link)
