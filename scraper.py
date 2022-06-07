import requests
import time
from bs4 import BeautifulSoup
import numpy as np
from geopy import GoogleV3
import re
import pandas as pd
import dotenv
from geopy.geocoders import Nominatim
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from main import app
import os
# Scrape https://wdfw.wa.gov/fishing/reports/stocking/trout-plants
engine = create_engine(os.environ.get("SQLALCHEMY_DATABASE_URI"))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
db.create_all()


# return list of lake names
def scrape_lake_names():
    url_string = "https://wdfw.wa.gov/fishing/reports/stocking/trout-plants"
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
    url_string = "https://wdfw.wa.gov/fishing/reports/stocking/trout-plants"
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

#
# Return list of Scraped Dates
def scrape_date():
    url_string = "https://wdfw.wa.gov/fishing/reports/stocking/trout-plants"
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


# Make a Dataframe from scraped data
def make_df():
    # Get lake names, Stock Count, And Dates
    lakes = scrape_lake_names()

    amount_scraped = len(lakes)

    lakes = lakes[1:amount_scraped]

    stock_count = scrape_stock_count()
    stock_count = stock_count[1:amount_scraped]

    dates = scrape_date()
    dates = dates[1:amount_scraped]

    # Make a Dataframe with empty lat & lon collumns
    df = pd.DataFrame(
        {'Lake': lakes,
         'Stocked Fish': stock_count,
         'Date': dates
         })

    df["latitude"] = ""
    df["longitude"] = ""
    df["Directions"] = ""

    return df


# Driver Function
# Find Lat Lon's from lake names
# Update dataframe with the Lat Lon's
def get_lat_lon():
    df = make_df()

    # Use locator to get lat and lon of lake names
    # Google is preffered, Nominatim for backup
    #     locator = Nominatim(user_agent="your_app_name")
    locator = GoogleV3(api_key=os.environ.get('GV3_API_KEY'))
    # locator = GoogleV3(api_key=os.getenv('API_KEY'))

    for ind in df.index:
        if df['Lake'][ind]:
            if locator.geocode(df['Lake'][ind]):
                # Nominatim
                #                   df.loc[ind, ['latitude']] = [locator.geocode(df['Lake'][ind]).latitude]
                #                   df.loc[ind, ['longitude']] = [locator.geocode(df['Lake'][ind]).longitude]

                # GoogleV3
                df.loc[ind, ['latitude']] = [locator.geocode(df['Lake'][ind]).point[0]]
                df.loc[ind, ['longitude']] = [locator.geocode(df['Lake'][ind]).point[1]]

                df.loc[ind, ['Directions']] = [f"https://www.google.com/maps/search/?api=1&query={df['Lake'][ind]}"]

                # Account for errors.
            # TODO: make a list of nan to display lakes not on map
            else:
                df.loc[ind, ['latitude']] = [np.nan]
                df.loc[ind, ['longitude']] = [np.nan]
            #                 https://www.google.com/maps/search/?api=1&query=pizza+seattle+wa

    # Make a CSV File for testing purposes
    # TODO Remove this upon deployment

    df.to_sql('stocked_lakes_table', engine, if_exists='replace')

    print(df.dropna())
    return df.dropna()

# TODO Make another table for derby participants from scraped names
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
    print(text_lst_trimmed)
    return text_lst_trimmed


# DRIVER
if __name__ == "__main__":
    get_lat_lon()
