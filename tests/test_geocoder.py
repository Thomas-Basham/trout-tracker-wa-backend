import os
import pytest
from dotenv import load_dotenv
from geopy import GoogleV3


def test_app_exists():
    load_dotenv()
    from main import app
    assert app


def test_geocoder():
    load_dotenv()
    locator = GoogleV3(api_key=os.getenv('GV3_API_KEY'))
    lat_lon = locator.geocode('BLUE Lake Columbia County Washington').point
    print(lat_lon)
    assert lat_lon == (46.2775138, -117.814262, 0.0)


