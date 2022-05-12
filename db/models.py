from sqlalchemy import Column, Integer, String, Enum, Date
from sqlalchemy.orm import declarative_base
import enum
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
    
    @property
    def rating(self):
        return self.rating

    @rating.setter
    def rating(self, value):
        if not isinstance(value, int) or value not in range(1, 6):
            raise ValueError('Rating must be integer value from 1 to 5')
        self.rating = value
