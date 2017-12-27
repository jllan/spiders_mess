# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


# from cookies import cookies
# from .user_agent import agents
# from .user_agent import agents_mobile
from .proxy import get_proxy_available

# class UserAgentMiddleware(object):
#     """ 换User-Agent """
#
#     def process_request(self, request, spider):
#         agent = random.choice(agents)
#         # agent = random.choice(agents_mobile)
#         request.headers["User-Agent"] = agent
#         # request.headers['Cookie'] = 'prov=244d7b9e-30e6-4f6b-a8db-8ce26444efb6; __qca=P0-1272077840-1457968696850; usr=p=[2|6]; _gat=1; _gat_pageData=1; _ga=GA1.2.1877860909.1480826598'
#         # request.headers['Referer'] = 'http://stackoverflow.com/questions'


class ProxyMiddleware(object):
    """ 设置代理 """
    def process_request(self, request, spider):
        proxy = get_proxy_available()
        # proxy = '121.22.212.84:8118'
        print('使用代理：', proxy)
        request.meta['proxy'] = proxy


class MobaispiderSpiderMiddleware(object):
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
