#coding:utf-8
import requests

class HtmlDownloader:

    def __init__(self):
        pass

    def download(self, url):
        if not url:
            return None
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.content