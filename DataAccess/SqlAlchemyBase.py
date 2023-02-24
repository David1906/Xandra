from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

CONNECTION_STRING = "mysql+pymysql://root:@localhost/xandra_dbo"
engine = create_engine(CONNECTION_STRING, pool_size=10)
Session = sessionmaker(bind=engine)
Base = declarative_base()
