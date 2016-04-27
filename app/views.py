from flask import Flask, request, render_template, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import spotipy
import spotipy.util as util


username = '124028238'
scope = 'playlist-modify-public'
token = 'BQAPT0toVFpZiMZQsDZfcSSkAmrsNc1YKK2W2odGLypU5yaXQkCoJ1nSf0-UlH9UzILXaaHnMT7d6esJIDihKY3iwjzVNkaWq-reR2COIAXrx_MOHewN7FbQUdMgH9PWCr458mupplHhFrJuyBZsVrXETbTKl96Rk6vIhH0i_-8cJ6lm5JH_S8cL3A'
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
      return '<Song %r Playlist %r>' % self.uri, self.playlist

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
  # THIS IS IF WE ADD TO PARTY
  if 'addbutton' in request.form:
    if request.form['addbutton'] == 'Add to Party':
      track_ids = [request.form['uri'][14:]]
      sp.user_playlist_add_tracks(username, '2b0pwZQzfNQBTufDZA86Az', track_ids)
      playlist = sp.user_playlist_tracks(username,'2b0pwZQzfNQBTufDZA86Az')
      song = Song(track_ids, '2b0pwZQzfNQBTufDZA86Az')
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
    playlist = sp.user_playlist_tracks(username, request.form['uri'])
    q_tracks = []
    for track in playlist['items']:
      q_tracks.append(track['track'])
    return results("idk",q_tracks)

# creates a new playlist but how to access playlist uri...?
# @app.route('/new', methods=['POST'])
# def new_playlist(username, playlist_name):
#   sp.user_playlist_create(username, playlist_name)
#   playlist = Playlist(playlist_name, uri)
#   db.session.add(playlist)
#   db.session.commit()
  

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
    upper = len(items) if len(items) < 10 else 10
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

def initialize_db():
  db.create_all()
  p = Playlist('TEST', '2b0pwZQzfNQBTufDZA86Az')
  db.session.add(p)
  db.session.commit()

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True)
