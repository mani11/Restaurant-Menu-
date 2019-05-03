import sys
from sqlalchemy import Column,ForeignKey,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):

    __tablename__ = 'user'

    name = Column(String(120),nullable = False)
    id = Column(Integer,primary_key = True)
    email = Column(String(150),nullable = False)
    picture = Column(String(160))

class Restaurant(Base):

    __tablename__ = 'restaurant'

    name = Column(String(80),nullable = False)
    id = Column(Integer,primary_key = True)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

class MenuItem(Base):

    __tablename__ = 'menu_item'

    name = Column(String(80),nullable = False)
    id = Column(Integer,primary_key = True)
    course = Column(String(80))
    description = Column(String(250))
    price = Column(String(80))
    restaurant_id = Column(Integer,ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)
 

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.create_all(engine)    
