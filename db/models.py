from sqlalchemy import Column, Integer, String, Enum, Date, create_engine
from sqlalchemy.orm import declarative_base, Session
import enum, config
from datetime import date

Base = declarative_base()


class Section(enum.Enum):
    programming = 1
    history = 2
    war = 3
    music = 4
    movies = 5
    entertainment = 6
    education = 7
    other = 8


class ViewedVideos(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True, autoincrement='auto')
    name = Column(String, nullable=False)
    description = Column(String, default='')
    section = Column(Enum(Section), default=Section.other)
    chapter = Column(String, default='')
    author = Column(String, nullable=False)
    link = Column(String, nullable=False)
    rating = Column(Integer, default=1)
    createdAt = Column(Date, default=date.today())

    def __init__(self, name, author, link, **kwargs):
        self.name = name
        self.author = author
        self.link = link
        for k, v in kwargs.items():
            setattr(self, k, v)


def create_db(db):
    engine = create_engine(db, echo=True)
    Base.metadata.create_all(engine)


def add_video(name, author, link, *, db, **kwargs):
    engine = create_engine(db, echo=True)
    session = Session(bind=engine)
    video = ViewedVideos(name, author, link)
    for k,v in kwargs.items():
        setattr(video, k, v)
    session.add(video)
    session.commit()


if __name__ == '__main__':
    create_db(config.DB_TEST)
    add_video('Telegram Bot inline режим', 'Python Hub Studio',
              'https://www.youtube.com/watch?v=Cn0sMvgqf4E&t=71s', db=config.DB_TEST,
              section=Section.programming, chapter='Python, Aiogram')


