#coding:utf-8
from baike import url_manager, html_download, html_parser, html_output

class BaiKeSpider:

    def __init__(self):
        self.urls = url_manager.UrlManager()
        self.downloader = html_download.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.output = html_output.HtmlOutPut()

    def run(self, start_url):
        self.urls.add_url(start_url)
        count = 1
        while self.urls.has_url():
            url = self.urls.get_url()
            try:
                print('正在爬取第{}个url：{}'.format(count, url))
                html_content = self.downloader.download(url)
                new_urls, new_data = self.parser.parse(url, html_content)
                self.urls.add_urls(new_urls)
                self.output.collect_data(new_data)
            except Exception as e:
                print('Craw failed:', e)
            if count == 100:
                break
            count += 1
        self.output.show_html()

if __name__ == '__main__':
    start_url = 'http://baike.baidu.com/view/21087.htm'
    baike_spider = BaiKeSpider()
    baike_spider.run(start_url)