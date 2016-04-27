from flask import Flask, request, render_template, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import spotipy
import spotipy.util as util
# import spotify

# config = spotify.Config()
# config.user_agent = 'My awesome Spotify client'
# config.tracefile = b'/tmp/libspotify-trace.log'
# session = spotify.Session(config)

app = Flask(__name__)
app.config.from_pyfile('db.cfg')
db = SQLAlchemy(app)

# ------------Models --------------------------
# Queue model for database
class Queue(db.Model):
    __tablename__ = 'queues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    password = db.Column(db.String(80))

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __repr__(self):
        return '<Queue %r>' % self.name


# Song model for database
class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    queue = db.Column(db.String(120))
    rank = db.Column(db.Integer)

    def __init__(self, name, queue):
        self.name = name

    def __repr__(self):
        return '<Song %r Queue %r>' % self.name, self.queue

    def upvote(self):
        self.rank += 1

    def downvote(self):
        self.rank -= 1

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
            return (url_for('login'))
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

if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True)
