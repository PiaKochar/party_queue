from flask import Flask, request, render_template, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import spotipy
import spotipy.util as util


username = '124028238'
scope = 'playlist-modify-public'
token = 'BQBsQEYN1vW1Z6xyt6Bnzmd8mtarbEZNHwVs7CCAoy0iSp7x6ip7huvX22rFbrGCZssOs5WEV4d_l00NKBDDP-GKbCSsFWwUHx7S0rqw0a8s7eq79tjxtYWvLZ2jT14wlolbpOEWAL5YL6TDJ0thWj-vEPXXIzLinosjkjxuD3CvR0S0qPWNjfN74A'
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

    def __init__(self, name, uri):
        self.name = name
        self.uri = uri

    def __repr__(self):
        return '<Playlist %r>' % self.name

# Song model for database
class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String(25))
    playlist = db.Column(db.String(120))
    num_votes = db.Column(db.Integer)
    rank = db.Column(db.Integer)

    def __init__(self, uri, playlist):
      self.uri = uri
      self.playlist = playlist

    def __repr__(self):
      return '<Song %r Playlist %r>' % (self.uri, self.playlist)

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
    spotify = spotipy.Spotify()
    user = {'nickname': 'Miguel'}
    playlists = Playlist.query.all()
    return render_template("index.html",
                           title='Home',
                           user=user,
                           playlists=playlists)

@app.route('/', methods=['POST'])
def my_form_post():
  # add to party
  if 'addbutton' in request.form:
    if request.form['addbutton'] == 'Add to Party':
      track_ids = [request.form['uri'][14:]]
      sp.user_playlist_add_tracks(username, session['playlist'], track_ids)
      playlist = sp.user_playlist_tracks(username, session['playlist'])
      song = Song(track_ids[0], session['playlist'])
      db.session.add(song)
      db.session.commit()
      q_tracks = []
      for track in playlist['items']:
        q_tracks.append(track['track'])
      return results("", [])
  # search for songs
  elif 'my-form' in request.form:
    playlist = sp.user_playlist_tracks(username, session['playlist'])
    q_tracks = []
    for track in playlist['items']:
      q_tracks.append(track['track'])
    text = request.form['text']
    processed_text = text.lower()
    return results(processed_text,q_tracks)
  # upvote
  elif 'up' in request.form:
    # upvote(request.form['uri'])
    return results("", [])
  # downvote
  elif 'down' in request.form:
    # downvote(request.form['uri'])
    return results("", [])
  # join a playlist from homepage
  else:
    session['playlist'] = request.form['uri']
    playlist = sp.user_playlist_tracks(username, session['playlist'])
    q_tracks = []
    for track in playlist['items']:
      q_tracks.append(track['track'])
    return results("", [])


@app.route('/results')
def results(search, q_tracks):
    if not is_logged_in():
        return redirect(url_for('login'))
    spotify = spotipy.Spotify()
    results = spotify.search(q='track:' + search, type='track')
    items = results['tracks']['items']
    upper = len(items) if len(items) < 10 else 10
    tracks = []
    if not search == "":
      for i in range(upper):
          track = items[i]
          tracks.append(track)
    return render_template("results.html",
                          title='Home',
                          tracks=tracks,
                          q_tracks=q_tracks)


# @app.route('/new', methods=['POST'])
def new_playlist(playlist_name, playlist_uri):
  if playlist_uri not in Playlist.query.all():
    print 'not in db'
    # current_user = 'pia'
    # sp.user_playlist_create(current_user, playlist_name)
    playlist = Playlist(playlist_name, playlist_uri)
    db.session.add(playlist)
    db.session.commit()
  

def initialize_db():
  db.create_all()
  new_playlist('TEST', '2b0pwZQzfNQBTufDZA86Az')

if __name__ == '__main__':
    # initialize_db()
    # db.create_all()
    app.run(debug=True)
