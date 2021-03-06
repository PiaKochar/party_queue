from flask import Flask, request, render_template, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import spotipy
import spotipy.util as util

username = '124028238'
scope = 'playlist-modify-public'
token = 'BQAYvVlo7OyL2C6-4JQLwxPu6MaQLBaSD1GfP3XvJgcc-kDPESnVbK0eknLXr5YNdc4TpC9FAW7KpcJ5FTm8b2Q-m7RD4ZW1O6oZXqVKSuKFoG3R42Lk8vVNweJw7QLhQn-GivFL6PtNxu1o-LvJZHEvQ6l0MJDLvr1IzsZusQbUyuWMledi6iDDiw'
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
    num_songs = db.Column(db.Integer, default=0)

    def __init__(self, name, uri):
        self.name = name
        self.uri = uri

    def __repr__(self):
        return '<Playlist {}>'.format(self.name)

# Song model for database


class Song(db.Model):
    __tablename__ = 'songs'
    uri = db.Column(db.String(25), primary_key=True)
    playlist = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(120))
    num_votes = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer)

    def __init__(self, uri, playlist):
        self.uri = uri
        self.num_votes = 0
        self.playlist = playlist
        p = Playlist.query.filter(Playlist.uri == playlist).first()
        self.rank = p.num_songs
        p.num_songs += 1

    def __repr__(self):
        return '<Song: {}, Playlist: {}, Order: {}, Votes: {}>'.format(
            self.name, self.playlist, self.rank, self.num_votes)

    def upvote(self):
        self.num_votes += 1
        db.session.commit()
        print '<Votes: {}>'.format(self.num_votes)

    def downvote(self):
        self.num_votes -= 1
        db.session.commit()
        print '<Votes: {}>'.format(self.num_votes)

    def set_rank(self, rank):
        self.rank = rank
        db.session.commit()


# Voted model for database
class Voted(db.Model):
    __tablename__ = 'voted'
    song = db.Column(db.String(120), primary_key=True)
    user = db.Column(db.String(120), primary_key=True)
    upvote = db.Column(db.Boolean)

    def __init__(self, song, user, upvote):
        self.song = song
        self.user = user
        self.upvote = upvote

    def __repr__(self):
        return '<User {} Voted on {} {}>'.format(
            self.user, self.song, self.upvote)

# User model for database


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User {}: {}>'.format(self.username, self.id)

# ------------- Helper Functions -----------------


def is_logged_in():
    if 'username' in session:
        return True
    return False


def change_ordering_upvote(song_uri):
    song = Song.query.filter(Song.uri == song_uri).first()
    print "upvote song at rank: " + str(song.rank)
    prev_song = Song.query.filter(
        Song.playlist == song.playlist,
        Song.rank == song.rank - 1).first()
    if prev_song:
        print " UGHGHH" + str(song.num_votes)
        print prev_song.num_votes
        while (song.num_votes > prev_song.num_votes):
            print str(song.rank) + "-->" + str(prev_song.rank)
            sp.user_playlist_reorder_tracks(
                username, song.playlist, song.rank, prev_song.rank)
            song.rank -= 1
            prev_song.rank += 1
            db.session.commit()
            prev_song = Song.query.filter(
                Song.playlist == song.playlist,
                Song.rank == song.rank - 1).first()
            if not prev_song:
                break
    db.session.commit()


def change_ordering_downvote(song_uri):
    song = Song.query.filter(Song.uri == song_uri).first()
    print "downvote song at rank: " + str(song.rank)
    next_song = Song.query.filter(
        Song.playlist == song.playlist,
        Song.rank == song.rank + 1).first()
    if next_song:
        while (song.num_votes < next_song.num_votes):
            print str(song.rank) + "-->" + str(next_song.rank)
            print "uri: " + str(song.playlist)
            curr_playlist = Playlist.query.filter(
                Playlist.uri == session['playlist']).first()
            sp.user_playlist_reorder_tracks(
                username, song.playlist, song.rank, next_song.rank + 1)
            song.rank += 1
            next_song.rank -= 1
            db.session.commit()
            next_song = Song.query.filter(
                Song.playlist == song.playlist,
                Song.rank == song.rank + 1).first()
            if not next_song:
                break
    db.session.commit()


def vote(song_uri, user_id, upvote):
    user_vote = Voted(song_uri, user_id, upvote)
    db.session.add(user_vote)
    db.session.commit()


def upvote(song_uri):
    if not is_logged_in():
        return redirect(url_for('login'))
    user = User.query.filter(User.username == session['username']).first()
    if Voted.query.filter(Voted.user == user.id, Voted.song == song_uri,
                          Voted.upvote).all():
        print "can't upvote a song twice"
        return
    if Voted.query.filter(Voted.user == user.id, Voted.song == song_uri).all():
        print "changing vote from down to up"
        user_vote = Voted.query.filter(
            Voted.user == user.id,
            Voted.song == song_uri).first()
        user_vote.upvote = True

        song = Song.query.filter(Song.uri == song_uri).first()
        print song
        song.upvote()
        song.upvote()

        change_ordering_upvote(song_uri)
    else:
        print "new vote"
        vote(song_uri, user.id, True)
        song = Song.query.filter(Song.uri == song_uri).first()
        song.upvote()
        change_ordering_upvote(song_uri)


def downvote(song_uri):
    if not is_logged_in():
        return redirect(url_for('login'))
    user = User.query.filter(User.username == session['username']).first()
    if Voted.query.filter(Voted.user == user.id, Voted.song == song_uri,
                          Voted.upvote == False).all():
        print "can't downvote a song twice"
        return

    if Voted.query.filter(Voted.user == user.id, Voted.song == song_uri).all():
        print "changing vote from up to down"
        user_vote = Voted.query.filter(
            Voted.user == user.id,
            Voted.song == song_uri).first()
        user_vote.upvote = False

        song = Song.query.filter(Song.uri == song_uri).first()
        song.downvote()
        song.downvote()

        change_ordering_downvote(song_uri)
    else:
        print "new vote"
        print ""
        vote(song_uri, user.id, False)
        song = Song.query.filter(Song.uri == song_uri).first()
        song.downvote()
        change_ordering_downvote(song_uri)

# ------------- Views ----------------------------


@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        redirect(url_for('index'))
    if request.method == 'POST':
        if User.query.filter(User.username == request.form['username']).all():
            return redirect(url_for('register'))
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
                           playlists=playlists,
                           username=session['username'])


@app.route('/', methods=['POST'])
def my_form_post():
    # add to party
    if 'addbutton' in request.form:
        if request.form['addbutton'] == 'Add to Party':
            track_ids = [request.form['uri'][14:]]
            sp.user_playlist_add_tracks(
                username, session['playlist'], track_ids)
            playlist = sp.user_playlist_tracks(username, session['playlist'])
            song = Song(track_ids[0], session['playlist'])
            db.session.add(song)
            db.session.commit()
            q_tracks = []
            for track in playlist['items']:
                q_tracks.append(track['track'])
            return results("", q_tracks)
    # search for songs
    elif 'my-form' in request.form:
        playlist = sp.user_playlist_tracks(username, session['playlist'])
        q_tracks = []
        for track in playlist['items']:
            song = Song.query.filter(
                Song.uri == track['track']['uri'][
                    14:]).first()
            print 'rank: ' + str(song.rank) + ' num_votes: ' + str(song.num_votes)
            q_tracks.append(track['track'])
        text = request.form['text']
        processed_text = text.lower()
        return results(processed_text, q_tracks)
    # upvote
    elif 'up' in request.form:
        print 'upvote'
        playlist = sp.user_playlist_tracks(username, session['playlist'])
        q_tracks = []
        upvote(request.form['uri'][14:])
        for track in playlist['items']:
            q_tracks.append(track['track'])
        return results("", q_tracks)
    # downvote
    elif 'down' in request.form:
        print 'downvote'
        playlist = sp.user_playlist_tracks(username, session['playlist'])
        q_tracks = []
        downvote(request.form['uri'][14:])
        for track in playlist['items']:
            q_tracks.append(track['track'])
        return results("", q_tracks)
    # create new playlist
    elif 'new-playlist' in request.form:
        text = request.form['text']
        processed_text = text
        sp.user_playlist_create(username, processed_text)
        playlist_uri = sp.user_playlists(username)['items'][0]['uri'][32:]
        playlist = Playlist(processed_text, playlist_uri)
        db.session.add(playlist)
        db.session.commit()
        session['playlist'] = playlist_uri
        return results("", [])
    # join a playlist from homepage
    else:
        session['playlist'] = request.form['uri']
        playlist = sp.user_playlist_tracks(username, session['playlist'])
        q_tracks = []
        for track in playlist['items']:
            q_tracks.append(track['track'])
            if not Song.query.filter(
                Song.uri == track['track']['uri'][
                    14:]).all():
                song = Song(track['track']['uri'][14:], session['playlist'])
                db.session.add(song)
                db.session.commit()
        return results("", q_tracks)


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
                           q_tracks=q_tracks,
                           username=session['username'],
                           playlist=session['playlist'])


@app.route('/', methods=['POST'])
def new_playlist(playlist_name, playlist_uri):
    if playlist_uri not in Playlist.query.all():
        current_user = 'pia'
        sp.user_playlist_create(current_user, playlist_name)
        print sp.user_playlists(username)[0]
        playlist = Playlist(playlist_name, playlist_uri)
        db.session.add(playlist)
        db.session.commit()


def initialize_db():
    db.create_all()
    # new_playlist('TEST', '2b0pwZQzfNQBTufDZA86Az')

if __name__ == '__main__':
    initialize_db()
    # db.create_all()
    app.run(debug=True)
