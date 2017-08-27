from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()
# 初始化数据库连接:
'''
# default
engine = create_engine('mysql://scott:tiger@localhost/foo')

# mysql-python
engine = create_engine('mysql+mysqldb://scott:tiger@localhost/foo')

# MySQL-connector-python
engine = create_engine('mysql+mysqlconnector://scott:tiger@localhost/foo')

# OurSQL
engine = create_engine('mysql+oursql://scott:tiger@localhost/foo')
'''

# engine = create_engine('mysql+mysqlconnector://root:cbj@localhost:3306/seed_info?charset=utf8')
engine = create_engine("postgresql+psycopg2://postgres:njau@192.168.116.59:5432/postgres", client_encoding='utf8')
# 创建DBSession类型:
RiceSession = sessionmaker(bind=engine)

def initDB():
    Base.metadata.create_all(engine)

def dropDB():
    Base.metadata.drop_all(engine)

class Rice(Base):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    __tablename__ = 'cgris_rice'

    id = Column(Integer, primary_key=True)
    库编号 = Column(String(64))
    统一编号 = Column(String(64), unique=True)
    品种名称 = Column(String(64))
    译名 = Column(String(64))
    科名 = Column(String(64))
    属名 = Column(String(64))
    学名 = Column(String(64))
    高程 = Column(String(64))
    东经 = Column(String(64))
    北纬 = Column(String(64))
    种子来源 = Column(String(64))
    原产地 = Column(String(64))
    保存单位 = Column(String(64))
    单位编号 = Column(String(64))
    选育单位 = Column(String(64))
    方法及组合 = Column(String(64))
    籼粳 = Column(String(64))
    早中晚 = Column(String(64))
    水陆 = Column(String(64))
    粘糯 = Column(String(64))
    米色 = Column(String(64))
    米香 = Column(String(64))
    芒长 = Column(String(64))
    粒形状 = Column(String(64))
    粒长度 = Column(String(64))
    长宽比 = Column(String(64))
    颖尖色 = Column(String(64))
    颖壳色 = Column(String(64))
    颖毛有无 = Column(String(64))
    护颖长短 = Column(String(64))
    颖尖弯直 = Column(String(64))
    株高 = Column(String(64))
    出穗期 = Column(String(64))
    糙米率 = Column(String(64))
    精米率 = Column(String(64))
    垩白率 = Column(String(64))
    蛋白质 = Column(String(64))
    赖氨酸 = Column(String(64))
    总淀粉 = Column(String(64))
    直链淀粉 = Column(String(64))
    支链淀粉 = Column(String(64))
    糊化温度 = Column(String(64))
    胶稠度 = Column(String(64))
    苗瘟 = Column(String(64))
    白叶枯 = Column(String(64))
    纹枯病 = Column(String(64))
    褐稻虱 = Column(String(64))
    白背飞虱 = Column(String(64))
    芽期耐寒 = Column(String(64))
    苗期耐旱 = Column(String(64))
    耐盐 = Column(String(64))
    省 = Column(String(64))
    样品类型 = Column(String(64))
    备注 = Column(String(64))
    保存单位_2 = Column(String(64))


if __name__ == "__main__":
    initDB()
    #dropDB()
