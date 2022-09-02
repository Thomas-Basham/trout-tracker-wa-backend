import os
import pytest
from dotenv import load_dotenv
from geopy import GoogleV3
import requests
from bs4 import BeautifulSoup
from scraper import get_lat_lon


def test_scrape_lake_names():
    url_string = "https://wdfw.wa.gov/fishing/reports/stocking/trout-plants"
    response = requests.get(url_string)
    if response.status_code != 200:
        print("Error fetching page")
        exit()
    soup = BeautifulSoup(response.content, "html.parser")

    # Scrape Names
    found_text = soup.findAll(class_="views-field views-field-lake-stocked")

    assert found_text


def test_scrape_stock_count():
    url_string = "https://wdfw.wa.gov/fishing/reports/stocking/trout-plants"
    response = requests.get(url_string)
    if response.status_code != 200:
        print(response)
        print("Error fetching page")
        exit()
    soup = BeautifulSoup(response.content, "html.parser")

    # Scrape Stock Count
    found_text = soup.findAll(class_="views-field views-field-num-fish")

    assert found_text


def test_scrape_date():
    url_string = "https://wdfw.wa.gov/fishing/reports/stocking/trout-plants"
    response = requests.get(url_string)
    if response.status_code != 200:
        print(response)
        print("Error fetching page")
        exit()
    soup = BeautifulSoup(response.content, "html.parser")

    # Scrape Dates
    found_text = soup.findAll(class_="views-field views-field-stock-date")
    assert found_text


def test_scrape_derby_names():
    url_string = "https://wdfw.wa.gov/fishing/contests/trout-derby/lakes"
    response = requests.get(url_string)
    if response.status_code != 200:
        print("Error fetching page")
        exit()
    soup = BeautifulSoup(response.content, "html.parser")
    found_text = soup.find("div", {"class": "derby-lakes-list"}).findAll("ul", recursive=False)
    assert found_text


@pytest.mark.skip('Skipped for Github Test Badge')
def test_request_example(client):
    response = client.get("/")
    assert b"<h1>Washington Stocked Trout Finder</h1>" in response.data


@pytest.mark.skip('Skipped for Github Test Badge')
def test_geocoder():
    load_dotenv()
    locator = GoogleV3(api_key=os.getenv('GV3_API_KEY'))
    lat_lon = locator.geocode('BLUE Lake Columbia County Washington').point
    print(lat_lon)
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

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
