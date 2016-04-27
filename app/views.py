from flask import Flask, request, render_template, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import spotipy
import spotipy.util as util


username = '124028238'
scope = 'playlist-modify-public'
token = 'BQDJwFOCnl8aG0K8TmSJKAbCTfD2uE0I5XdOzapSaV1wfySiVVVfzfakcnRDgktHFsjdWng6sXoTkP-tidrBX4yh00jcsr5bYMiLhbwwvW6QIEM7wnXsvGQEWSBEmQ5w10AO-jEvQMcjC3GmRevcj0YF_aQwFRb5glSR7WC_KSvAxcWwMIkR9wKlBQ'
sp = spotipy.Spotify(auth=token)
user = sp.user(username)

app = Flask(__name__)
app.config.from_pyfile('db.cfg')
db = SQLAlchemy(app)

# SPOTIFY USER STUFF#
# username = '124028238'
# scope = 'playlist-modify-public'
# # token = 'BQDi0tF5KYHzgUDTk3F-9fCIO7KHdHioIM0hTC5CpASkpXPyZrNT2UEaUu1K1dqt9qfwWhaFDtfvoBBQiVYG6BnbMyfB3_UH_O9St6mfgH3PNx6fHZdhUbenhFlvPbNKLUNoYVV0qZjAjb040du4Va6r07_-jTFpcwPLoUl6mk46a2M7tutwdlJSjw'
# sp = spotipy.Spotify(auth=token)
# user = sp.user(username)
# playlists = sp.user_playlists(username)

# ------------Models --------------------------
# Playlist model for database
class Playlist(db.Model):
    __tablename__ = 'playlists'
    uri = db.Column(db.String(25), primary_key=True)
    name = db.Column(db.String(120))
    # password = db.Column(db.String(80))

    def __init__(self, name, uri):
        self.name = name
        self.uri = uri
        # self.password = password

    def __repr__(self):
        return '<Playlist %r>' % self.name

# Song model for database
class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String(25))
    name = db.Column(db.String(120))
    queue = db.Column(db.String(120))
    num_votes = db.Column(db.Integer)
    rank = db.Column(db.Integer)

    def __init__(self, name, uri, queue):
      self.name = name
      self.uri = uri
      self.queue = queue

    def __repr__(self):
      return '<Song %r Queue %r>' % self.name, self.queue

    def upvote(self):
      self.num_votes += 1
      db.session.commit()

    def downvote(self):
      self.num_votes -= 1
      db.session.commit()

    def set_rank(self, rank):
      self.rank = rank
      db.session.commit()


# Voted model for database
class Voted(db.Model):
  __tablename__ = 'voted'
  song = db.Column(db.String(120), primary_key=True)
  user = db.Column(db.String(120), primary_key=True)

  def __init__(self, song, user):
    self.song = song
    self.user = user

  def __repr__(self):
    return '<User %r Voted on %r>' % self.user, self.song

# User model for database
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.username

def is_logged_in():
    if 'username' in session:
        return True
    return False

# ------------- Views ----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        redirect(url_for('index'))
    if request.method == 'POST':
        session['username'] = request.form['username']
        user = User(request.form['username'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('index'))
    if request.method == 'POST':
        if User.query.filter(User.username == request.form['username']).all():
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
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
  # THIS IS IF WE ADD TO PARTY
  if 'addbutton' in request.form:
    if request.form['addbutton'] == 'Add to Party':
      track_ids = [request.form['uri'][14:]]
      sp.user_playlist_add_tracks(username, '2b0pwZQzfNQBTufDZA86Az', track_ids)
      # sp.user_playlist_create(username, 'TEST')
      playlist = sp.user_playlist_tracks(username,'2b0pwZQzfNQBTufDZA86Az')
      q_tracks = []
      for track in playlist['items']:
        q_tracks.append(track['track'])
      return results('hello',q_tracks)
  # THIS IS IF WE SEARCH
  elif 'my-form' in request.form:
    playlist = sp.user_playlist_tracks(username,'2b0pwZQzfNQBTufDZA86Az')
    q_tracks = []
    for track in playlist['items']:
      q_tracks.append(track['track'])
    text = request.form['text']
    processed_text = text.lower()
    return results(processed_text,q_tracks)
  #THIS IS IF WE CLICK UP OR DOWN
  else:
    playlist = sp.user_playlist_tracks(username,'2b0pwZQzfNQBTufDZA86Az')
    q_tracks = []
    for track in playlist['items']:
      q_tracks.append(track['track'])
    print("what")
    return results("idk",q_tracks)

@app.route('/new', methods=['POST'])
def new_playlist(username, playlist_name):
  sp.user_playlist_create(username, playlist_name)
  playlist = Playlist(playlist_name, uri)
  db.session.add(playlist)
  db.session.commit()
  

@app.route('/results')
def results(search,q_tracks):
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
                          tracks=tracks,
                          q_tracks=q_tracks)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
