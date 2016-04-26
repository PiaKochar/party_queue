from flask import render_template
from flask import request
from app import app
import spotipy
import spotipy.util as util
import spotify 


@app.route('/')
@app.route('/index')
def index():
    # track = session.get_track('spotify:track:1ToxbPCzdozcOPAe0Pyuyk')
    # player = Player(session)
    # player.load(track)
    # player.play
    # session = spotify.Session()
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

@app.route('/', methods=['POST'])
def my_form_post():
  text = request.form['text']
  processed_text = text.lower()
  return results(processed_text)

@app.route('/results')
def results(search):
  # if request.form['submit'] == 'Add to Party':
  #     song = Song(track['name'], queue name) # how to get this data?
  #     db.session.add(song)
  #     db.session.commit()
  spotify = spotipy.Spotify()
  results = spotify.search(q='track:' + search, type='track')
  items = results['tracks']['items']
  tracks = []
  for i in range(10):
    track = items[i]
      # for key in track:
      #   print "key: %s , value: %s" % (key, track[key])
      # tracks.append(track['name'] + " " + track['artists'][0]['name'] + \
      #  " " + track['uri'])
    tracks.append(track)


  return render_template("results.html",
                          title='Home',
                          tracks=tracks)


