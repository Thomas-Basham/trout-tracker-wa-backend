import os
import pytest
from dotenv import load_dotenv
from geopy import GoogleV3
from back_end.scraper import Scraper

scraper = Scraper(
  lake_url="https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/all?lake_stocked=&county=&species=&hatchery=&region=&items_per_page=250")


def test_scrape_lake_names():
  assert len(scraper.lake_names) > 20 and type(scraper.lake_names) == list


def test_scrape_stock_count():
  assert len(scraper.stock_counts) > 20 and type(scraper.stock_counts) == list


def test_scrape_date():
  assert len(scraper.dates) > 20 and type(scraper.dates) == list


def test_scrape_derby_names():
  assert type(scraper.derby_lake_names) == list


def test_geocoder():
  load_dotenv()
  locator = GoogleV3(api_key=os.getenv('GV3_API_KEY'))
  lat_lon = locator.geocode('BLUE Lake Columbia County Washington').point
  assert lat_lon == (46.2775138, -117.814262, 0.0)
