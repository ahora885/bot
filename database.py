from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///bot.db")

Base = declarative_base()

Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    telegram_id = Column(Integer, unique=True)

    username = Column(String)

    first_name = Column(String)

    wallet = Column(Integer, default=0)

    welcome_bonus = Column(Boolean, default=False)

    free_test_count = Column(Integer, default=0)

    configs = Column(Integer, default=0)


Base.metadata.create_all(engine)