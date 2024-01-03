# from geopy.geocoders import Nominatim
import os
import re
from time import time
from requests import get
from datetime import datetime
from bs4 import BeautifulSoup
from geopy import GoogleV3
from dotenv import load_dotenv


from api.database import DataBase
load_dotenv()


class Scraper:
  """
  ************************* Scrape data to render the map from *************************

  Need: Lake names, stock count, date stocked, derby participant, and lat/lon
  Steps:
  1. Scrape the data from wdfw.wa.gov
  2. Use Geolocator to get lat/lon
  3. Make the data into a list of dictionaries
  """

  def __init__(self, lake_url):
    self.lake_url = lake_url
    self.response = get(self.lake_url)
    if self.response.status_code != 200:
      print("Error fetching page")
      exit()
    self.soup = BeautifulSoup(self.response.content, "html.parser")
    self.lake_names = self.scrape_lake_names()
    self.stock_counts = self.scrape_stock_count()
    self.dates = self.scrape_date()
    self.species = self.scrape_species()
    self.weights = self.scrape_weights()
    self.hatcheries = self.scrape_hatcheries()
    self.derby_lake_names = self.scrape_derby_names()
    self.df = self.make_df()

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

  # return list of Species
  def scrape_species(self):
    found_text = self.soup.findAll(class_="views-field views-field-species")

    species_text_list = [i.text.strip() for i in found_text]

    # print("SPECIES", species_text_list)
    return species_text_list[1:]

  # return list of Weights
  def scrape_weights(self):
    found_text = self.soup.findAll(class_="views-field views-field-fish-per-lb")

    weights_float_list = []
    for i in found_text:
      try:
        weight = float(i.text.strip())
        weights_float_list.append(weight)
      except ValueError:
        # handle the error here, such as skipping the value or setting it to a default value
        print(f"Could not convert {i.text.strip()} to float")
    return weights_float_list

  # return list of Weights
  def scrape_hatcheries(self):
    found_text = self.soup.findAll(class_="views-field views-field-hatchery")

    hatcheries_text_list = [i.text.strip().title() for i in found_text]

    # print("HATCHERIES", hatcheries_text_list)
    return hatcheries_text_list[1:]

  # Return list of Scraped Dates
  def scrape_date(self):
    date_text = self.soup.findAll(class_="views-field views-field-stock-date")

    date_text_list = [i.text.strip() for i in date_text]

    date_list = []
    for i in date_text_list:
      try:
        date_list.append(datetime.strptime(i, '%b %d, %Y').date() or datetime.strptime(i, '%b %dd, %Y').date())
      except ValueError:
        date_list.append(i)
        print(f"Error: {i} is not a valid date")
        continue

    return date_list[1:]

  # Return a list of names of lakes that are in the state trout derby
  def scrape_derby_names(self):

    # The trout derby doesn't start until april 22. don't scrape names unless the derby is running
    Trout_derby_start_date = datetime(2023, 4, 30)
    today = datetime.now()
    if today > Trout_derby_start_date:
      url_string = "https://wdfw.wa.gov/fishing/contests/trout-derby/lakes"

      # Reassign response and soup to new url
      self.response = get(url_string)
      self.soup = BeautifulSoup(self.response.content, "html.parser")

      # Scrape Names
      text_list = []
      found_text = self.soup.find("div", {"class": "derby-lakes-list"})
      if found_text:
        found_text = found_text.findAll("ul", recursive=False)

        for i in found_text:
          text_list.append(i.find("li").text)

        # Clean up Names
        text_lst_trimmed = []
        for i in text_list:
          text_lst_trimmed.append(i.replace("\n", ""))
        text_lst_trimmed = [re.sub(r"\(.*?\)", '', text).title() for text in text_lst_trimmed]
        return text_lst_trimmed
      else:
        # TODO: if there is no derby lakes aka derby isn't running, clear all derby participants from stocked lake table
        return []

  def make_df(self):
    lake_names = self.lake_names
    stock_count = self.stock_counts
    dates = self.dates
    species = self.species
    weights = self.weights
    hatcheries = self.hatcheries
    amount_scraped = len(lake_names)

    # Create a list of dictionaries
    data = []
    for i in range(amount_scraped - 1):
      data.append(
        {'lake': lake_names[i], 'stocked_fish': stock_count[i], 'date': dates[i], 'species': species[i],
         'weight': weights[i], "hatchery": hatcheries[i],
         'latitude': "", 'longitude': "",
         'directions': "", "derby_participant": False})

    data = self.get_lat_lon(data)  # ? side effect

    return data

  # Get the latitude and longitude of the lake names and update the df
  @staticmethod
  def get_lat_lon(data):
    locator = GoogleV3(api_key=os.getenv('GV3_API_KEY'))

    for i in range(len(data)):
      lake = data[i]['lake']
      if lake:
        geocode = locator.geocode(lake + ' washington state')
        if geocode:
          data[i]['latitude'] = float(geocode.point[0])
          data[i]['longitude'] = float(geocode.point[1])
          data[i]['directions'] = f"https://www.google.com/maps/search/?api=1&query={lake}"
        else:
          data[i]['latitude'] = float(0.0)
          data[i]['longitude'] = float(0.0)
          data[i]['directions'] = f"https://www.google.com/maps/search/?api=1&query={lake}"
    # print(data)
    return data


# ran only in a dev environment, used to get all the wdfw trout plant archives
def write_archived_data():
  for i in range(2022, 2015, -1):  # data goes back to 2015
    for j in range(7):  # there are at most 7 pages to scrape
      data_base.write_data(scraper=Scraper(
        lake_url=f'https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/archive/{i}?lake_stocked=&county=&species=&hatchery=&region=&items_per_page=250&page={j}'))
      print(f'updated year {i}, page {j}')


# Run Once Every day
if __name__ == "__main__":
  start_time = time()

  data_base = DataBase()
  scraper = Scraper(
    lake_url="https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/all?lake_stocked=&county=&species=&hatchery=&region=&items_per_page=250"
  )

  data_base.write_data(scraper=scraper)

  if os.getenv('ENVIRONMENT') and os.getenv('ENVIRONMENT') == 'testing':
    data_base.back_up_database()

  end_time = time()
  print(f"It took {end_time - start_time:.2f} seconds to compute")
