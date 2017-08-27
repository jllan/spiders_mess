#_*_ coding:utf-8 _*_

from main_spider import GetExhibitions
from tools.db_operator import DataOperator
from tools.logger_encapsulation import Logger

logger = Logger()


class Main:
    def __init__(self):
        pass

    '''
        爬虫启动前的操作:
        1. 清空临时库中eventlist_official，把正式库中的数据导入到临时表eventlist_official
        2. 把临时库中eventlist_current的数据导入eventlist_last，清空eventlist_current
        3. 清空临时库中eventlist_unique
    '''
    def pre_spider(self):
        logger.info('爬虫开始前的操作')
        data_operator = DataOperator()
        data_operator.truncate_table('eventlist_official_temp')
        data_operator.from_official_to_temp_official()
        data_operator.truncate_table('eventlist_last')
        data_operator.from_current_to_last()
        data_operator.truncate_table('eventlist_current')
        data_operator.truncate_table('eventlist_unique')
        data_operator.mysql_close()

    '''启动爬虫'''
    def spider_start(self):
        logger.info('爬虫开始')
        GetExhibitions().start()
        #GetExhibitions(self.current_date).start_multi_thread()

    '''
        爬虫结束后的操作:
        1. 删除过期数据
        2. 格式化城市名
    '''
    def post_spider(self):
        logger.info('爬虫结束后的操作')
        data_operator = DataOperator()
        data_operator.delete_data_dated()
        data_operator.data_unique()
        data_operator.deduplication()
        data_operator.mysql_close()


if __name__ == '__main__':
    main = Main()
    # main.pre_spider()
    main.spider_start()
    main.post_spider()

