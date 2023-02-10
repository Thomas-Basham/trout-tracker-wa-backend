# from geopy.geocoders import Nominatim
import requests
import time
from bs4 import BeautifulSoup
from geopy import GoogleV3
import re
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, Date, String, Boolean, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
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


# Create the derby_lakes_table class
class DerbyLake(Base):
  __tablename__ = 'derby_lakes_table'
  id = Column(Integer, primary_key=True)
  lake = Column(String)


# Load Database
if os.getenv("SQLALCHEMY_DATABASE_URI"):
  engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
else:
  engine = create_engine('sqlite:///')

# Start a session
Session = sessionmaker(bind=engine)
session = Session()


"""
************************* Scrape data to render the map from ************************* 

Need: Lake names, stock count, date stocked, derby participant, and lat/lon
Steps: 
1. Scrape the data from wdfw.wa.gov
2. Use Geolocator to get lat/lon
3. Make the data into a list of dictionaries 
4. Save data to Postgres Database 

"""

lake_url = "https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/all?lake_stocked=&county=&species=&hatchery=&region=&items_per_page=250"
response = requests.get(lake_url)
if response.status_code != 200:
  print("Error fetching page")
  exit()
soup = BeautifulSoup(response.content, "html.parser")


# return list of lake names
def scrape_lake_names():
  found_text = soup.findAll(class_="views-field views-field-lake-stocked")

  text_list = [i.text + " County, Washington" for i in found_text]

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

  return text_lst_trimmed


# return list of Stock Counts
def scrape_stock_count():
  found_stock_counts = soup.findAll(class_="views-field views-field-num-fish")

  found_stock_text_list = [i.text.strip() for i in found_stock_counts]

  return found_stock_text_list


# Return list of Scraped Dates
def scrape_date():
  date_text = soup.findAll(class_="views-field views-field-stock-date")

  date_text_list = [i.text.strip() for i in date_text]

  return date_text_list


# Get the names of lakes that are in the state trout derby
def scrape_derby_names():
  global response, soup
  url_string = "https://wdfw.wa.gov/fishing/contests/trout-derby/lakes"
  response = requests.get(url_string)
  if response.status_code != 200:
    print("Error fetching page")
    exit()
  soup = BeautifulSoup(response.content, "html.parser")

  # Scrape Names
  text_list = []
  found_text = soup.find("div", {"class": "derby-lakes-list"}).findAll("ul", recursive=False)

  for i in found_text:
    text_list.append(i.find("li").text)

  # Clean up Names
  text_lst_trimmed = []
  for i in text_list:
    text_lst_trimmed.append(i.replace("\n", ""))
  text_lst_trimmed = [re.sub(r"\(.*?\)", '', text) for text in text_lst_trimmed]
  return text_lst_trimmed


def get_lat_lon(data):
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

  return data


def write_derby_data(data):
  # Iterate through the data and add it to the database
  derby_lakes_on_map = []
  derby_lakes = scrape_derby_names()
  for lake in derby_lakes:
    for item in data:
      if lake.capitalize() in item['lake'].capitalize():
        item['derby_participant'] = True
        session.add(DerbyLake(lake=lake))
  session.commit()
  return data


def write_lake_data(data):
  for lake_data in data:
    lake = StockedLakes(lake=lake_data['lake'], stocked_fish=lake_data['stocked_fish'], date=lake_data['date'],
                        latitude=lake_data['latitude'], longitude=lake_data['longitude'],
                        directions=lake_data['directions'], derby_participant=lake_data['derby_participant'])
    session.add(lake)
  session.commit()


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
                 'directions': "", "derby_participant": False})
  data = get_lat_lon(data)
  Base.metadata.drop_all(engine)
  Base.metadata.create_all(engine)

  new_data = write_derby_data(data)
  write_lake_data(new_data)
  session.close()



# Run Once Every morning on Heroku Scheduler
if __name__ == "__main__":
  start_time = time.time()

  make_df()

  end_time = time.time()
  print(f"It took {end_time - start_time:.2f} seconds to compute")
