# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import requests
from config import TARGET_DIR, DOMAIN
from .model import SpiderItem, Session, init_db
from .items import AttachmentItem


from contextlib import contextmanager

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        print('插入失败', e)
        session.rollback()
        raise
    finally:
        session.close()



class SpiderwholesitePipeline(object):
    def __init__(self):
        init_db()
        self.target_dir = os.path.join(TARGET_DIR, DOMAIN)
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)

    def process_item(self, item, spider):
        if isinstance(item, AttachmentItem):
            '''保存附件，附件名是附件链接的标题名'''
            filename = item['title']
            link = item['link']
            file_type = link.split('.')[-1]
            if filename.split('.')[-1] != file_type:
                filename = filename + '.' + file_type
            r = requests.get(link, stream=True)
            if r:
                attachment_name = os.path.join(self.target_dir, filename)
                with open(attachment_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
        else:
            '''保存数据到数据库'''
            sql_item = SpiderItem()
            sql_item.title = item['title']
            sql_item.link = item['link']
            sql_item.text = item['text']
            sql_item.attachment = item.get('attachment')
            sql_item.structure = item.get('structure')
            with session_scope() as session:
                session.add(sql_item)
            # session = Session()
            # try:
            #     session.add(sql_item)
            #     session.commit()
            # except Exception as e:
            #     print('插入失败', e)
            #     session.rollback()
            # else:
            #     print('插入成功')
            # session.close()