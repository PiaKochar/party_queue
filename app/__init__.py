from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
from app import views

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
app.secret_key = 'many random bytes'

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


