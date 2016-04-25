from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
from app import views

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class Queue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    password = db.Column(db.String(80))
    songs = 

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __repr__(self):
        return '<Queue %r>' % self.name