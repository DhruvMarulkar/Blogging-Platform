from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase , sessionmaker



sqlalchemy_database_url = "sqlite:///./blog.db"

engine = create_engine(
   sqlalchemy_database_url,
   connect_args={"check_same_thread":False} 
)
Sessionlocal = sessionmaker(autoflush=False,bind=engine)

class base(DeclarativeBase):
    pass

def get_db():
    with Sessionlocal() as db:
        yield db