#coding:utf-8
from baike import baike_db
import codecs

class HtmlOutPut:

    def __init__(self):
        self.data = []

    def collect_data(self, data):
        if not data:
            return
        self.data.append(data)

    def show_html(self):
        with codecs.open('baike.html', 'w', 'utf8') as f:
            f.write('<html>')
            f.write('<body>')
            f.write('<table>')
            for data in self.data:
                f.write('<tr>')
                f.write('<td>%s</td>' %data['title'])
                f.write('<td>%s</td>' % data['url'])
                f.write('<td>%s</td>' % data['summary'])
                f.write('</tr>')
            f.write('</table>')
            f.write('</body>')
            f.write('</html>')

    def write_db(self, data):
        if not data:
            return
        for data in self.data:
            baike_db.baike.insert_one(data)

