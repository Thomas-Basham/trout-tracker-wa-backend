import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster, Fullscreen
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Postgres Database
engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@app.route('/')
def render_the_map():
    # *********************** DRIVER FOR MAP DATA **********************************
    with engine.connect().execution_options(autocommit=True) as conn:
        df = pd.read_sql(f"""SELECT * FROM stocked_lakes_table """, con=conn)
        derbydf = pd.read_sql(f"""SELECT * FROM derby_lakes_table """, con=conn)

    folium_map = make_map(df)
    derby_lakes = set(derbydf['Lake'])

    most_recent_stocked = df.head()
    most_recent_stocked = df.drop(["latitude", "longitude", "Directions", "index"], axis=1)
    most_recent_stocked = most_recent_stocked.to_html(index=False, classes='table table-hover table-bordered table-dark table-striped table-sm')
    return render_template('index.html', folium_map=folium_map._repr_html_(),
                           derby_lakes=derby_lakes, most_recent_stocked=most_recent_stocked)


@app.route('/fullscreen')
def map_full_screen():
    # df = pd.read_csv("templates/Stocked-Lakes.csv")
    with engine.connect().execution_options(autocommit=True) as conn:
        df = pd.read_sql(f"""SELECT * FROM stocked_lakes_table """, con=conn)

    folium_map = make_map(df)
    return render_template('map_full_screen.html', folium_map=folium_map._repr_html_())


# Make the Map with Folium
def make_map(df):
    # https://towardsdatascience.com/pythons-geocoding-convert-a-list-of-addresses-into-a-map-f522ef513fd6
    # write_derby_participants(df)
    # import the library and its Marker clusterization service
    m = folium.Map(width="100%", max_width="100%", max_height="100%", location=df[["latitude", "longitude"]].mean().to_list(),
                   zoom_start=7)
    # if the points are too close to each other, cluster them, create a cluster overlay with MarkerCluster, add to m
    marker_cluster = MarkerCluster().add_to(m)
    Fullscreen(
        position='topright',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True
    ).add_to(m)
    # draw the markers and assign popup and hover texts
    # add the markers the the cluster layers so that they are automatically clustered
    for i, r in df.iterrows():

        html = f'''
        <h3 >{r["Lake"].capitalize()}<h3/>
        <p style="color:green">Stocked Amount: {r["Stocked Fish"]}<p/>
        <a style="color:blue" href="{r["Directions"]}" target="_blank">Directions via Googlemaps <a/>
        <p style="color:red">Date Stocked: {r["Date"]}</p>
        <p style="color:orange">In Trout Derby: {r["Derby Participant"]}</p>
        
        '''

        iframe = folium.IFrame(html, width='max-content', height='fit-content')
        popup = folium.Popup(iframe, max_width="max-content")

        location = (r["latitude"], r["longitude"])

        if r["Derby Participant"] =="true":
            folium.Marker(location=location, tooltip=r["Lake"].capitalize(), popup=popup,
                          icon=folium.Icon(color='green', icon= 'info', prefix='fa')).add_to(
                m)
        else:
            folium.Marker(location=location, tooltip=r["Lake"].capitalize(), popup=popup,
                          icon=folium.Icon(color='blue', icon= 'info', prefix='fa')).add_to(
                marker_cluster)
    folium.raster_layers.TileLayer('Stamen Terrain').add_to(m)
    folium.LayerControl().add_to(m)

    return m


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
