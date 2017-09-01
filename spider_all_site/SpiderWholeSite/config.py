from tld import get_tld

HOST = 'http://jlan.me'
DOMAIN = get_tld(HOST)
TARGET_DIR = '/home/jlan/spider/whole_site_spider/result/'
DB_SEETING = 'mysql+pymysql://username:passwd@127.0.0.1:3306/db?charset=utf8'
