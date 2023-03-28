from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://darth:123456pos@postgresserver/ChatApp"
Database_Connection_Creater = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=Database_Connection_Creater
)
Base_Model_Mapper = declarative_base()
