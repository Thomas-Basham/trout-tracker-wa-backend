
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from flask import Flask, render_template, url_for, request, flash
import re
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine


app = Flask(__name__)
engine = create_engine('postgresql://jwfbiznnunacny:fba985f8952e07c141048fb3f27c2f9e92546f0776885f4730e1ae0dff06f6c9@ec2-54-165-178-178.compute-1.amazonaws.com:5432/d785j4kuapuget')
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://jwfbiznnunacny:fba985f8952e07c141048fb3f27c2f9e92546f0776885f4730e1ae0dff06f6c9@ec2-54-165-178-178.compute-1.amazonaws.com:5432/d785j4kuapuget'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


@app.route('/')
def render_the_map():
    # *********************** DRIVER FOR MAP DATA **********************************
    with engine.connect().execution_options(autocommit=True) as conn:
        df = pd.read_sql(f"""SELECT * FROM stocked_lakes_table """, con=conn)
    folium_map = make_map(df)

    most_recent_stocked = df.head()
    most_recent_stocked = df.drop(["latitude", "longitude", "Directions", "index"], axis=1)
    most_recent_stocked = most_recent_stocked.to_html(index=False, classes='table table-stripped' "table-hover" "table-sm")
    return render_template('index.html', folium_map=folium_map._repr_html_(),
                           derby_lakes=set(derby_lakes_on_map), most_recent_stocked=most_recent_stocked)


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
    write_derby_participants(df)
    # import the library and its Marker clusterization service
    m = folium.Map(width="100%" , max_width="100%", max_height="100%", location=df[["latitude", "longitude"]].mean().to_list(),
                   zoom_start=7)  # if the points are too close to each other, cluster them, create a cluster overlay with MarkerCluster, add to m
    marker_cluster = MarkerCluster().add_to(m)
    derby_lakes = ['Golf Course Pond', 'Beehive Reservoir', 'Battle Ground Lake', 'Blue Lake (Columbia County)', 'Horseshoe Lake (Cowlitz County)', 'Jameson Lake', 'Curlew Lake', 'Dalton Lake', 'Corral Lake', 'Duck Lake', 'Deer Lake (Island County)', 'Leland Lake', 'Cottage Lake', 'Island Lake (Kitsap County)', 'Easton Ponds', 'Rowland Lake', 'Carlisle Lake', 'Fishtrap Lake', 'Benson Lake', 'Alta Lake', 'Black Lake', 'Diamond Lake', 'American Lake', 'Lake Erie', 'Icehouse Lake', 'Ballinger Lake', 'Badger Lake', 'Cedar Lake', 'Deep Lake (Thurston County)', 'Bennington Lake', 'Lake Padden', 'Garfield Pond', 'I-82 Pond 4']

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


        if r["Derby Participant"] == True:
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


derby_lakes_on_map = []


def write_derby_participants(df):
    df["Derby Participant"] = ""
    derby_lakes = ['Golf Course Pond', 'Beehive Reservoir', 'Battle Ground Lake', 'Blue Lake (Columbia County)', 'Horseshoe Lake (Cowlitz County)', 'Jameson Lake', 'Curlew Lake', 'Dalton Lake', 'Corral Lake', 'Duck Lake', 'Deer Lake (Island County)', 'Leland Lake', 'Cottage Lake', 'Island Lake (Kitsap County)', 'Easton Ponds', 'Rowland Lake', 'Carlisle Lake', 'Fishtrap Lake', 'Benson Lake', 'Alta Lake', 'Black Lake', 'Diamond Lake', 'American Lake', 'Lake Erie', 'Icehouse Lake', 'Ballinger Lake', 'Badger Lake', 'Cedar Lake', 'Deep Lake (Thurston County)', 'Bennington Lake', 'Lake Padden', 'Garfield Pond', 'I-82 Pond 4']
    derby_lakes = [re.sub(r"\(.*?\)", '', text) for text in derby_lakes]

    # print(df[df['Lake'].str.contains('Pond')==True])

    for lake in derby_lakes:
        for ind in df.index:
            if lake.capitalize() in df['Lake'][ind].capitalize():
                derby_lakes_on_map.append(lake)
                df.loc[ind, ['Derby Participant']] = [True]
            # elif lake.capitalize() not in df['Lake'][ind].capitalize():
            #     df.loc[ind, ['Derby Participant']] = [False]
    # print(f"DERBY LAKES: {(set(derby_lakes_on_map))}")
    return df


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
