import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster, Fullscreen

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import sys
import logging

load_dotenv()

app = Flask(__name__)
app.app_context().push()
# ************** Postgres Database **************
# If database in .env exists, use that,
if os.getenv("SQLALCHEMY_DATABASE_URI"):
  engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")

# else use sqlite database
if not os.getenv("SQLALCHEMY_DATABASE_URI"):
  app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
  engine = create_engine('sqlite://')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@app.route('/')
def index_view():
  with engine.connect().execution_options(autocommit=True) as conn:
    stocked_lakes_df = pd.read_sql(f"""SELECT * FROM stocked_lakes_table """, con=conn)
    derby_df = pd.read_sql(f"""SELECT * FROM derby_lakes_table """, con=conn)

  folium_map = make_map(stocked_lakes_df)._repr_html_()

  derby_lakes = set(derby_df['Lake'])

  most_recent_stocked = stocked_lakes_df.drop(["latitude", "longitude", "Directions", "index"], axis=1)
  most_recent_stocked = most_recent_stocked.to_html(index=False, classes='table ')

  return render_template('index.html', folium_map=folium_map,
                         derby_lakes=derby_lakes, most_recent_stocked=most_recent_stocked)


@app.route('/fullscreen')
def map_full_screen_view():
  with engine.connect().execution_options(autocommit=True) as conn:
    stocked_lakes_df = pd.read_sql(f"""SELECT * FROM stocked_lakes_table """, con=conn)

  folium_map = make_map(stocked_lakes_df)._repr_html_()
  return render_template('map_full_screen.html', folium_map=folium_map)


# *********************** DRIVER FOR MAP DATA **********************************
# Make the Map with Folium
def make_map(df):
  # https://towardsdatascience.com/pythons-geocoding-convert-a-list-of-addresses-into-a-map-f522ef513fd6

  # import the library and its Marker clusterization service
  folium_map = folium.Map(width="100%", max_width="100%", max_height="100%",
                          location=df[["latitude", "longitude"]].mean().to_list(),
                          zoom_start=7)

  # if the points are too close to each other, cluster them, create a cluster overlay with MarkerCluster, add to map
  marker_cluster = MarkerCluster().add_to(folium_map)
  Fullscreen(
    position='topright',
    title='Expand me',
    title_cancel='Exit me',
    force_separate_button=True
  ).add_to(folium_map)

  # draw the markers and assign popup and hover texts
  # add the markers to the cluster layers so that they are automatically clustered
  for i, r in df.iterrows():

    html = f'''
        <h3 >{r["Lake"].title()}<h3/>
        <p style="color:red">Date Stocked: {r["Date"]}</p>
        <p style="color:green">Stocked Amount: {r["Stocked Fish"]}<p/>
        <a style="color:blue" href="{r["Directions"]}" target="_blank">Directions via Googlemaps <a/>
        '''

    popup = folium.Popup(html, max_width=400)

    location = (r["latitude"], r["longitude"])

    # red icon for derby lake participant
    if r["Derby Participant"] == "true":
      folium.Marker(location=location, tooltip=r["Lake"].capitalize(), popup=popup,
                    icon=folium.Icon(color='red', icon='trophy', prefix='fa')).add_to(
        folium_map)

    # blue icon for all other lakes
    else:
      folium.Marker(location=location, tooltip=r["Lake"].capitalize(), popup=popup,
                    icon=folium.Icon(color='blue', icon='info', prefix='fa')).add_to(
        marker_cluster)

  folium.raster_layers.TileLayer('Stamen Terrain').add_to(folium_map)
  folium.LayerControl().add_to(folium_map)

  return folium_map


app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

if __name__ == '__main__':
  db.create_all()
  app.run(debug=False)
