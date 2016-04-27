from sqlalchemy import Column, Integer, String
from database import Base

# Queue model for database
class Queue(Base):
    __tablename__ = 'queues'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    password = Column(String(80))

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __repr__(self):
        return '<Queue %r>' % self.name


# Song model for database
class Song(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    queue = Column(String(120))
    rank = Column(Integer)

    def __init__(self, name, queue):
        self.name = name

    def __repr__(self):
        return '<Song %r Queue %r>' % self.name, self.queue

    def upvote(self):
        self.rank += 1

    def downvote(self):
        self.rank -= 1

# User model for database
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(120))

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.username