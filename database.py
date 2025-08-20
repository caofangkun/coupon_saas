from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base # 引入Base，用于创建表

DATABASE_URL = "sqlite:///./coupon_saas.db" # 本地SQLite文件

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 用于创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine)
