from flask import render_template
from app import app
import spotipy
import spotipy.util as util

@app.route('/')
@app.route('/index')
def index():
    birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
    spotify = spotipy.Spotify()

    results = spotify.artist_albums(birdy_uri, album_type='album')
    albums = results['items']
    while results['next']:
        results = spotify.next(results)
        albums.extend(results['items'])
    
    user = {'nickname': 'Miguel'}
    return render_template("index.html",
                           title='Home',
                           user=user,
                           albums=albums)
