from sqlalchemy.orm import  declarative_base, relationship
from sqlalchemy import  Column, Integer, String, Boolean, Date, Float, TIMESTAMP, ForeignKey

# Create a SQLAlchemy base
Base = declarative_base()

class WaterLocations(Base):
    __tablename__ = 'water_locations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_html_name = Column(String, unique=True)  # what wdfw named
    water_name_cleaned = Column(String)  # the cleaned name after scraping
    latitude = Column(Float)
    longitude = Column(Float)
    directions = Column(String)
    created_at = Column(TIMESTAMP)
    derby_participant = Column(Boolean)
    
# Create the stocked_lakes_table class
class StockedLakes(Base):
    __tablename__ = 'stocked_lakes_table'
    id = Column(Integer, primary_key=True)
    lake = Column(String)  # plans to move to FK
    stocked_fish = Column(Integer)
    species = Column(String)
    weight = Column(Float)
    hatchery = Column(String)
    date = Column(Date)
    latitude = Column(Float)  # plans to move to FK
    longitude = Column(Float)  # plans to move to FK
    directions = Column(String)  # plans to move to FK
    derby_participant = Column(Boolean)  # plans to move to FK
    # Replace raw lat/lng/directions with FK
    water_location_id = Column(Integer, ForeignKey('water_locations.id'))
    water_location = relationship("WaterLocations")

    def to_dict(self):
        return {
            "date": self.date,
            "lake": self.lake,
            "stocked_fish": self.stocked_fish,
            "species": self.species,
            "hatchery": self.hatchery,
            "weight": self.weight,
            "derby_participant": self.derby_participant,
            "latitude": self.water_location.latitude if self.water_location else None,
            "longitude": self.water_location.longitude if self.water_location else None,
            "directions": self.water_location.directions if self.water_location else None,
            "water_location_id": self.water_location_id,
            "water_location": self.water_location
        }

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

