from flask import render_template, request, flash, session, redirect, url_for
from app import app
from app.models import User
import spotipy
import spotipy.util as util
# import spotify

# config = spotify.Config()
# config.user_agent = 'My awesome Spotify client'
# config.tracefile = b'/tmp/libspotify-trace.log'
# session = spotify.Session(config)

def is_logged_in():
    if 'username' in session:
        return True
    return False

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        redirect(url_for('index'))
    if request.method == 'POST':
        session['username'] = request.form['username']
        user = User(request.form['username'])
        # db.session.add(user)
        # db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('index'))
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
@app.route('/index')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
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
  print(request.form)
  if 'addbutton' in request.form:
    if request.form['addbutton'] == 'Add to Party':
      return results('hello')
  else:
    text = request.form['text']
    processed_text = text.lower()
    return results(processed_text)

# @app.route('/', methods=['POST'])
# def add_post():
#   return add_song(queue)

@app.route('/results')
def results(search):
    if not is_logged_in():
        return redirect(url_for('login'))
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
      #     print "key: %s , value: %s" % (key, track[key])
      # tracks.append(track['name'] + " " + track['artists'][0]['name'] + \
      #  " " + track['uri'])
        tracks.append(track)


    return render_template("results.html",
                          title='Home',
                          tracks=tracks)

# @app.route('/add')
# def add_song(queue):

