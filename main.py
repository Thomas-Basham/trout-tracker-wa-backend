import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from geopy import GoogleV3
import folium
from folium.plugins import MarkerCluster# Create a map object and center it to the avarage coordinates to m

from geopy.geocoders import Nominatim

# THIS CAN BE USED, MAYBE IF GOOGLE MAPS FAILS
# geolocator = Nominatim(user_agent="example app")
# print(geolocator.geocode("Snohomish - Region 4").raw)


def scrape_url(url_string):
    response = requests.get(url_string)
    if response.status_code != 200:
        print("Error fetching page")
        exit()
    soup = BeautifulSoup(response.content, "html.parser")

    found_text = soup.findAll(class_="views-field views-field-lake-stocked")

    text_list = []

    for i in found_text:
        text_list.append(i.text)

    time.sleep(1)
    return text_list


def get_lat_lon():
    text = scrape_url('https://wdfw.wa.gov/fishing/reports/stocking/trout-plants')

    geolocator = GoogleV3(api_key='AIzaSyDzWG8llw5v3g8RHswBvyKlwQH2MeAbsfU')

    lat_lon_list = []
    for line in text:
        if line is not None:
            if geolocator.geocode(line):
                lat_lon_list.append(geolocator.geocode(line).point)
    return lat_lon_list


def make_df():
    lat_lon_list = get_lat_lon()
    df = pd.DataFrame(lat_lon_list)
    print(df)
    return df

# TODO get the name of the lakes and pass   popup = r['Name'],
#                                           tooltip=r['Name'])
def make_map(df):
    # https://towardsdatascience.com/pythons-geocoding-convert-a-list-of-addresses-into-a-map-f522ef513fd6
    # import the library and its Marker clusterization service
    m = folium.Map(location=df[[0, 1]].mean().to_list(), zoom_start=2)  # if the points are too close to each other, cluster them, create a cluster overlay with MarkerCluster, add to m
    marker_cluster = MarkerCluster().add_to(m)  # draw the markers and assign popup and hover texts
    # add the markers the the cluster layers so that they are automatically clustered
    for i, r in df.iterrows():
        location = (r[0], r[1])
        folium.Marker(location=location,)\
            .add_to(marker_cluster)  # display the map
    print(m)
    return m


if __name__ == '__main__':
    make_map(make_df())
