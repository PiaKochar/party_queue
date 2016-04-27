#!flask/bin/python
from app import app
from app import db
db.create_all()
app.run(debug=True)
