import requests
from lxml import etree
from urllib.parse import urljoin
from pymongo import MongoClient

"""从多个网站抓取姓名"""

client = MongoClient('localhost', 27017)
db = client['data']
name_collection = db['names']


url1 = 'http://www.yw11.com/namelist.php'
url2 = 'http://www.resgain.net/xmdq.html'


def get_name1(url):
    res = requests.get(url)
    doc = etree.HTML(res.content)
    surnames_url = doc.xpath('//ul[@class="e3"]/li/a/@href')
    surnames = doc.xpath('//ul[@class="e3"]/li/a/text()')
    surnames_url = [urljoin(url, surname_url) for surname_url in surnames_url]
    for surname, surname_url in zip(surnames, surnames_url):
        # print(surname, surname_url)
        res = requests.get(surname_url)
        doc = etree.HTML(res.content)
        names = doc.xpath('//div[@class="listbox1_text"]/ul/li/text()')
        names = [name.strip() for name in names if name.strip()]
        names = {'surname': surname, 'names': list(set(names))}
        save_data(names)


def get_name2(url):
    res = requests.get(url)
    doc = etree.HTML(res.content)
    surnames_url = doc.xpath('//div[@class="col-xs-12"]/a/@href')
    surnames = doc.xpath('//div[@class="col-xs-12"]/a/text()')
    surnames = [surname.split('姓')[0] for surname in surnames]
    surnames_url = [urljoin(url, surname_url) for surname_url in surnames_url]
    for surname, surname_url in zip(surnames, surnames_url):
        surname_urls = [urljoin(surname_url, 'name/{}_{}.html'.format(sex, page)) for sex in ['boys', 'girls'] for page in range(1, 11)]
        print(surname, surname_urls)
        name_dict = {'surname': surname}
        names = set()
        for surl in surname_urls:
            print(surl)
            res = requests.get(surl)
            doc = etree.HTML(res.content)
            name = doc.xpath('//div[@class="col-xs-12"]/a/text()')
            name = [n.strip() for n in name if n.strip()]
            print(name)
            names = names | set(name)

        print(len(names))
        name_dict['names'] = list(names)
        print(name_dict)
        save_data(name_dict)



def save_data(item):
    names = name_collection.find_one({'surname': item['surname']})
    print(item)
    if names:
        item['names'] = list(set(names['names']+item['names']))
        print(item)
    name_collection.find_one_and_update(
        {'surname': item['surname']},
        {'$set': item},
        upsert=True
    )


if __name__ == '__main__':
    # surname = get_name1(url1)
    surname = get_name2(url2)

