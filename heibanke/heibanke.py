__author__ = 'jlan'
#_*_coding:utf-8 _*_

import requests
import re
import time
import random
import pytesseract
from PIL import Image
from subprocess import Popen

def first(start_url):
    pattern = re.compile('<h3>.*?数字.*?(\d+).*?</h3>')
    url = ''
    num = ''
    while True:
        url = start_url + num
        print(url)
        response = requests.get(url)
        data = response.text
        num = re.findall(pattern, data)
        print(num)
        if not num:
            print(url)
            break
        else:
            num = str(num[0])
    return url

def second(url):
    pattern = re.compile('您输入的密码错误, 请重新输入')
    data = {
        'csrfmiddlewaretoken': 'Vcc9obuke0TkvRVOxePRJJU1eeyUjxpL',
        'username': 'asd',
    }
    passwd = 1
    while passwd<31:
        print(passwd)
        data['password'] = str(passwd)
        response = requests.post(url, data=data)
        if not re.findall(pattern, response.text):
            return passwd
        else:
            passwd += 1

'''def third():
    register_url = 'http://www.heibanke.com/accounts/register'
    name, email, passwd, = 'jlllan', 'cbj_love@126.com', 'cbj123'
    def get_data():
        response = requests.get(register_url)
        image_name = re.findall('src="/captcha/image/(.*?)/"', response.text)
        csrf = re.findall("name='csrfmiddlewaretoken' value='(.*?)'", response.text)[0]
        image_data = requests.get('http://www.heibanke.com/captcha/image/'+image_name[0]).content
        with open('pic.png', 'wb') as f:
            f.write(image_data)
        f.close()
        image = Image.open('pic.png')
        image_text = pytesseract.image_to_string(image)
        return (image_text, image_name[0], csrf)

    data = get_data()
    captcha = data[0]
    print(data[2],data[1],data[0])
    #Popen('pic.png',shell =True)
    #captcha = input('captcha: ')
    headers = {
        'Connection': 'keep-alive',
        'Content-Encoding': 'gzip',
        'Content-Type': 'text/html; charset=utf-8',
        #Date:Tue, 28 Jun 2016 08:34:09 GMT
        'Server': 'nginx/1.9.3',
        #Set-Cookie:csrftoken=2KBgRZhHZoZDklCGAD0DvpniXVGhslOm; expires=Tue, 27-Jun-2017 08:34:09 GMT; Max-Age=31449600; Path=/
        'Transfer-Encoding': 'chunked',
        'Vary': 'Cookie',
        'X-Frame-Options': 'SAMEORIGIN'
    }
    params = {
        'csrfmiddlewaretoken': '2KBgRZhHZoZDklCGAD0DvpniXVGhslOm',
        'username': name,
        'email': email,
        'password': passwd,
        're_password': passwd,
        'captcha_0': 'bdccfdbe8c2ecf90fb0d163c72a116fc40750cb3',
        'captcha_1': data[0]
    }
    print(params)
    response = requests.post(register_url, headers=headers, data=params)
    print(response.status_code)
    print(response.text)
    if response.status_code == '302':
        print('OK')
'''

def third():
    s = requests.session()
    url = 'http://www.heibanke.com/lesson/crawler_ex02/'
    login_url = 'http://www.heibanke.com/accounts/login/?next=/lesson/crawler_ex02/'
    #csrf = s.get(login_url).headers['Set-Cookie'].split(';')[0].split('=')[1]
    csrf = s.get(login_url).cookies['csrftoken']
    data = {
        'username': 'test',
        'password': 'test123',
        'csrfmiddlewaretoken': csrf
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'www.heibanke.com',
        'Origin': 'http://www.heibanke.com',
        'Referer': 'http://www.heibanke.com/accounts/login/?next=/lesson/crawler_ex02/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'
    }
    response = s.post(login_url, data=data, headers=headers)
    passwd = 0
    data['username'] = 'asd'
    while True:
        csrf = s.get(url).cookies['csrftoken']
        print(passwd)
        data['csrfmiddlewaretoken'] = csrf
        data['password'] = str(passwd)
        response = s.post(url, data=data, headers=headers)
        print(response.text)
        if '您输入的密码错误, 请重新输入' not in response.text:
            print('The correct password is: ', passwd)
            break
        else:
            print(passwd,' is not correct!')
            passwd += 1
    return passwd



if __name__ == '__main__':
    start = time.time()
    #result = first('http://www.heibanke.com/lesson/crawler_ex00/')
    #result = second('http://www.heibanke.com/lesson/crawler_ex01/')
    result = third()
    print(result)
    print('持续时间：', time.time() - start)