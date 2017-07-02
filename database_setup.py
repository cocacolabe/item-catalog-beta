import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Shelter(Base):
    __tablename__ = 'shelter'
    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    address = Column(String(250))
    city = Column(String(80))
    state = Column(String(20))
    zipCode = Column(String(5))
    website = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
        'id': self.id,
        'name':self.name,
        'address':self.address,
        'city':self.city,
        'state':self.state,
        'zipcode':self.zipCode,
        'website':self.website
        }
    
class Puppy(Base):
    __tablename__ = 'puppy'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    gender = Column(String(6), nullable = False)
    dateOfBirth = Column(Date)
    picture = Column(String)
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    shelter = relationship(Shelter)
    weight = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

# Add serialize function to be able to send Json object
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name':self.name,
            'gender':self.gender,
            'dateOfBirth':self.dateOfBirth,
            'picture':self.picture
        }

engine = create_engine('sqlite:///petshelterwithuser.db')
 

Base.metadata.create_all(engine)