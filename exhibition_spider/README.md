# 基本功能
爬取数据，并对数据进行去重操作
***
# 代码目录结构
```
.
├── log         # 日志目录，程序每次运行会在该目录产生一个日志文件
├── main.py     # 启动函数
├── main_spider.py  # 爬虫主函数
├── requiremetns.txt
├── spiders     # 爬虫模块
│   ├── get_3158.py
│   ├── get_77huiyi.py
│   ├── get_bandenghui.py
│   ├── get_chemsoc.py
│   ├── get_cnean_jieqing.py
│   ├── get_cnean.py
│   ├── get_csp.py
│   ├── get_dxy.py
│   ├── get_eshow.py
│   ├── get_expochina.py
│   ├── get_expowindow.py
│   ├── get_fairso.py
│   ├── get_foodmate.py
│   ├── get_haozhanhui.py
│   ├── get_huodongjia.py
│   ├── get_huodongshu.py
│   ├── get_hys.py
│   ├── get_medmeeting.py
│   ├── get_meeting163.py
│   ├── get_onezh.py
│   ├── get_qq_play.py
│   ├── get_qq_sports.py
│   ├── get_science_meeting.py
│   ├── get_sciencenet.py
│   ├── get_sina_finance.py
│   ├── get_zhankoo.py
│   └── __init__.py
└── tools       # 工具模块
    ├── config.py               # 配置mysq，日志路径
    ├── db_operator.py          # 数据库的一系列操作
    ├── get_address.py          # 从高德地图获取标准地名
    ├── __init__.py             
    └── logger_encapsulation.py # 日志模块的简单封装
```
# 数据库结构
### 1. 正式数据库
- **eventlist**
经过处理的所有展会数据的集合
### 2. 临时数据库
- **eventlist_current**
本次爬取的全部数据
- **eventlist_last**
上个月爬取的全部数据
- **eventlist_unique**
本次爬取的全部数据经过两次去重后留下的数据
- **eventlist_official_temp**
对正式库中eventlist表的备份


***
# 程序流程
- 整体流程图
```flow
st=>start: Start
e=>end: End
op1=>operation: pre_spider
op2=>operation: spider_start
op3=>operation: post_spider
st->op1->op2->op3
op3->e
```
- pre_spider
 1. 清空临时库中eventlist_official_temp，把正式库中eventlist的数据导入到eventlist_official_temp
 2. 把临时库中eventlist_current的数据导入eventlist_last，清空eventlist_current
 3. 清空临时库中eventlist_unique

- spider
爬取展会数据，存入eventlist_current中

- post_spider
 1. 删除eventlist_current中的过期数据
 2. 全匹配去重
对**eventlist_current**中每条数据根据**开始日期**，**城市名**，**展会名**判断该条展会数据是否已存在**eventlist_last**表或**eventlist_official_temp**中，若不存在则插入**eventlist_unique**
**流程图**
```flow
st=>start: Start
e=>end: End
io1=>inputoutput: eventlist_current
io2=>inputoutput: 一条展会数据
io3=>inputoutput: 展会开始日期，城市，展会名
io4=>inputoutput: eventlist_unique
cond1=>condition: eventlist_current空?
cond2=>condition: 已存在eventlist_last中?
cond3=>condition: 已存在eventlist_official_temp中?
cond4=>condition: 爬取成功??
cond5=>condition: ids_remain空?
op1=>operation: 在eventlist_last中查找
op2=>operation: 在eventlist_official_temp中查找
op3=>operation: insert
st->io1->cond1
cond1(no)->io2->io3->op1->cond2
cond2(no)->op2->cond3
cond3(no)->op3->io4
cond1(yes)->e
```
3. 分词后去重
从**eventlist_unique**中取出一条数据A，对A进行分词，去除地点，日期等信息，只保留关键字段，然后在**eventlist_official_temp**中查找与A同一天同一个城市的数据集合B，对B中的每条数据采取同样的分词处理，最后比较B中是否有数据和A相同，如果有则删除A，没有则把A插入**eventlist_official_temp**中
```flow
st=>start: Start
e=>end: End
io1=>inputoutput: eventlist_unique
io2=>inputoutput: 一条展会数据
io3=>inputoutput: 关键字段
io4=>inputoutput: eventlist_official_temp
cond1=>condition: eventlist_unique空?
cond2=>condition: 已存在eventlist_official_temp中?
op1=>operation: 分词处理
op2=>operation: 在eventlist_official_temp中查找
op3=>operation: insert
op4=>operation: delete
st->io1->cond1
cond1(no)->io2->op1->io3->op2->cond2
cond2(no)->op3->io4
cond2(yes)->op4
cond1(yes)->e
```
 