
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from flask import Flask, render_template, url_for
import jinja2
app = Flask(__name__)  #, static_url_path='', static_folder='static'



@app.route('/')
def render_the_map():
    folium_map = make_map(df=pd.read_csv("templates/Stocked-Lakes(3).csv"))
    derby_lakes = ['Golf Course Pond', 'Beehive Reservoir', 'Battle Ground Lake', 'Blue Lake (Columbia County)', 'Horseshoe Lake (Cowlitz County)', 'Jameson Lake', 'Curlew Lake', 'Dalton Lake', 'Corral Lake', 'Duck Lake', 'Deer Lake (Island County)', 'Leland Lake', 'Cottage Lake', 'Island Lake (Kitsap County)', 'Easton Ponds', 'Rowland Lake', 'Carlisle Lake', 'Fishtrap Lake', 'Benson Lake', 'Alta Lake', 'Black Lake', 'Diamond Lake', 'American Lake', 'Lake Erie', 'Icehouse Lake', 'Ballinger Lake', 'Badger Lake', 'Cedar Lake', 'Deep Lake (Thurston County)', 'Bennington Lake', 'Lake Padden', 'Garfield Pond', 'I-82 Pond 4']
    return render_template('index.html', folium_map=folium_map._repr_html_(), derby_lakes=derby_lakes)


# Make the Map with Folium
def make_map(df):
    # https://towardsdatascience.com/pythons-geocoding-convert-a-list-of-addresses-into-a-map-f522ef513fd6

    # import the library and its Marker clusterization service
    m = folium.Map(width="100%" , max_width="50%", max_height="50%", location=df[["latitude", "longitude"]].mean().to_list(),
                   zoom_start=7)  # if the points are too close to each other, cluster them, create a cluster overlay with MarkerCluster, add to m
    marker_cluster = MarkerCluster().add_to(m)

    # draw the markers and assign popup and hover texts
    # add the markers the the cluster layers so that they are automatically clustered
    for i, r in df.iterrows():
        html = f'''
        <h3 >{r["Lake"].capitalize()}<h3/>
        <a style="color:blue" href="{r["Directions"]}" target="_blank">Directions via Googlemaps <a/>
        <p style="color:green">Stocked Amount: {r["Stocked Fish"]}<p/>
        <p style="color:red">Date Stocked: {r["dates"]}</p>'''

        iframe = folium.IFrame(html, width=200, height='300')
        popup = folium.Popup(iframe, max_width=200)

        location = (r["latitude"], r["longitude"])

        folium.Marker(location=location, tooltip=r["Lake"].capitalize(), popup=popup).add_to(
            marker_cluster)

    return m


if __name__ == '__main__':
    app.run(debug=True)
