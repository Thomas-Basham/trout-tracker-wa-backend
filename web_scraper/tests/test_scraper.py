import os
from dotenv import load_dotenv
from geopy import GoogleV3
from web_scraper.scraper import Scraper

scraper = Scraper(
  lake_url="https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/all?lake_stocked=&county=&species=&hatchery=&region=&items_per_page=250"
)


def test_scrape_lake_names():
  data = scraper.lake_names
  assert len(data) > 20 and type(data) == list and type(data[0] == str)


def test_scrape_stock_counts():
  data = scraper.stock_counts
  assert len(data) > 20 and type(data) == list and type(data[0] == int)


def test_scrape_dates():
  data = scraper.dates
  assert len(data) > 20 and type(data) == list and type(data[0] == object)


def test_scrape_hatcheries():
  data = scraper.hatcheries
  assert len(data) > 20 and type(data) == list and type(data[0] == str)


def test_scrape_weights():
  data = scraper.weights
  assert len(data) > 20 and type(data) == list and type(data[0] == float)


def test_geocoder():
  load_dotenv()
  locator = GoogleV3(api_key=os.getenv('GV3_API_KEY'))
  lat_lon = locator.geocode('BLUE Lake Columbia County Washington').point
  assert lat_lon == (46.2775138, -117.814262, 0.0)
