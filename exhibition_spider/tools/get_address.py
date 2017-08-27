#_*_coding:utf-8 _*_
import requests

class GetAddress:

    def __init__(self):
        self.url = 'http://restapi.amap.com/v3/place/text'

    def get_data(self, venue='', city=''):
        params = {
            'key':'9dae296022a975ffef54a3837144e2f2',
            'keywords': venue,
            'types': '',
            'city': city,
            'children': 0,
            'offset': 5,
            'page': 1,
            'extensions': 'all'
        }
        response = requests.get(self.url, params=params)
        print response.text
        data = response.json()
        if data['status'] != '1':
            print '访问出错'
            return None
        if int(data['count']) < 1:
            print '未找到%s的数据'%venue
            return None
        data = data['pois']
        return data

    def parse_data(self, data, venue=''):
        print ';'.join([i['name'] for i in data])
        data = data[0]
        format_venue = data['name'].strip()
        address = ''.join(data['address'])
        lng = data['location'].strip().split(',')[0]
        lat = data['location'].strip().split(',')[1]
        tel = ''.join(data['tel'])      #tel可能是空的list
        seat = ''.join(data['adname'])
        zone = ''.join(data['business_area'])
        print format_venue, address, lng, lat, tel, seat, zone
        return (format_venue, address, lng, lat, tel, seat, zone)

    def get_address(self, venue='', city=''):
        venue = '国家会议中心'
        city = '北京'
        #print venue, city
        data = self.get_data(venue, city)
        if data:
            address_group = self.parse_data(data, venue)
            return address_group
        else:
            return None

if __name__ == '__main__':
    address = GetAddress()
    print address.get_address()
