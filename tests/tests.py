import os
import pytest
from dotenv import load_dotenv
load_dotenv()
from geopy import GoogleV3

from main import app, db


def test_app_exists():
    assert app


def test_geocoder():
    locator = GoogleV3(api_key=os.getenv('GV3_API_KEY'))
    lat_lon = locator.geocode('BLUE Lake Columbia County Washington').point
    print(lat_lon)
    assert lat_lon == (46.2775138, -117.814262, 0.0)


