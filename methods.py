from config import db, File, api
from flask import jsonify


class FilesDAO(object):
    def __init__(self):
        self.files = File.query.all()

    def get(self, filename):
        for file in self.files:
            if file.filename == filename:
                return jsonify(file)
        api.abort(404, "File {} doesn't exist".format(filename))

    def update(self, filename, file_hash):
        if File.query.filter_by(hash=file_hash).first():
            row = File.query.filter_by(hash=file_hash).first()
            row.name = filename
            db.session.commit()
            return jsonify(filename)
        api.abort(404, "File {} doesn't exist".format(file_hash))

    def delete(self, file_hash):
        if File.query.filter_by(hash=file_hash).first():
            db.session.delete(File.query.filter_by(hash=file_hash).first())
            db.session.commit()
            return 'successfully deleted'
        api.abort(404, "File {} doesn't exist".format(file_hash))

