import os
import pytest
from dotenv import load_dotenv
from geopy import GoogleV3
from scraper import Scraper

scraper = Scraper()


def test_scrape_lake_names():
  assert len(scraper.lake_names) > 20 and type(scraper.lake_names) == list


def test_scrape_stock_count():
  assert len(scraper.stock_counts) > 20 and type(scraper.stock_counts) == list


def test_scrape_date():
  assert len(scraper.dates) > 20 and type(scraper.dates) == list


def test_scrape_derby_names():
  assert type(scraper.derby_lake_names) == list


@pytest.mark.skip('Skipped for Github Test Badge')
def test_index_request(client):
  response = client.get("/")
  assert b"<h1>Washington Stocked Trout Finder</h1>" in response.data


# @pytest.mark.skip('Skipped for Github Test Badge')
def test_geocoder():
  load_dotenv()
  locator = GoogleV3(api_key=os.getenv('GV3_API_KEY'))
  lat_lon = locator.geocode('BLUE Lake Columbia County Washington').point
  assert lat_lon == (46.2775138, -117.814262, 0.0)


def create_app():
  from main import app
  app.config['TESTING'] = True
  # Default port is 5000
  app.config['LIVESERVER_PORT'] = 8943
  # Default timeout is 5 seconds
  app.config['LIVESERVER_TIMEOUT'] = 10
  return app


@pytest.fixture()
def app():
  app = create_app()
  app.config.update({
    "TESTING": True,
  })

  # other setup can go here

  yield app


@pytest.fixture()
def client(app):
  return app.test_client()


@pytest.fixture()
def runner(app):
  return app.test_cli_runner()
