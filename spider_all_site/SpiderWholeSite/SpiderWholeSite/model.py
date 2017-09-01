from sqlalchemy import Column, String, Integer, Text, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import DB_SEETING, DOMAIN

Base = declarative_base()


def init_db():
    Base.metadata.create_all(engine)


def drop_db():
    Base.metadata.drop_all(engine)


class SpiderItem(Base):
    __tablename__ = DOMAIN
    id = Column(Integer, primary_key=True)
    title = Column(String(256), default='', nullable=False)
    link = Column(String(256), default='', nullable=False, unique=True)
    publish_date = Column(String(64), default='', nullable=False)
    author = Column(String(100), default='', nullable=False)
    structure = Column(String(100), default='', nullable=False)
    text = Column(Text, default='', nullable=False)
    attachment = Column(Text, default='', nullable=False)


# 初始化数据库连接:
engine = create_engine(DB_SEETING)
# engine = create_engine('mysql+pymysql://root:cbj@localhost:3306/spider_item?charset=utf8')
Session = sessionmaker(bind=engine)

from contextlib import contextmanager

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()



if __name__ == "__main__":
    init_db()
    # drop_db()
