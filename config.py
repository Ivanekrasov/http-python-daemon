from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

DATABASE = 'app.db'
UPLOAD_FOLDER = 'store'

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.getcwd() + '/' + DATABASE
db = SQLAlchemy(app)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, unique=True, nullable=False)


# db.create_all()
# db.session.add(File(filename='somefilename', hash='somehash'))
# db.session.add(File(filename='somefilename', hash='somehash1'))
# db.session.add(File(filename='somefilename1', hash='somehash2'))
# db.session.commit()
