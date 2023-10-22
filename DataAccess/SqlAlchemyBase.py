from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

CONNECTION_STRING = "mysql+pymysql://root:123@localhost:3306/xandra_dbo"
engine = create_engine(CONNECTION_STRING, pool_size=5)
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
