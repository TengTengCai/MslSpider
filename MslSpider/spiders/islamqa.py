# -*- coding: utf-8 -*-
import hashlib

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from MslSpider.items import MslspiderItem


class IslamqaSpider(CrawlSpider):
    name = 'islamqa'
    allowed_domains = ['islamqa.info']
    start_urls = ['https://islamqa.info/ar/']

    rules = (
        # Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'https://islamqa.info/ar/answers/\d+/.*?'), callback='parse_ar', follow=True),
        Rule(LinkExtractor(allow=r'https://islamqa.info/zh/answers/\d+/.*?'), callback='parse_zh', follow=True),
        Rule(LinkExtractor(allow=r'https://islamqa.info/en/answers/\d+/.*?'), callback='parse_en', follow=True),
        Rule(LinkExtractor(allow=r'https://islamqa.info/[a-z]{2}/categories/topics/\d+/.*?'), callback='parse_new_page',
             follow=True),
    )

    def start_requests(self):
        lang_list = [
            'ar',
            'zh',
            'en',
        ]
        for k in lang_list:
            for i in range(1, 300):
                new_url = f'https://islamqa.info/{k}/categories/topics/{i}'
                print("当前抓取的 Url 是：" + new_url)
                yield Request(new_url)

    def parse_ar(self, response):
        m = hashlib.md5()
        m.update(str(response.url).encode('utf-8'))
        i = MslspiderItem()
        i['title'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first().replace('\n', '') \
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
        # q_list = [q.strip("\n\r").replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
        #           for q in question_list]
        # i['question'] = ' '.join(q_list[::-1])
        i['question'] = ' '.join(question_list).replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ") \
            .replace("\r", " ")
        answer_list = response.xpath(
            '/html/body/section/div[1]/div/section/div/div[2]/section/section/div//text()').extract()
        # a_list = [a.strip("\n\r").replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
        #           for a in answer_list]
        # answer = '{{rr}}'.join(a_list[::-1])
        answer = ' '.join(answer_list).replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ") \
            .replace("\r", " ")
        i['answer'] = answer
        qa_id = response.xpath('/html/body/section/div[1]/div/section/div/div[1]/div/div[1]/div[1]/p/text()') \
            .extract()[1].split()[0]
        i['qa_id'] = qa_id
        i['url_mark'] = m.hexdigest()
        i['r_type'] = "islamqa"
        i['lang'] = "ar"
        del m
        return i

    # def parse_item(self, response):
    #     i = {}
    #     # i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
    #     # i['name'] = response.xpath('//div[@id="name"]').extract()
    #     # i['description'] = response.xpath('//div[@id="description"]').extract()
    #     return i

    def parse_new_page(self, response):
        a_link = response.xpath('//a/@href').extract()
        for link in a_link:
            yield Request(link)

    def parse_zh(self, response):
        m = hashlib.md5()
        m.update(str(response.url).encode('utf-8'))
        i = MslspiderItem()
        i['title'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first().replace('\n', '') \
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
        i['question'] = ' '.join(q_list)
        answer_list = response.xpath(
            '/html/body/section/div[1]/div/section/div/div[2]/section/section/div/p/text()').extract()
        a_list = [a.strip("\n\r").replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
                      .replace("   ", '') for a in answer_list]
        # answer = ' '.join(answer_list).replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ") \
        #     .replace("\r", " ")
        answer = ' '.join(a_list)
        i['answer'] = answer
        qa_id = response.xpath('/html/body/section/div[1]/div/section/div/div[1]/div/div[1]/div[1]/p/text()') \
            .extract()[1].split()[0]
        i['qa_id'] = qa_id
        i['url_mark'] = m.hexdigest()
        i['r_type'] = "islamqa"
        i['lang'] = "zh"
        del m
        return i

    def parse_en(self, response):
        m = hashlib.md5()
        m.update(str(response.url).encode('utf-8'))
        i = MslspiderItem()
        title = response.xpath('//h1[@itemprop="name"]/text()').extract_first()
        if title:
            i['title'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first().replace('\n', '') \
                .replace('   ', '')
        else:
            return None
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
        i['question'] = ' '.join(q_list)
        answer_list = response.xpath(
            '/html/body/section/div[1]/div/section/div/div[2]/section/section/div/p/text()').extract()
        a_list = [a.strip("\n\r").replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
                      .replace("   ", '') for a in answer_list]
        # answer = ' '.join(answer_list).replace("r\n\\", " ").replace("\r\n", " ").replace("\n", " ") \
        #     .replace("\r", " ")
        answer = ' '.join(a_list)
        i['answer'] = answer
        qa_id = response.xpath('/html/body/section/div[1]/div/section/div/div[1]/div/div[1]/div[1]/p/text()') \
            .extract()[1].split()[0]
        i['qa_id'] = qa_id
        i['url_mark'] = m.hexdigest()
        i['r_type'] = "islamqa"
        i['lang'] = "en"
        del m
        return i
