import requests
import time
from bs4 import BeautifulSoup
from geopy import GoogleV3
import re
from dotenv import load_dotenv
# from geopy.geocoders import Nominatim
from main import app
import os

load_dotenv()
#
# from sqlalchemy import create_engine, Column, Integer, String, Date
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, Date, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a SQLAlchemy base
Base = declarative_base()


# Create the stocked_lakes_table class
class StockedLakes(Base):
  __tablename__ = 'stocked_lakes_table'
  id = Column(Integer, primary_key=True)
  lake = Column(String)
  stocked_fish = Column(String)
  date = Column(String)
  latitude = Column(String)
  longitude = Column(String)
  directions = Column(String)
  derby_participant = Column(Boolean)


class DerbyLake(Base):
  __tablename__ = 'derby_lakes_table'
  id = Column(Integer, primary_key=True)
  lake = Column(String)


# Load Database
if os.getenv("SQLALCHEMY_DATABASE_URI"):
  engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
else:
  app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
  engine = create_engine('sqlite:///')

# Start a session
Session = sessionmaker(bind=engine)
session = Session()

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

"""
************************* Scrape data to render the map from ************************* 

Need: Lake names, stock count, date stocked, derby participant, and lat/lon
Steps: 
1. Scrape the data from wdfw.wa.gov/
2. Use Geolocator to get lat/lon
3. Make the data into a Pandas Dataframe
4. Save Pandas Dataframe to Postgres Database 

"""


# Scrape https://wdfw.wa.gov/fishing/reports/stocking/trout-plants
# return list of lake names
def scrape_lake_names():
  url_string = "https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/all"
  response = requests.get(url_string)
  if response.status_code != 200:
    print("Error fetching page")
    exit()
  soup = BeautifulSoup(response.content, "html.parser")

  # Scrape Names
  found_text = soup.findAll(class_="views-field views-field-lake-stocked")

  text_list = []
  for i in found_text:
    text_list.append(i.text + " County, Washington")

  # Clean up Names
  text_lst_trimmed = []
  for i in text_list:
    text_lst_trimmed.append(i.replace("\n", "").replace("- Region", ''))
  text_lst_trimmed = [re.sub(r"\(.*?\)", '', text) for text in text_lst_trimmed]
  text_lst_trimmed = [re.sub(r'[^\w\s]', '', text) for text in text_lst_trimmed]
  text_lst_trimmed = [re.sub(r"\d", '', text) for text in text_lst_trimmed]
  text_lst_trimmed = [re.sub(r"\bLK\b", 'Lake', text) for text in text_lst_trimmed]
  text_lst_trimmed = [re.sub(r"\bPD\b", 'Pond', text) for text in text_lst_trimmed]
  text_lst_trimmed = [re.sub(r"\bCR\b", 'Creek', text) for text in text_lst_trimmed]
  text_lst_trimmed = [re.sub(r"\bPRK\b", 'Park', text) for text in text_lst_trimmed]
  text_lst_trimmed = [re.sub(r"\bCO\b", 'County', text) for text in text_lst_trimmed]
  text_lst_trimmed = [" ".join(text.split()) for text in text_lst_trimmed]

  time.sleep(1)
  return text_lst_trimmed


# return list of Stock Counts
def scrape_stock_count():
  url_string = "https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/all"
  response = requests.get(url_string)
  if response.status_code != 200:
    print(response)
    print("Error fetching page")
    exit()
  soup = BeautifulSoup(response.content, "html.parser")

  # Scrape Stock Count
  found_text = soup.findAll(class_="views-field views-field-num-fish")

  text_list = []
  for i in found_text:
    text_list.append(i.text)
    time.sleep(1)

  text_list = [i.strip() for i in text_list]
  return text_list


# Return list of Scraped Dates
def scrape_date():
  url_string = "https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/all"
  response = requests.get(url_string)
  if response.status_code != 200:
    print(response)
    print("Error fetching page")
    exit()
  soup = BeautifulSoup(response.content, "html.parser")

  # Scrape Dates
  found_text = soup.findAll(class_="views-field views-field-stock-date")

  text_list = []
  for i in found_text:
    text_list.append(i.text)
    time.sleep(1)

  text_list = [i.strip() for i in text_list]
  return text_list


def make_df():
  lakes = scrape_lake_names()
  amount_scraped = len(lakes)
  lakes = lakes[1:amount_scraped]

  stock_count = scrape_stock_count()
  stock_count = stock_count[1:amount_scraped]

  dates = scrape_date()
  dates = dates[1:amount_scraped]

  # Create a list of dictionaries
  data = []
  for i in range(amount_scraped - 1):
    data.append({'lake': lakes[i], 'stocked_fish': stock_count[i], 'date': dates[i], 'latitude': "", 'longitude': "",
                 'directions': ""})

  return data


# Get the names of lakes that are in the state trout derby
# Helper function for below code
def scrape_derby_names():
  url_string = "https://wdfw.wa.gov/fishing/contests/trout-derby/lakes"
  response = requests.get(url_string)
  if response.status_code != 200:
    print("Error fetching page")
    exit()
  soup = BeautifulSoup(response.content, "html.parser")
  #     UL -> LI -> a
  # Scrape Names
  #     found_text = soup.findAll( class_="derby-lakes-list")
  text_list = []
  found_text = soup.find("div", {"class": "derby-lakes-list"}).findAll("ul", recursive=False)

  for i in found_text:
    text_list.append(i.find("li").text)

  # Clean up Names
  text_lst_trimmed = []
  for i in text_list:
    text_lst_trimmed.append(i.replace("\n", ""))
  text_lst_trimmed = [re.sub(r"\(.*?\)", '', text) for text in text_lst_trimmed]
  print(text_lst_trimmed)
  return text_lst_trimmed


def write_derby_participants(data):
  # Iterate through the data and add it to the database
  derby_lakes_on_map = []
  derby_lakes = scrape_derby_names()
  for lake in derby_lakes:
    for item in data:
      if lake.capitalize() in item['lake'].capitalize():
        item['derby_participant'] = True
        derby_lakes_on_map.append(lake)
        session.add(StockedLakes(**item))
  for lake in derby_lakes_on_map:
    session.add(DerbyLake(lake=lake))
  session.commit()
  session.close()


def get_lat_lon():
  data = make_df()

  locator = GoogleV3(api_key=os.getenv('GV3_API_KEY'))

  for i in range(len(data)):
    if data[i]['lake']:
      geocode = locator.geocode(data[i]['lake'])
      if geocode:
        data[i]['latitude'] = geocode.point[0]
        data[i]['longitude'] = geocode.point[1]
        data[i]['directions'] = f"https://www.google.com/maps/search/?api=1&query={data[i]['lake']}"
      else:
        data[i]['latitude'] = None
        data[i]['longitude'] = None
        data[i]['directions'] = f"https://www.google.com/maps/search/?api=1&query={data[i]['lake']}"

  write_derby_participants(data)
  for lake_data in data:
    lake = StockedLakes(lake=lake_data['lake'], stocked_fish=lake_data['stocked_fish'], date=lake_data['date'],
                        latitude=lake_data['latitude'], longitude=lake_data['longitude'],
                        directions=lake_data['directions'])
    session.add(lake)
    session.commit()
    # engine.execute(lake.insert())

  return data


# Run Once Every morning on Heroku Scheduler
if __name__ == "__main__":
  Base.metadata.drop_all(engine)
  Base.metadata.create_all(bind=engine)
  get_lat_lon()
