import requests
import time
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from geopy import GoogleV3
import folium
from folium.plugins import MarkerCluster
import re
from geopy.geocoders import Nominatim

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def render_the_map():
    folium_map = make_map(df=pd.read_csv("templates/Stocked-Lakes(3).csv"))
    folium_map.save('templates/map.html')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)


# Scrape https://wdfw.wa.gov/fishing/reports/stocking/trout-plants

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
    lakes = lakes[1:100]

    stock_count = scrape_stock_count()
    stock_count = stock_count[1:100]

    dates = scrape_date()
    dates = dates[1:100]

    # Make a Dataframe with empty lat & lon collumns
    df = pd.DataFrame(
        {'Lake': lakes,
         'Stocked Fish': stock_count,
         'dates': dates
         })

    df["latitude"] = ""
    df["longitude"] = ""
    df["Directions"] = ""
    return df


# Find Lat Lon's from lake names
# Update dataframe with the Lat Lon's
def get_lat_lon():
    df = make_df()

    # Use locator to get lat and lon of lake names
    # Google is preffered, Nominatim for backup
    #     locator = Nominatim(user_agent="your_app_name")
    locator = GoogleV3(api_key='AIzaSyDzWG8llw5v3g8RHswBvyKlwQH2MeAbsfU')

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
    df.to_csv('Stocked-Lakes.csv')

    print(df.dropna())
    return df.dropna()


# Make the Map with Folium
def make_map(df):
    # https://towardsdatascience.com/pythons-geocoding-convert-a-list-of-addresses-into-a-map-f522ef513fd6

    # import the library and its Marker clusterization service
    m = folium.Map(location=df[["latitude", "longitude"]].mean().to_list(),
                   zoom_start=7)  # if the points are too close to each other, cluster them, create a cluster overlay with MarkerCluster, add to m
    marker_cluster = MarkerCluster().add_to(m)

    # draw the markers and assign popup and hover texts
    # add the markers the the cluster layers so that they are automatically clustered
    for i, r in df.iterrows():
        html = f'''
        <h3 >{r["Lake"].capitalize()}<h3/>
        <a style="color:blue" href="{r["Directions"]}">Directions via Googlemaps <a/>
        <p style="color:green">Stocked Amount: {r["Stocked Fish"]}<p/>
        <p style="color:red">Date Stocked: {r["dates"]}</p>'''

        iframe = folium.IFrame(html, width=300, height=300)
        popup = folium.Popup(iframe, max_width=400)

        location = (r["latitude"], r["longitude"])

        folium.Marker(location=location, tooltip=r["Lake"].capitalize(), popup=popup).add_to(
            marker_cluster)

    return m


# # Driver
# make_map(get_lat_lon())

# Testing
# make_map(df=pd.read_csv("templates/Stocked-Lakes(3).csv"))
