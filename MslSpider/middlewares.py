# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time
from logging import getLogger

from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from random import choice

from MslSpider.settings import USER_AGENT_LIST
from MslSpider.settings import PROXY_IP_LIST


class MslspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MslspiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SeleniumMiddleware(object):
    def __init__(self, timeout=30):
        self.logger = getLogger(__name__)
        self.timeout = timeout
        # dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap = dict(DesiredCapabilities.CHROME)
        dcap[
            "phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
        # self.browser = webdriver.PhantomJS(desired_capabilities=dcap)
        self.browser = webdriver.Chrome(desired_capabilities=dcap)
        self.browser.set_window_size(1400, 700)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def __del__(self):
        self.browser.close()

    def process_request(self, request, spider):
        # self.logger.debug('PhantomJS is Starting')
        self.logger.debug('Chrome is Starting')
        try:
            self.browser.implicitly_wait(30)
            self.logger.debug(request.url)
            self.browser.get(request.url)
            # js = "var q=document.documentElement.scrollTop=10000"
            # self.browser.execute_script(js)
            time.sleep(3)
            body = self.browser.page_source
            # self.logger.debug(body)
            return HtmlResponse(url=request.url, status=200, body=body,
                                request=request, encoding='utf-8')
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)


class SetUserAgentAndProxyMiddleware(object):
    def __init__(self):
        self._error_times = 0

    def process_request(self, request, spider):
        user_agent = choice(USER_AGENT_LIST)
        # proxy_https = choice(PROXY_IP_LIST)
        if user_agent:
            request.headers.setdefault('User-Agent', user_agent)
            # request.meta['proxy'] = 'http://' + proxy_https

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        if response.status == 400:
            self._error_times += 1
        if self._error_times > 10:
            spider.crawler.engine.close_spider(spider, 'Request Bad')

        return response
