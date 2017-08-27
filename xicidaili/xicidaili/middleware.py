# encoding=utf-8
import random
# from cookies import cookies
from .user_agents import agents
from .get_proxy import ProxyGetting

class UserAgentMiddleware(object):
    """ 换User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent

class ProxyMiddleware(object):
    """ 设置代理 """
    def process_request(self, request, spider):
        request.meta['proxy'] = ProxyGetting().get_one_proxy()

# class CookiesMiddleware(object):
#     """ 换Cookie """
#
#     def process_request(self, request, spider):
#         cookie = random.choice(cookies)
#         request.cookies = cookie
