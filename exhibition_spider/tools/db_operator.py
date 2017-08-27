#_*_ coding:utf-8 _*_
import time
import jieba.analyse
import MySQLdb
from get_address import GetAddress
from logger_encapsulation import Logger
from config import current_date, host, db_official_config, db_temp_config
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

logger = Logger()

class DataOperator:

    def __init__(self):
        self.table_current = 'eventlist_current'
        self.table_last = 'eventlist_last'
        self.table_official_temp = 'eventlist_official_temp'
        self.table_official = 'eventlist'
        self.table_unique = 'eventlist_unique'
        self.table_history = 'eventlist_history'
        self.current_date = current_date
        self.host = host
        self.conn_temp = MySQLdb.connect(**db_temp_config)
        self.conn_official = MySQLdb.connect (**db_official_config)

    def item_insert(self, data=None, data_history=None, *args, **kw):
        cursor = self.conn_temp.cursor ()
        cursor.execute("SELECT VERSION()")
        row = cursor.fetchone ()
        print "MySQL server version:", row[0]
        if data_history:
            for i in data_history:
                sid = i['sid']
                itemid = i['itemid']
                history_itemid = i['history_itemid']
                title = i['title']
                venue = i['venue']
                date = i['date']
                area = i['area']
                query_sql = 'SELECT * FROM  %s where Sid="%s" and Itemid="%s"'%(self.table_history, sid, itemid)
                result_query = cursor.execute(query_sql)
                if result_query:
                    print u'数据已存在，不进行插入'
                else:
                    print u'数据不存在，准备插入'
                    insert_sql = 'INSERT INTO '+self.table_history+' (Sid,Itemid,HistoryItemID,ExpoName,UnitName,ExpoDate,ExpoArea,GetDate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
                    try:
                        cursor.execute(insert_sql, (sid,itemid,history_itemid,title,venue,date,area,self.current_date))
                    except Exception as e:
                        print '来源于sid为%s的网站且其itemid为%s的数据插入失败:%s'%(sid, itemid, e)
                    else:
                        self.conn_temp.commit()
                        print u'插入成功'
        for i in data:
            sid = i['sid']
            itemid = i['id']
            title = i['title'].replace('"', '').strip()
            begin_date = i['begin_date'].strip()
            end_date = i['end_date'].strip()
            city = i['city'].strip().rstrip('市')
            venue = i['venue'].strip()
            industry = i['industry']
            organizer = i['organizer']
            site = i['site']
            visitor = i['visitor'].rstrip('人')
            area = i['area']
            history_info_tag = i['history_info_tag']
            print itemid, title, begin_date, end_date, city, venue, industry, organizer, area, history_info_tag
            query_sql = 'SELECT * FROM %s where ExpoName="%s" and CityName="%s" and StartDate="%s"'%(self.table_current, title, city, begin_date)
            print query_sql
            result_query = cursor.execute(query_sql)
            if result_query:
                print '数据已存在，不进行插入'
            else:
                print '数据不存在，准备插入'
                insert_sql = 'INSERT INTO '+self.table_current+'(Itemid,Sid,ExpoName,UnitName,CityName,StartDate,EndDate,Industry,OrganizerName,Site,Visitor,ExpoArea,HistoryInfoTag) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                try:
                    cursor.execute(insert_sql, (itemid,sid,title,venue,city,begin_date,end_date,industry,organizer,site,visitor,area,history_info_tag))
                except Exception as e:
                    print '来源于sid为%s的网站且其itemid为%s的数据插入失败:%s'%(sid, itemid, e)
                else:
                    self.conn_temp.commit()
                    print u'插入成功'
        cursor.close ()
        self.conn_temp.commit()
        self.conn_temp.close ()

    def delete_data_dated(self):
        logger.info('删除过期数据')
        cursor = self.conn_temp.cursor()
        dated = self.current_date[:4]+'-'+self.current_date[-2:]
        cursor.execute('delete from eventlist_current where StartDate<"%s"'%dated)

    '''
    功能：简单数据去重（根据展会名字，开始日期，城市名）
    方法：1从eventlist_current中检索每条数据
         2根据(ExpoName、StartDate、CityName)从eventlist_last所有数据表中检索该条数据，
          若不存在，则在entevent_official数据表中继续检索，
          若仍不存在，则把该条数据写入eventlist_unique表中
    '''
    def data_unique(self):
        logger.info('全匹配数据去重')
        cursor = self.conn_temp.cursor ()
        cursor.execute ("SELECT * FROM %s"%self.table_current)
        rows = cursor.fetchall()
        num_total = cursor.rowcount
        print "%s共有%s行数据" % (self.table_current, num_total)
        num_last, num_official, num_unique = 0, 0, 0
        for row in rows:
            itemid = row[1]
            name = row[5]
            city = row[9]
            begin_date = row[11]
            query_sql_by_last = 'SELECT * FROM %s where ExpoName="%s" and StartDate="%s"'%(self.table_last, name, begin_date)
            result_by_last = cursor.execute(query_sql_by_last)
            if result_by_last:
                num_last += 1
            else:
                query_sql_by_official = 'SELECT * FROM %s where ExpoName="%s" and StartDate="%s"'%(self.table_official_temp, name, begin_date)
                print query_sql_by_official
                result_by_official = cursor.execute(query_sql_by_official)
                if result_by_official:
                    num_official += 1
                else:
                    insert_sql = 'INSERT INTO '+self.table_unique+' (Itemid,HashName,Sid,State,ExpoName,UnitCode,UnitName,UnitNameEn,CityCode,CityName,StartDate,EndDate,Industry,OrganizerName,CoorganizerName,Site,Exhibitor,Visitor,BusinessMan,Mobile,Tel,Qq,Weixin,Email,Fax,Addr,ExpoArea,HistoryInfoTag) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                    result_insert = cursor.execute(insert_sql, row[1:])
                    if result_insert:
                        num_unique += 1
        print "%s共有%s条数据,其中与上月数据重复的有%s条，与正式数据表重复的有%s条，简单去重后的数据有%s条" % (self.table_current, num_total, num_last, num_official, num_unique)
        logger.info("%s共有%s条数据,其中与上月数据重复的有%s条，与正式数据表重复的有%s条，简单去重后的数据有%s条" % (self.table_current, num_total, num_last, num_official, num_unique))
        self.conn_temp.commit()
        cursor.close ()


    '''
    功能：数据去重（根据展会名字，开始日期，城市名）
    方法：1从eventlist_unique数据表X=[a,b,c....]中取出a，对a进行分词并只保留特定词性，删除无用词，得到brief_a
            2从eventlist_official中检索a所对应的(StartDate、CityName)的所有数据，得到Y=[A,B,C...]
                取出A，对A进行同样的分词处理，得到brief_A
                if brief_a<=brief_A or brief_a>=brief_A:
                    a和A是同一条信息
                    从X中删除a
                    跳出循环2
                else:
                    a和A不是同一条信息
                    把a写入eventlist_official中
    '''
    def deduplication(self):
        logger.info('分词后数据去重')
        start = time.time()
        num_del, num_insert, num_same, num_empty = 0, 0, 0, 0
        useless_words = [u'会',u'会议',u'大会',u'展览会',u'博览会',u'博会',u'展会',u'展览',u'展',u'世博',u'世博威',u'国际',u'国家',u'中国',u'全国',u'产业']  #展会名中意义不大的名词
        cursor = self.conn_temp.cursor()
        cursor.execute ("SELECT ID,Itemid,Sid,ExpoName,UnitName,CityName,StartDate,EndDate,Industry,OrganizerName,Site,Exhibitor,Visitor,ExpoArea,HistoryInfoTag FROM "+self.table_unique)
        rows_eventlist = cursor.fetchall()
        num_total = cursor.rowcount
        print "共有%s行数据" % num_total
        for row_eventlist in rows_eventlist:
            has_same = False
            print row_eventlist[3], row_eventlist[5], row_eventlist[6]  #展会名，城市，开始日期
            brief_name = jieba.analyse.extract_tags(row_eventlist[3], allowPOS=['a','n','nz','nr','vn','v','j','l'])    #对展会名进行分词，然后只保留特定的词性，包括名词，动词等
            brief_name = set(brief_name) - set(useless_words)   #除去意义不大的名词
            print ' '.join(brief_name)
            if brief_name:  #分词并只保留指定词性后，若结果为空，则不再继续查找
                cursor.execute ("SELECT ExpoName FROM %s where StartDate='%s' and CityName='%s'"%(self.table_official_temp, row_eventlist[6], row_eventlist[5]))
                rows_official = cursor.fetchall()
                print "在正式表中找到与'%s'同时同地进行的展会共有%s个" %(row_eventlist[3], cursor.rowcount)
                for row_official in rows_official:
                    print row_official[0]
                    brief_name_official = jieba.analyse.extract_tags(row_official[0], allowPOS=['a','n','nz','nr','vn','v','j','l'])
                    brief_name_official = set(brief_name_official) - set(useless_words)
                    print ' '.join(brief_name_official)
                    if brief_name_official and (brief_name.issubset(brief_name_official) or brief_name_official.issubset(brief_name)):
                        with open('same.txt', 'a+') as f:
                            f.write(row_eventlist[3]+'\n'+row_official[0]+'\n............................................................\n')
                        f.close()
                        del_sql = 'delete from %s where ID="%s"' %(self.table_unique, row_eventlist[0])
                        cursor.execute(del_sql)
                        self.conn_temp.commit()
                        num_del += 1
                        num_same += 1
                        has_same = True
                        break   #若在to_table中找到相同数据，则跳出本次循环，直接跳到'if not has_same:'处
            else:
                num_empty += 1  #empty_num用来记录分词并只保留指定词性后，剩余为空的数据量
            if not has_same:
                insert_sql = 'INSERT INTO '+self.table_official_temp+' (Itemid,Sid,ExpoName,UnitName,CityName,StartDate,EndDate,Industry,OrganizerName,Site,Exhibitor,Visitor,ExpoArea,HistoryInfoTag) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                cursor.execute(insert_sql, row_eventlist[1:])
                self.conn_temp.commit()
                num_insert += 1
        print '共查询了%s条数据，其中有%s条数据重复，总用时%s'%(num_total, num_same, time.time()-start)
        print '从%s中删除了%s条数据，向%s中插入了%s条数据'%(self.table_unique, num_del, self.table_official_temp, num_insert)
        logger.info('共查询了%s条数据，其中有%s条数据重复'%(num_total, num_same))
        logger.info('从%s中删除了%s条数据，向%s中插入了%s条数据'%(self.table_unique, num_del, self.table_official_temp, num_insert))
        cursor.close()
        self.conn_temp.commit()

    def create_table(self):
        cursor = self.conn_temp.cursor ()
        create_last_sql = 'CREATE TABLE %s LIKE eventlist_201607'%('eventlist_last')
        cursor.execute(create_last_sql)


    '''从高德地图获取精确的场馆名'''
    def venue_format(self):
        address = GetAddress()
        cursor = self.conn_temp.cursor()
        cursor.execute ("SELECT ID,ExpoName,UnitName,CityName FROM %s WHERE length(UnitName)>9" %self.table_unique)
        rows_eventlist = cursor.fetchall()
        events_num = cursor.rowcount
        num = 1
        m, n = 0, 0
        for row_eventlist in rows_eventlist:
            id = row_eventlist[0]
            event = row_eventlist[1]
            venue = row_eventlist[2]
            city = row_eventlist[3]
            print venue, city
            data = address.get_address(venue, city)
            if data:
                print event, venue, city, data[0], data[1], data[2], data[3], data[4], data[5], data[6], num
                if venue.strip(' ') != data[0].strip(' '):
                    update_sql = 'UPDATE %s set UnitName="%s" where ID="%s"'%(self.table_unique, data[0], id)
                    print update_sql
                    result_query = cursor.execute(update_sql)
                    if result_query:
                        print '设置成功'
                        m += 1
                    else:
                        print '设置出错'
                        n += 1
                else:
                    print 'venue相同，不需要设置'
            else:
                print '未找到%s的数据'%venue
            num += 1
        print '共有%s条数据,修改成功%s条，失败%s条'%(events_num, m, n)
        cursor.close()
        self.conn_temp.commit()
        # self.conn_temp.close()

    def venue_format_exhibitionlist(self):
        address = GetAddress()
        from_table = 'exhibitionlist'
        cursor = self.conn_temp.cursor()
        cursor.execute ("SELECT ID,UnitName,CityName,Address FROM %s WHERE Address=''" %from_table)
        rows_venue = cursor.fetchall()
        venues_num = cursor.rowcount
        num = 1
        m, n = 0, 0
        for row_venue in rows_venue:
            id = row_venue[0]
            venue = row_venue[1]
            city = row_venue[2]
            add = row_venue[3]
            print venue, city
            data = address.get_address(venue, city)
            if data:
                print venue, city, add, data[0], data[1], data[2], data[3], data[4], data[5], data[6], num
                #if venue.strip(' ') != data[0].strip(' '):
                update_sql = 'UPDATE {1} set Address="{0[1]}",Lon="{0[2]}",Lat="{0[3]}",Tel="{0[4]}",Seat="{0[5]}",Zone="{0[6]}" where ID="{2}"'.format(data, from_table, id)
                print update_sql
                result_query = cursor.execute(update_sql)
                if result_query:
                    print '设置成功'
                    m += 1
                    self.conn_temp.commit()
                else:
                    print '设置出错'
                    n += 1
                '''else:
                    print 'venue相同，不需要设置'''''
            else:
                print '未找到%s的数据'%venue
            num += 1
        print '共有%s条数据,修改成功%s条，失败%s条'%(venues_num, m, n)
        cursor.close()
        self.conn_temp.commit()
        # self.conn_temp.close()

    # 把正式库中的eventlist导入临时库中eventlist_official_temp中
    def from_official_to_temp_official(self):
        logger.info('把正式库中的eventlist导入临时库中eventlist_official_temp中')
        m, n = 0, 0
        cursor_temp = self.conn_temp.cursor ()
        cursor_official = self.conn_official.cursor ()
        cursor_official.execute ("SELECT * FROM %s"%self.table_official)
        rows_official = cursor_official.fetchall()
        print "共有%s行数据" % cursor_official.rowcount
        for row in rows_official:
            name = row[5]
            city = row[10]
            itemid = row[1]
            begin_date = row[11]
            print name, city, itemid, begin_date
            insert_sql = 'INSERT INTO '+self.table_official_temp+' (Itemid,HashName,Sid,State,ExpoName,UnitCode,UnitName,UnitNameEn,CityCode,CityName,StartDate,EndDate,Industry,OrganizerName,CoorganizerName,Site,Exhibitor,Visitor,BusinessMan,Mobile,Tel,Qq,Weixin,Email,Fax,Addr,ExpoArea) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            print insert_sql
            try:
                result_insert = cursor_temp.execute(insert_sql, row[1:])
                self.conn_temp.commit()
            except Exception, e:
                print '插入失败',e
                n = n + 1
            else:
                if result_insert:
                    print '插入成功'
                    m += 1
                else:
                    print name, begin_date
                    print '插入失败！'
                    n = n + 1
        print '插入成功%s条，失败%s条'%(m, n)
        cursor_official.close()
        cursor_temp.close()
        self.conn_temp.commit()
        # self.conn_official.close()
        return n

    # 把处理过的eventlist_unique导入正式库中eventlist
    def from_temp_unique_to_official(self):
        m, n = 0, 0
        cursor_temp = self.conn_temp.cursor ()
        cursor_official = self.conn_official.cursor ()
        cursor_temp.execute ("SELECT * FROM %s"%self.table_unique)
        rows_temp = cursor_temp.fetchall()
        print "共有%s行数据" % cursor_temp.rowcount
        for row in rows_temp:
            name = row[5]
            city = row[10]
            itemid = row[1]
            begin_date = row[11]
            print name, city, itemid, begin_date
            query_sql = 'SELECT * FROM %s where ExpoName="%s" and CityName="%s" and StartDate="%s"'%(self.table_official, name, city, begin_date)
            print query_sql
            result_query = cursor_official.execute(query_sql)
            if result_query:
                print '数据已存在，不进行插入'
            else:
                print '数据不存在，准备插入'
                insert_sql = 'INSERT INTO '+self.table_official+' (Itemid,HashName,Sid,State,ExpoName,UnitCode,UnitName,UnitNameEn,CityCode,CityName,StartDate,EndDate,Industry,OrganizerName,CoorganizerName,Site,Exhibitor,Visitor,BusinessMan,Mobile,Tel,Qq,Weixin,Email,Fax,Addr,ExpoArea) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                print insert_sql
                try:
                    result_insert = cursor_official.execute(insert_sql, row[1:-2])
                    self.conn_official.commit()
                except Exception, e:
                    print '插入失败',e
                    n = n + 1
                else:
                    if result_insert:
                        print '插入成功'
                        m += 1
                    else:
                        print name, begin_date
                        print '插入失败！'
                        n = n + 1
        print '插入成功%s条，失败%s条'%(m, n)
        cursor_official.close()
        self.conn_official.commit()
        # self.conn_official.close()
        cursor_temp.close()
        # self.conn_temp.close()
        return n

    def from_current_to_last(self):
        logger.info('把eventlist_current导入eventlist_last')
        cursor = self.conn_temp.cursor ()
        cursor.execute('insert into eventlist_last select * from eventlist_current')
        cursor.close()
        self.conn_temp.commit()

    #把eventlist_official_temp表中展会的展馆名称插入到exhibitionlist表中
    def unitname_inserting(self, unit_table, event_table):
        n = 0
        m = 0
        cursor = self.conn_temp.cursor ()
        cursor.execute ("SELECT distinct UnitName, CityName FROM "+event_table+" where UnitCode='' and length(UnitName)>9")
        rows = cursor.fetchall()
        for row in rows:
            print row[0], row[1]
            query_sql = 'SELECT * FROM %s where UnitName="%s"'%(unit_table, row[0])
            print query_sql
            result_query = cursor.execute(query_sql)
            if result_query:
                print '在%s中找到相同数据' %unit_table
            else:
                print '在%s中未找到 '%unit_table+row[0]+'!'
                n = n + 1
                insert_sql = 'INSERT INTO '+ unit_table+'(UnitName,CityName) VALUES(%s,%s)'
                print insert_sql
                result_inserting = cursor.execute(insert_sql, row)
                if result_inserting:
                    print row[0]+'"插入成功"'
                    m += 1
                    unitcode_setting_sql = 'update %s set UnitCode=(ID + 1000) where UnitCode=""'%unit_table
                    unitcode_setting_result = cursor.execute(unitcode_setting_sql)
                    if unitcode_setting_result:
                        print 'UnitCode设置成功'
                else:
                    print row[0]+"插入失败!"
        print '共有%s行数据不存在'%n
        print '共插入%s条数据'%m
        cursor.close()
        self.conn_temp.commit()

    #根据exhibitionlist设置eventlist中展会场馆的UnitCode
    def unit_code_setting(self, unit_table, event_table):
        n = 0
        m = 0
        cursor = self.conn_temp.cursor()
        cursor.execute ("SELECT UnitName, UnitCode, CityName FROM "+event_table+" where UnitCode='' and length(UnitName)>9") #length(UnitName)>9来确保展馆名不是城市名
        rows_eventlist = cursor.fetchall()
        for row_eventlist in rows_eventlist:
            print row_eventlist[0], row_eventlist[1]
            query_sql = 'SELECT * FROM %s where UnitName="%s"'%(unit_table, row_eventlist[0])
            print query_sql
            result_query = cursor.execute(query_sql)
            if result_query:
                print '找到相同数据'
                rows_exhibitionlist = cursor.fetchone()
                print rows_exhibitionlist[2], rows_exhibitionlist[3]
                set_sql = 'update %s set UnitCode="%s" where UnitName="%s"'%(event_table, rows_exhibitionlist[2], row_eventlist[0])
                cursor.execute(set_sql)
                m += 1
            else:
                print '在'+unit_table+'中未找到 "'+row_eventlist[0]+'" !'
                n = n + 1
        print '共有%s行数据不存在'%n
        print '共插入%s条数据'%m
        cursor.close()
        self.conn_temp.commit()

    def truncate_table(self, table_name):
        cursor = self.conn_temp.cursor()
        cursor.execute('truncate %s'%table_name)
        self.conn_temp.commit()
        cursor.close()

    def mysql_close(self):
        self.conn_official.close()
        self.conn_temp.close()


if __name__ == '__main__':
    operator = DataOperator()
    #operator.data_unique()
    #operator.deduplication()
    # operator.venue_format_exhibitionlist()
    operator.from_temp_unique_to_official()