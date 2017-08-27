import logging
import time

host = '127.0.0.1'
current_date = time.strftime('%Y%m',time.localtime(time.time()))

db_temp_config = {
    'host': host,
    'user':  "root",
    'passwd': "thanku",
    'db': "hq_exhi_data_month",
    'port': 12307,
    'charset': "utf8"
}

db_official_config = {
    'host': host,
    'user':  "root",
    'passwd': "thanku",
    'db': "hq_exhibitions",
    'port': 12307,
    'charset': "utf8"
}

logger_config = {
    'level': logging.INFO,
    'format': '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    'datefmt': '%a, %d %b %Y %H:%M:%S',
    'filename': 'log/{}.log'.format(current_date),
    'filemode': 'w'
}
