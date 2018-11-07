from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
import os
from flask_restplus import Api, fields

DATABASE = 'app.db'
UPLOAD_FOLDER = 'store'

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.getcwd() + '/' + DATABASE
db = SQLAlchemy(app)

blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, version='0.1', title='HTTP daemon API', description='A simple HTTP daemon API', doc='/doc/')
app.register_blueprint(blueprint)
ns = api.namespace('files', description='Files operations')

files_api = api.model('Files', {
    'filename': fields.String(readOnly=True, description='The file name'),
    'hash': fields.String(required=True, description='The file hash')
})


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, unique=True, nullable=False)


# for the safe side
# db.create_all()
# db.session.add(File(filename='somefilename', hash='somehash'))
# db.session.commit()
