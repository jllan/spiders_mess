from sqlalchemy import Column, String, Integer, Text, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import DB_SEETING, HOST
from tld import get_tld

Base = declarative_base()


def init_db():
    Base.metadata.create_all(engine)


def drop_db():
    Base.metadata.drop_all(engine)


class Item(Base):
    '''创建一个以域名为名称的表'''
    __tablename__ = get_tld(HOST)
    id = Column(Integer, primary_key=True)
    title = Column(String(256), default='', nullable=False)
    link = Column(String(256), default='', nullable=False, unique=True)
    publish_date = Column(String(64), default='', nullable=False)
    author = Column(String(100), default='', nullable=False)
    structure = Column(String(100), default='', nullable=False)
    text = Column(Text, default='', nullable=False)
    attachment = Column(Text, default='', nullable=False)


# 初始化数据库连接:
# engine = create_engine('mysql+mysqlconnector://root:cbj@192.168.3.126:3306/huazhu')
engine = create_engine(DB_SEETING)
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
