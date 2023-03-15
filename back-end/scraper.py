# from geopy.geocoders import Nominatim
import re
from os import getenv
from time import time
from requests import get
from datetime import datetime
from bs4 import BeautifulSoup
from geopy import GoogleV3
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, func, text, Column, Integer, String, Boolean, DateTime

load_dotenv()

# Create a SQLAlchemy base
Base = declarative_base()


# Create the stocked_lakes_table class
class StockedLakes(Base):
  __tablename__ = 'stocked_lakes_table'
  id = Column(Integer, primary_key=True)
  lake = Column(String)
  stocked_fish = Column(Integer)
  date = Column(DateTime)
  latitude = Column(String)
  longitude = Column(String)
  directions = Column(String)
  derby_participant = Column(Boolean)


# Create the derby_lakes_table class
class DerbyLake(Base):
  __tablename__ = 'derby_lakes_table'
  id = Column(Integer, primary_key=True)
  lake = Column(String)


class DataBase:
  def __init__(self):
    # Load Database
    if getenv("SQLALCHEMY_DATABASE_URI"):
      self.engine = create_engine(getenv("SQLALCHEMY_DATABASE_URI"))
    else:
      self.engine = create_engine('sqlite:///')

    self.conn = self.engine.connect()
    self.Session = sessionmaker(bind=self.engine)
    self.session = self.Session()

    # self.stocked_lakes = self.conn.execute(text("SELECT * FROM stocked_lakes_table")).fetchall()
    # print(self.stocked_lakes)
    # self.derby_lakes = self.conn.execute(text("SELECT * FROM derby_lakes_table")).fetchall()
    # self.total_stocked_by_date = self.session.query(
    #   StockedLakes.date,
    #   func.sum(StockedLakes.stocked_fish)
    # ).group_by('date').order_by('date').all()

  def get_data(self):
    stocked_lakes = self.conn.execute(text("SELECT * FROM stocked_lakes_table")).fetchall()
    derby_lakes = self.conn.execute(text("SELECT * FROM derby_lakes_table")).fetchall()
    total_stocked_by_date = self.session.query(
      StockedLakes.date,
      func.sum(StockedLakes.stocked_fish)
    ).group_by(StockedLakes.date).order_by(StockedLakes.date).all()
    return {"stocked_lakes": stocked_lakes, "derby_lakes": derby_lakes, "total_stocked_by_date": total_stocked_by_date}

  def write_data(self):
    scraper = Scraper()
    Base.metadata.drop_all(self.engine)  # TODO: Remove in production
    Base.metadata.create_all(self.engine)  # TODO: Remove in production
    self.write_derby_data(scraper)
    self.write_lake_data(scraper)
    self.session.commit()
    self.session.close()

  def write_derby_data(self, scraper):
    derby_lakes = scraper.derby_lake_names
    for lake in derby_lakes:
      for item in scraper.df:
        if lake.capitalize() in item['lake'].capitalize():
          item['derby_participant'] = True
          self.session.add(DerbyLake(lake=lake))

  def write_lake_data(self, scraper):
    for lake_data in scraper.df:
      # check if entry already exists in the table
      existing_lake = self.session.query(StockedLakes).filter_by(lake=lake_data['lake'],
                                                                 stocked_fish=lake_data['stocked_fish'],
                                                                 date=lake_data['date']).first()
      if existing_lake:
        continue  # skip if the lake already exists in the table

      # add the lake to the table if it doesn't exist
      lake = StockedLakes(lake=lake_data['lake'], stocked_fish=lake_data['stocked_fish'], date=lake_data['date'],
                          latitude=lake_data['latitude'], longitude=lake_data['longitude'],
                          directions=lake_data['directions'], derby_participant=lake_data['derby_participant'])

      self.session.add(lake)


class Scraper:
  """
  ************************* Scrape data to render the map from *************************

  Need: Lake names, stock count, date stocked, derby participant, and lat/lon
  Steps:
  1. Scrape the data from wdfw.wa.gov
  2. Use Geolocator to get lat/lon
  3. Make the data into a list of dictionaries
  """

  def __init__(self):
    self.lake_url = "https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/all?lake_stocked=&county=&species=&hatchery=&region=&items_per_page=250"
    self.response = get(self.lake_url)
    if self.response.status_code != 200:
      print("Error fetching page")
      exit()
    self.soup = BeautifulSoup(self.response.content, "html.parser")
    self.lake_names = self.scrape_lake_names()
    self.stock_counts = self.scrape_stock_count()
    self.dates = self.scrape_date()
    self.df = self.make_df()
    self.derby_lake_names = self.scrape_derby_names()

  def scrape_lake_names(self):
    ABBREVIATIONS = {
      "LK": "Lake",
      "PD": "Pond",
      "CR": "Creek",
      "PRK": "Park",
      "CO": "County"
    }

    found_text = self.soup.select('.views-field-lake-stocked')

    # Clean up the names
    text_list = [re.sub(r"\(.*?\)|[^\w\s\d]|(?<!\w)(\d+)(?!\w)|\b(" + "|".join(ABBREVIATIONS.keys()) + r")\b",
                        lambda match: "" if match.group(1) else ABBREVIATIONS.get(match.group(2), ""),
                        i.text.strip() + " County").strip().replace("\n", "").replace(" Region ", '').replace("  ",
                                                                                                              " ").title()
                 for i in found_text]
    return text_list[1:]

  # return list of Stock Counts
  def scrape_stock_count(self):
    found_stock_counts = self.soup.findAll(class_="views-field views-field-num-fish")

    stock_count_text_list = [i.text.strip().replace(',', '') for i in found_stock_counts]

    stock_count_int_list = []
    for i in stock_count_text_list:
      try:
        stock_count_int_list.append(int(i))
      except ValueError:
        stock_count_int_list.append(i)
        print(f"Error: {i} is not a valid number")
        continue

    return stock_count_int_list[1:]

  # Return list of Scraped Dates
  def scrape_date(self):
    date_text = self.soup.findAll(class_="views-field views-field-stock-date")

    date_text_list = [i.text.strip() for i in date_text]

    date_list = []
    for i in date_text_list:
      try:
        date_list.append(datetime.strptime(i, '%b %d, %Y') or datetime.strptime(i, '%b %dd, %Y'))
      except ValueError:
        date_list.append(i)
        print(f"Error: {i} is not a valid number")
        continue

    return date_list[1:]

  def make_df(self):
    lake_names = self.lake_names
    stock_count = self.stock_counts
    dates = self.dates
    amount_scraped = len(lake_names)

    # Create a list of dictionaries
    data = []
    for i in range(amount_scraped - 1):
      data.append(
        {'lake': lake_names[i], 'stocked_fish': stock_count[i], 'date': dates[i], 'latitude': "", 'longitude': "",
         'directions': "", "derby_participant": False})

    data = self.get_lat_lon(data)  # ? side effect

    return data

  # Get the latitude and longitude of the lake names and update the df
  @staticmethod
  def get_lat_lon(data):
    locator = GoogleV3(api_key=getenv('GV3_API_KEY'))

    for i in range(len(data)):
      lake = data[i]['lake']
      if lake:
        geocode = locator.geocode(lake + ' washington state')
        if geocode:
          data[i]['latitude'] = geocode.point[0]
          data[i]['longitude'] = geocode.point[1]
          data[i]['directions'] = f"https://www.google.com/maps/search/?api=1&query={lake}"
        else:
          data[i]['latitude'] = ''
          data[i]['longitude'] = ''
          data[i]['directions'] = f"https://www.google.com/maps/search/?api=1&query={lake}"
    # print(data)
    return data

  # Get the names of lakes that are in the state trout derby
  def scrape_derby_names(self):
    url_string = "https://wdfw.wa.gov/fishing/contests/trout-derby/lakes"

    # Reassign response and soup to new url
    self.response = get(url_string)
    self.soup = BeautifulSoup(self.response.content, "html.parser")

    # Scrape Names
    text_list = []
    found_text = self.soup.find("div", {"class": "derby-lakes-list"}).findAll("ul", recursive=False)

    for i in found_text:
      text_list.append(i.find("li").text)

    # Clean up Names
    text_lst_trimmed = []
    for i in text_list:
      text_lst_trimmed.append(i.replace("\n", ""))
    text_lst_trimmed = [re.sub(r"\(.*?\)", '', text).title() for text in text_lst_trimmed]
    return text_lst_trimmed


# Run Once Every morning on Heroku Scheduler
if __name__ == "__main__":
  start_time = time()

  data_base = DataBase()
  # Scraper()
  data_base.write_data()

  end_time = time()
  print(f"It took {end_time - start_time:.2f} seconds to compute")
