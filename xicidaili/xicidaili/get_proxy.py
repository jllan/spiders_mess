import pymongo
from queue import Queue
# from Queue import Queue

q = Queue()


class ProxyGetting:
    def __init__(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client['Proxies']
        self.proxies = db['proxies']


    def get_proxy(self):
        proxy_list = self.proxies.find({},{'_id':0, 'address':0})[:100]
        for proxy in proxy_list:
            q.put(proxy['protocol']+'://'+proxy['ip']+':'+str(proxy['port']))

    def get_one_proxy(self):
        if q.qsize() > 10:
            return q.get()
        else:
            self.get_proxy()
