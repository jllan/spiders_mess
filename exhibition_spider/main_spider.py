#_*_ coding:utf-8 _*_
import re
import time
import sys
import datetime
from multiprocessing.dummy import Pool as ThreadPool
sys.path.append('..')
from tools.db_operator import DataOperator
from tools.config import current_date
from tools.logger_encapsulation import Logger
from spiders.get_3158 import Get3158
from spiders.get_cnean import Cnean
from spiders.get_cnean_jieqing import CneanJieqing
from spiders.get_csp import CcpEscience
from spiders.get_dxy import Dxy
from spiders.get_eshow import Eshow
from spiders.get_expochina import ExpoChina
from spiders.get_bandenghui import BanDengHui
from spiders.get_huodongshu import HuoDongShu
from spiders.get_huodongjia import HuoDongJia
from spiders.get_fairso import Fairso
from spiders.get_expowindow import ExpoWindow
from spiders.get_sina_finance import SinaFinance
from spiders.get_foodmate import FoodMate
from spiders.get_hys import Haoyisheng
from spiders.get_haozhanhui import Haozhanhui
from spiders.get_77huiyi import Huiyi77
from spiders.get_medmeeting import MedMeeting
from spiders.get_meeting163 import Meeting163
from spiders.get_onezh import Onezh
from spiders.get_science_meeting import ScienceMeeting
from spiders.get_sciencenet import SciencenetMeeting
from spiders.get_zhankoo import Zhankoo
from spiders.get_chemsoc import Chemsoc
import spiders.get_qq_play as get_qq_play
import spiders.get_qq_sports as get_qq_sports

logger = Logger()

class GetExhibitions:

    def __init__(self):
        self.current_date = current_date

    '''
        在city_list中添加城市（城市的拼音），
        默认开始日期为本月，不需要默认截止日期,程序中会自动判断符合要求的日期
    '''
    def Get3158(self):
        logger.info('3158 start')
        sid = '10'
        city_list = ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'tianjin', 'chongqing',
            'chengdu', 'hangzhou', 'zhengzhou', 'jinan', 'qingdao', 'wuhan', 'xian',
            'nanjing', 'hainan', 'suzhou', 'xiamen', 'dalian', 'shenyang', 'guiyang',
            'kunming', 'fuzhou', 'dongguan', 'yangzhou', 'nanchang', 'hunan',
            'heilongjiang', 'guangxi'
        ]
        get_3158 = Get3158(self.current_date, sid)
        for city in  city_list:
            url = 'http://zhanhui.3158.cn/zhxx/all/trade/%s/'%city
            print city, url
            pages = get_3158.get_pages(url)
            print '%s共%s页'%(city, pages)
            for page in range(1, pages+1):
                get_3158.get_data(page, city)
            print '%s的数据全部抓取并写入完毕'%city
        logger.info('3158 over')


    '''
        城市在city_list中添加（需要看下有效日期大概有几页），
        默认开始日期为本月，不需要默认截止日期,程序中会自动判断符合要求的日期
    '''
    def GetCnean(self):
        logger.info('cnean start')
        sid = '11'
        city_list = {
            '北京' : 3, '上海' : 8, '广州' : 3, '深圳' : 2, '天津' : 1, '重庆' : 1, '杭州' : 1, '成都' : 1,
            '郑州' : 1, '青岛' : 1, '济南' : 1, '武汉' : 1, '南京' : 1, '西安' : 1, '苏州' : 1, '福州' : 1,
            '厦门' : 1, '沈阳' : 1, '大连' : 1, '贵阳' : 1, '昆明' : 1, '东莞' : 1, '哈尔滨': 1, '长沙': 1,
            '南宁': 1, '北海': 1,
        }
        cnean = Cnean(self.current_date, sid)
        for city_name, pages in city_list.iteritems():
            print('%s大约有%s页'%(city_name, pages))
            for page in range(1,int(pages)+1):
                cnean.get_data(page, city_name)
        logger.info('cnean over')


    '''
        城市就在city_list中添加（城市类型和城市代码），
        默认开始日期为本月，截止日期设为'2018/12/31'，需要根据实际情况修改
    '''
    def GetEshow(self):
        logger.info('eshow start')
        start_date =  self.current_date[:4]+'/'+self.current_date[-2:]+'/'+'01'
        end_date = '2018/12/31'
        sid = '13'
        url = 'http://www.eshow365.com/ZhanHui/Ajax/AjaxSearcherV3.aspx'
        city_list = {
            '北京' : ['areano', '1'],
            '天津' : ['areano', '2'],
            '上海' : ['areano', '9'],
            '江苏' : ['areano', '10'],
            '浙江' : ['areano', '11'],
            '广东' : ['areano', '19'],
            '重庆' : ['areano', '22'],
            '广西' : ['areano', '20'] ,
            '海南' : ['areano', '21'] ,        #海南
            '合肥' : ['Drpcity', '98'],
            '成都' : ['Drpcity', '235'],
            '济南' : ['Drpcity', '135'],
            '青岛' : ['Drpcity', '136'],
            '沈阳' : ['Drpcity', '37'],
            '大连' : ['Drpcity', '38'],
            '哈尔滨' : ['Drpcity', '60'],
            '郑州' : ['Drpcity', '152'],
            '长沙' : ['Drpcity', '183'],
            '武汉' : ['Drpcity', '169'],
            '贵阳' : ['Drpcity', '256'],
            '昆明' : ['Drpcity', '265'],
            '福州' : ['Drpcity', '115'],
            '厦门' : ['Drpcity', '116'],
            '南昌' : ['Drpcity', '124'],
            '西安' : ['Drpcity', '288'],
        }
        eshow = Eshow(sid, self.current_date, start_date, end_date)
        for city_name, city_info in city_list.items():
            pages = 1
            for page in range(1, pages+1):
                print('正在爬取%s第%s页'%(city_name, page))
                html = eshow.get_html(url, page, *city_info)
                if html:
                    if page == 1:
                        pattern_pages = re.compile('<option.*?value="1".*?selected=.*?>1/(\d+).*?</option>')
                        pages = re.findall(pattern_pages, html)[0]
                        print '%s共%s页'%(city_name, pages)
                    eshow.get_data(html)
        logger.info('eshow over')


    '''
        城市就在city_list中添加（城市名和城市代码），
        默认开始日期为本月，截止日期设为当年年底，需要根据实际情况修改
    '''
    def GetExpoChina(self):         #截止日期设为当年年底，需要根据实际情况修改
        logger.info('expochina start')
        city_list = {
            '北京' : '1101',
            '上海' : '3101',
            '天津' : '1201',
            '重庆' : '5001',
            '深圳' : '4403',
            '广州' : '4401',
            '珠海' : '4404',
            '东莞' : '4419',
            '南京' : '3201',
            '苏州' : '3202',
            #'徐州' : '3203',
            #'常州' : '3204',
            #'昆山' : '3205',
            '扬州' : '3210',
            '杭州' : '3301',
            #'宁波' : '3302',
            #'温州' : '3303',
            #'义乌' : '3307',
            '济南' : '3701',
            '青岛' : '3702',
            '成都' : '5101',
            '武汉' : '4201',
            '郑州' : '4101',
            '西安' : '6101',
            '海南' : '4600',        #包括海口和三亚
            '贵阳' : '5201',
            '昆明' : '5301',
            '南昌' : '3601',
            '大连' : '2102',
            '哈尔滨': '2301',
            '沈阳' : '2101',
            '厦门' : '3502',
            '福州' : '3501',
            '南宁' : '4501',
            '桂林' : '4503',
            # '北海': ''  # 无数据
            '长沙' : '4301'
        }
        sid = '21'
        begin_time = self.current_date[:4]+'-'+self.current_date[-2:]+'-'+'01'
        end_time = '2017-12-31'
        expo_china = ExpoChina(sid, self.current_date, begin_time, end_time)
        for city_name, city_code in city_list.iteritems():
            expo_china.get_items(city_name, city_code)
        logger.info('expochina over')


    '''
        城市就在city_list中添加（城市名和城市代码），
        默认开始日期为本月，截止日期设为'20181231'，需要根据实际情况修改
    '''
    def GetOnezh(self):         #默认截止日期设为'20181231',需要根据实际情况修改
        logger.info('onezh start')
        city_list = {
            '北京' : '1_0_0',
            '上海' : '21_0_0',
            '广州' : '423_424_0',
            '深圳' : '423_524_0',
            '东莞' : '423_441_0',
            '天津' : '42_0_0',
            '南京' : '1643_1644_0',
            '苏州' : '1643_1692_0',
            '扬州' : '1643_1748_0',
            '杭州' : '3133_3134_0',
            #'宁波' : '3133_3182_0',
            #'温州' : '3133_3218_0',
            #'金华' : '3133_3162_0',
            '济南' : '2182_2183_0',
            '青岛' : '2182_2268_0',
            '重庆' : '62_0_0',
            '成都' : '2589_2590_0',
            '武汉' : '1320_1321_0',
            '郑州' : '998_999_0',
            '西安' : '2471_2472_0',
            '海南' : '788_0_0',        #包括海口和三亚
            '贵阳' : '690_691_0',
            '昆明' : '2987_2988_0',
            '南昌' : '1763_1764_0',
            '大连' : '1874_1912_0',
            '沈阳' : '1874_1875_0',
            '哈尔滨': '1176_1177_0',
            '厦门' : '227_303_0',
            '福州' : '227_228_0',
            '南宁' : '566_567_0',
            '桂林' : '566_617_0',
            '长沙' : '1436_1437_0'
        }
        sid = '18'
        begin_date = self.current_date+'01'
        end_date = '20181231'
        onezh = Onezh(sid, self.current_date)
        for key, value in city_list.iteritems():
            onezh.get_items(key, value, begin_date, end_date)
        logger.info('onezh over')


    '''
        不需要额外参数，爬取所有城市，网站只列出了当天以后的展会，所以不需要限定开始日期
    '''
    def GetHaozhanhui(self):
        logger.info('haozhanhui start')
        sid = '20'
        url = 'http://www.haozhanhui.com/zhanlanjihua/'
        haozhanhui = Haozhanhui(sid, self.current_date)
        data = haozhanhui.get_data(url)
        haozhanhui.get_items(data)
        logger.info('haozhanhui over')


    '''
        爬取所有城市的数据，
        爬取今后三年的数据，程序中会判断有效日期
        地址： http://csp.escience.cn/dct/page/65537/__rpcsp0x2Main!65537%7C0_action/confListMainView?
    '''
    def GetCsp(self):
        logger.info('csp start')
        sid = '19'
        years = [2016, 2017, 2018]      #年份要根据是否有会议及时更新
        csp_escience = CcpEscience(self.current_date, sid)
        for year in years:
            csp_escience.get_items(year)
        logger.info('csp over')


    '''
        爬取对应城市所在的省，
        不需要默认截止日期
        地址: http://meeting.dxy.cn/search.do
    '''
    def GetDxy(self):
        logger.info('dxy start')
        city_list = {
            '北京' : '110000',
            '天津' : '120000',
            '上海' : '310000',
            '重庆' : '500000',
            '广东' : '440000',          #广州深圳东莞
            '浙江' : '330000',          #杭州
            '江苏' : '320000',          #南京苏州扬州
            '山东' : '370000',          #济南青岛
            '四川' : '510000',          #成都
            '湖北' : '420000',          #武汉
            '湖南' : '430000',          #长沙
            '陕西' : '610000',          #西安
            '河南' : '410000',          #郑州
            '福建' : '350000',          #福州厦门
            '贵州' : '520000',          #贵阳
            '云南' : '530000',          #昆明
            '辽宁' : '210000',          #沈阳大连
            '黑龙江' : '230000',        #哈尔滨
            '海南' : '15303',
            '广西' : '450000'
        }
        begin_time = self.current_date[:4]+'-' + self.current_date[-2:]+'-'+'01'
        sid = '19'
        dxy = Dxy(self.current_date, sid)
        for city, city_id in city_list.iteritems():
            time.sleep(1)
            start_url = 'http://meeting.dxy.cn/search.do?keywords=&meetingType=&category_id=&meetingBegin=%s&meetingEnd=&location=%s&tagid=&t=0&pge=1'%(begin_time, city_id)
            dxy.get_items(start_url)

            start_url_2017 = 'http://meeting.dxy.cn/tag/list/loc_%s/y2016/p-1'%(city_id)
            print "正在抓取%s2017的数据"%city
            data_2016 = dxy.get_items(start_url_2017)
            if not data_2016:
                print "%s2016的数据为空"%city
        logger.info('dxy over')


    '''
        爬取所有城市的数据，数据很少
        不需要默认截止日期,循环爬取当年内当月及之后每月的数据，
    '''
    def GetFinanceSina(self):
        logger.info('financesina start')
        sid = '19'
        sina_finance = SinaFinance(sid, self.current_date)
        data = sina_finance.get_data(self.current_date[:4])   #因为只有当年的数据
        for month in range(int(self.current_date[-2:]), 13):       #查找本月及本月以后月份的数据
            sina_finance.get_items(data, month)
        logger.info('financesina over')


    '''
        爬取所有城市的数据，数据较少
        不需要默认截止日期，程序自动判断有效日期
        需要看下有效日期在前几页
        地址：http://member.haoyisheng.com/meet/meet_list.php
    '''
    def GetHaoyisheng(self):
        logger.info('haoyisheng start')
        sid = '19'
        hys = Haoyisheng(sid, self.current_date)
        for page in range(1, 15):       #在前十页的数据中筛选就可以了
            print '抓取第%s页的数据'%page
            hys.get_items(str(page))
        logger.info('haoyisheng over')


    '''
        爬取所有城市的数据，
        不需要默认截止日期，
        有些国外展会信息需要手动删除
        地址：http://www.77huiyi.com/meet/conferlist/?mc=&msi=2016-01-01&msa=&page=1
    '''
    def GetHuiyi77(self):
        logger.info('huiyi77 start')
        sid = '19'
        begin_time = self.current_date[:4]+'-'+self.current_date[-2:]+'-'+'01'
        huiyi77 = Huiyi77(sid, self.current_date)
        huiyi77.get_items(begin_time)
        logger.info('huiyi77 over')


    '''
        爬取所有城市的数据，
        不需要默认截止日期，循环爬取当年当月及之后每月和第二年的数据
        地址：url = 'http://www.medmeeting.org/home/search?&year=%s&month=%s&page=%s'%(year, month, page)
    '''
    def GetMedmeeting(self):
        logger.info('medmeeting start')
        sid = '19'
        med_meeting = MedMeeting(sid, self.current_date)
        for month in range(int(self.current_date[-2:]), 13):
            med_meeting.get_items(self.current_date[:4], str(month))
        med_meeting.get_items(str(int(self.current_date[:4])+1), '') # 爬取下一年的数据
        logger.info('medmeeting over')

    '''
        爬取所有城市的数据，数据很少
        不需要开始和截止日期，分析前十页的数据，自动判断有效日期
        地址：url = 'http://www.meeting163.com/meeting_type.asp?count=%s'%page
    '''
    def GetMeeting163(self):
        logger.info('meeting163 start')
        sid = '19'
        meeting163 = Meeting163(sid, self.current_date)
        for page in range(1, 10):
            meeting163.get_items(page)        #抓取前十页的数据
        logger.info('meeting163 over')


    '''
        爬取所有城市的数据
        不需要开始和截止日期，网站列出来的都是有效数据
        地址：http://www.meeting.edu.cn
    '''
    def GetScienceMeeting(self):
        logger.info('sciencemeeting start')
        sid = '19'
        science_meeting = ScienceMeeting(sid, self.current_date)
        science_meeting.get_items()
        logger.info('sciencemeeting over')

    '''
        爬取所有城市的数据，
        需要开始和截止日期，截止日期设为end_date = '2018-12-31'
        地址：http://meeting.sciencenet.cn/index.php?s=/Category/search_result
    '''
    def GetSciencenetMeeting(self):
        logger.info('sciencenetmeeting start')
        sid = '19'
        begin_date  = self.current_date[:4]+'-'+self.current_date[-2:]+'-'+'01'
        end_date = '2018-12-31'
        sciencenet_meeting = SciencenetMeeting(sid, self.current_date)
        sciencenet_meeting.get_items(begin_date, end_date, '1')
        logger.info('sciencenetmeeting over')

    '''
        爬取所有城市的数据，数据较少
        不需要默认截止日期，循环爬取当年当月及之后每月和第二年的数据
        地址：url = 'http://www.chemsoc.org.cn/Meeting/Home/search.asp?mingcheng=&province=&y=%s&m=%s'%(year, month)
    '''
    def GetChemsoc(self):
        logger.info('chemsoc start')
        sid = '30'
        chemsoc = Chemsoc(sid, self.current_date)
        for month in range(int(self.current_date[-2:]), 13):
            chemsoc.get_items(self.current_date[:4], str(month))
        chemsoc.get_items(str(int(self.current_date[:4])+1), '')
        logger.info('chemsoc over')


    '''
        爬取前100页所有城市的数据
        不需要开始和截止日期，程序中判断有效日期，网站列出来的大多数是有效数据
        地址：url = 'http://www.huodongjia.com/business/page-%s'%page
    '''
    def GetHuodongjia(self):
        logger.info('huodongjia start')
        sid = '31'
        huodongjia = HuoDongJia(sid, self.current_date)
        pages = range(1, 103)   #爬取前100页的数据
        for page in pages:
            huodongjia.getItems(page)
        logger.info('huodongjia over')


    """
        爬取所有城市的数据
        不需要截止日期
        地址： url = 'http://www.foodmate.net/exhibit/search.php?kw=&areaid=0&fromdate=%s&todate=&catid=3900&process=0&x=64&y=14&page=%s'%(start_date, page)
    """
    def GetFoodmate(self):
        logger.info('foodmate start')
        sid = '32'
        start_date = self.current_date+'01'
        food_mate = FoodMate(sid, self.current_date)
        food_mate.get_items(start_date)
        logger.info('foodmate over')


    '''
        爬取所有城市的数据,数据很少
        不需要开始和截止日期，程序自动判断有效日期
        地址：url = 'http://www.cnena.com/jieqing/listall-htm-ordertype-id-page-%s.html'%page
    '''
    def GetCneanJieqing(self):      #不需要额外设置参数，需要关注下有效数据截止到那一页（http://www.cnena.com/jieqing/listall-htm-ordertype-id-page-1.html）
        logger.info('cneanjieqing start')
        sid = '33'
        pages = 2
        cnean_jieqing = CneanJieqing(self.current_date, sid)
        for page in range(1, pages+1):
            cnean_jieqing.get_items(page)    #大多数数据都过期，有效数据只有第一页有几个
        logger.info('cneanjieqing over')


    '''
        爬取城市所在省的数据
        不需要开始和截止日期，网站列出来的都是有效数据
        地址：url = 'http://www.zhankoo.com/Search/SearchExhibitionList?city=%s&classifyId=0&ratingOverAll=0&rankType=5&isExhibitionEnd=0&_=1452759283208&pagenumber=%s'%(city, page)
    '''
    def GetZhankoo(self):
        logger.info('zhankoo start')
        sid = '34'
        city_list = {
            '北京', '上海', '广东', '天津', '重庆', '江苏', '四川', '河南', '山东', '湖北', '陕西', '浙江','福建','辽宁', '贵州', '云南'
        }
        zhankoo = Zhankoo(sid, self.current_date)
        for city in city_list:
            zhankoo.get_items(city)
        logger.info('zhankoo over')


    '''
        爬取所有城市的数据,数据很多,当天之后的数据集中在前50页，本月当天之前的数据集中在后50页
        不需要开始和截止日期，程序自动判断有效日期
        地址：url = 'http://www.bandenghui.com/list/0-0-0-0-0-0.html?&page=%s' %page
    '''
    def GetBandenghui(self):
        logger.info('bandenghui start')
        sid = '35'
        pages = range(10)   #当天之后的数据集中在前50页，本月当天之前的数据集中在后50页
        bandenghui = BanDengHui(sid, self.current_date)
        start = time.time()
        for page in pages:
            bandenghui.getItems(page)
        logger.info('bandenghui over')


    '''
        爬取所有城市的数据
        不需要开始和截止日期，程序自动判断有效日期
        地址：url = 'http://y.qq.com/yanchu'
    '''
    def GetQQPlay(self):
        logger.info('qqplay start')
        sid = '5'
        get_qq_play.get_items(sid, self.current_date)
        logger.info('qqplay over')


    '''
        爬取所有城市的数据
        不需要开始和截止日期，程序自动判断有效日期
        地址：url = 'http://y.qq.com/yanchu/category.html?type=26&city=0&page=1&g_f='
    '''
    def GetQQSports(self):
        logger.info('qqsports start')
        sid = '50'
        get_qq_sports.get_items(sid, self.current_date)
        logger.info('qqsports over')


    def GetExpoWindow(self):
        logger.info('expowindow start')
        sid = '36'
        expowindow = ExpoWindow(sid, self.current_date)
        category = range(1, 20)     #有20个分类
        for cate in category:
            print '正在查找类别为%s的数据'%cate
            expowindow.get_items(cate = str(cate))
        logger.info('expowindow over')

    """
        爬取所有城市的数据
        按月份爬取
        地址：url = 'http://www.huodongshu.com/html/find.html'
    """
    def GetHuoDongShu(self):
        logger.info('huodongshu start')
        sid = '37'
        current_month=int(self.current_date[-2:])
        huodongshu = HuoDongShu(sid, self.current_date)
        months = range(current_month, 13)
        for month in months:
            print '正在查找%s月份的数据'%month
            huodongshu.get_items(month = month)
        logger.info('huodongshu over')

    '''
        爬取所有城市
        自动判断有效日期
        url: 'http://www.fairso.com'
    '''
    def GetFairso(self):
        logger.info('fairso start')
        sid = '38'
        fairso = Fairso(sid, self.current_date)
        fairso.get_items()
        logger.info('fairso over')

    def start(self):
        # self.Get3158()
        # self.GetCnean()
        # self.GetEshow()
        # self.GetExpoChina()
        # self.GetOnezh()
        # self.GetHaozhanhui()
        # self.GetCsp()
        # self.GetDxy()
        # self.GetFinanceSina()
        # self.GetHaoyisheng()
        # self.GetHuiyi77()
        # self.GetMedmeeting()
        # self.GetMeeting163()
        # self.GetScienceMeeting()
        # self.GetSciencenetMeeting()
        # self.GetChemsoc()       #30
        # self.GetFoodmate()     #32
        self.GetCneanJieqing() #33
        # self.GetZhankoo()      #34
        # self.GetBandenghui()   #35
        # self.GetQQPlay()       #5
        # self.GetQQSports()     #50
        # self.GetExpoWindow()   #36
        # self.GetHuoDongShu()   #37
        # self.GetFairso()       #38
        # self.GetHuodongjia()   #31

    def start_multi_thread(self):
        functions = [
            'Get3158',
            'GetCnean',
            'GetEshow',
            'GetExpoChina',
            'GetOnezh',
            'GetHaozhanhui',
            'GetCsp',
            'GetDxy',
            'GetFinanceSina',
            'GetHaoyisheng',
            'GetHuiyi77',
            'GetMedmeeting',
            'GetMeeting163',
            'GetScienceMeeting',
            'GetSciencenetMeeting',
            'GetChemsoc',
            'GetFoodmate',
            'GetCneanJieqing',
            'GetZhankoo',
            'GetBandenghui',
            'GetQQPlay',
            'GetQQSports',
            'GetExpoWindow',
            'GetHuoDongShu',
            'GetFairso',
            'GetHuodongjia'
        ]
        def fun(f):
            # return getattr(get_exhibitions, f)()
            return getattr(self, f)()

        pool = ThreadPool(processes=8)
        # pool.map(lambda f: getattr(get_exhibitions, f)(), functions)
        pool.map(fun, functions)
        pool.close()
        pool.join()

if __name__ == '__main__':
    current_date = raw_input('请输入当前时间（包含年份和月份，如201601）')
    host = '127.0.0.1'
    print current_date

    print('爬虫启动....................')
    get_exhibitions = GetExhibitions(current_date)
    get_exhibitions.start()
    # get_exhibitions.start_multi_thread()
    #数据去重
    # print '简单去重程序'
    # operator.data_unique()
    # print '开始进行正式去重程序'
    # operator.deduplication()