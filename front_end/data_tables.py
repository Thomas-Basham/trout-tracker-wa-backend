from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Date, Float, func

# Create a SQLAlchemy base
Base = declarative_base()


# Create the stocked_lakes_table class
class StockedLakes(Base):
  __tablename__ = 'stocked_lakes_table'
  id = Column(Integer, primary_key=True)
  lake = Column(String)
  stocked_fish = Column(Integer)
  species = Column(String)
  weight = Column(Float)
  hatchery = Column(String)
  date = Column(Date)
  latitude = Column(Float)
  longitude = Column(Float)
  directions = Column(String)
  derby_participant = Column(Boolean)


# Create the derby_lakes_table class
class DerbyLake(Base):
  __tablename__ = 'derby_lakes_table'
  id = Column(Integer, primary_key=True)
  lake = Column(String)


# Create the derby_lakes_table class
class Utility(Base):
  __tablename__ = 'utility_table'
  id = Column(Integer, primary_key=True)
  updated = Column(Date)
