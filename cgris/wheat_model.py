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
WheatSession = sessionmaker(bind=engine)

def initDB():
    Base.metadata.create_all(engine)

def dropDB():
    Base.metadata.drop_all(engine)

class Wheat(Base):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    __tablename__ = 'cgris_wheat'

    id = Column(Integer, primary_key=True)
    库编号 = Column(String(64))
    统一编号 = Column(String(64), unique=True)
    保存单位 = Column(String(64))
    品种名称 = Column(String(64))
    译名 = Column(String(64))
    科名 = Column(String(64))
    属名 = Column(String(64))
    学名 = Column(String(64))
    系谱 = Column(String(64))
    育成年限 = Column(String(64))
    原产地 = Column(String(64))
    高程 = Column(String(64))
    东经 = Column(String(64))
    北纬 = Column(String(64))
    来源国 = Column(String(64))
    芒 = Column(String(64))
    壳色 = Column(String(64))
    粒色 = Column(String(64))
    冬春性 = Column(String(64))
    成熟期 = Column(String(64))
    穗粒数 = Column(String(64))
    穗长 = Column(String(64))
    株高 = Column(String(64))
    千粒重 = Column(String(64))
    粗蛋白 = Column(String(64))
    赖氨酸 = Column(String(64))
    沉淀值 = Column(String(64))
    硬度 = Column(String(64))
    容重 = Column(String(64))
    抗旱性 = Column(String(64))
    耐涝性 = Column(String(64))
    芽期耐盐 = Column(String(64))
    苗期耐盐 = Column(String(64))
    田间抗寒性 = Column(String(64))
    人工抗寒性 = Column(String(64))
    条锈严重度 = Column(String(64))
    条锈反应型 = Column(String(64))
    条锈普遍率 = Column(String(64))
    叶锈严重度 = Column(String(64))
    叶锈反应型 = Column(String(64))
    叶锈普遍率 = Column(String(64))
    秆锈严重度 = Column(String(64))
    秆锈反应型 = Column(String(64))
    秆锈普遍率 = Column(String(64))
    白粉严重度 = Column(String(64))
    白粉反应型 = Column(String(64))
    黄矮病 = Column(String(64))
    赤霉病病穗 = Column(String(64))
    赤霉病病指 = Column(String(64))
    赤霉病指数 = Column(String(64))
    赤霉病抗性 = Column(String(64))
    根腐叶病级 = Column(String(64))
    根腐穗病级 = Column(String(64))
    其它 = Column(String(64))
    省 = Column(String(64))
    样品类型 = Column(String(64))


if __name__ == "__main__":
    initDB()
    # dropDB()
