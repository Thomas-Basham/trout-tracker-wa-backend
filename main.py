import os
import folium
from folium.plugins import MarkerCluster, Fullscreen
from flask import Flask, render_template
from sqlalchemy import create_engine
from dotenv import load_dotenv
import sys
import logging

load_dotenv()

app = Flask(__name__.split('.')[0])
app.app_context().push()
# ************** Postgres Database **************
# If database in .env exists, use that,
if os.getenv("SQLALCHEMY_DATABASE_URI"):
  engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
  with engine.connect().execution_options(autocommit=True) as conn:
    stocked_lakes = conn.execute(f"SELECT * FROM stocked_lakes_table").fetchall()
    derby_lakes = conn.execute(f"SELECT * FROM derby_lakes_table").fetchall()
  engine.dispose()

# else use sqlite database
else:
  app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
  engine = create_engine('sqlite://')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route('/')
def index_view():
  folium_map = make_map(stocked_lakes)._repr_html_()

  derby_lakes_set = set(lake["lake"] for lake in derby_lakes)

  return render_template('index.html', folium_map=folium_map,
                         derby_lakes=derby_lakes_set, most_recent_stocked=stocked_lakes)


@app.route('/fullscreen')
def map_full_screen_view():

  folium_map = make_map(stocked_lakes)._repr_html_()
  return render_template('map_full_screen.html', folium_map=folium_map)


# *********************** DRIVER FOR MAP DATA **********************************
# Make the Map with Folium
def make_map(lakes):
  latitudes = [float(lake["latitude"]) for lake in lakes]
  longitudes = [float(lake["longitude"]) for lake in lakes]
  location = [sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)]
  folium_map = folium.Map(width="100%", max_width="100%", max_height="100%", location=location, zoom_start=7)

  marker_cluster = MarkerCluster().add_to(folium_map)
  Fullscreen(
    position='topright',
    title='Expand me',
    title_cancel='Exit me',
    force_separate_button=False
  ).add_to(folium_map)

  for lake in lakes:
    html = f'''
      <h3 >{lake["lake"].title()}<h3/>
      <p style="color:red">Date Stocked: {lake["date"]}</p>
      <p style="color:green">Stocked Amount: {lake["stocked_fish"]}<p/>
      <a style="color:blue" href="{lake["directions"]}" target="_blank">Directions via Googlemaps <a/>
      '''

    popup = folium.Popup(html, max_width=400)
    location = (lake["latitude"], lake["longitude"])

    if lake["derby_participant"]:
      folium.Marker(location=location, tooltip=lake["lake"].capitalize(), popup=popup,
                    icon=folium.Icon(color='red', icon='trophy', prefix='fa')).add_to(
        folium_map)
    else:
      folium.Marker(location=location, tooltip=lake["lake"].capitalize(), popup=popup,
                    icon=folium.Icon(color='blue', icon='info', prefix='fa')).add_to(
        marker_cluster)

  folium.raster_layers.TileLayer('Stamen Terrain').add_to(folium_map)
  folium.LayerControl().add_to(folium_map)

  return folium_map


app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

if __name__ == '__main__':
  app.run(debug=False)

