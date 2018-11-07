import os
from methods import FilesDAO
from flask import url_for, render_template, request, redirect, send_file, make_response, abort
from flask_restplus import Resource
from config import app, db, File, ns, files_api
from hash_file import hash_file
import shutil

# ----------- remove in prod
if not os.path.exists(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])):
    os.makedirs(os.path.join(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])))
# -----------


@app.route('/', methods=['GET'])
def page():
    # return redirect(url_for('main'))
    return render_template('root.html')


@app.route('/main', methods=['GET'])
def main():
    return render_template('home.html', files=File.query.all())


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        try:
            file = request.files["file"]
        except KeyError as e:
            return e, 404

        if File.query.filter_by(filename=file.filename).first():
            abort(404, "File with name {filename} already exists".format(filename=file.filename))

        hash = hash_file(file)
        path_name = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], hash[0:2])
        if not os.path.exists(path_name):
            os.makedirs(path_name)
            file.save(os.path.join(path_name, hash))
            if os.path.exists(path_name):
                response = make_response(redirect(url_for('main')))
                response.headers['hash'] = hash

        else:
            if os.path.exists(os.path.join(path_name, hash)):
                abort(404, "File with hash {hash} already exists".format(hash=hash))

    return response


@app.route('/download', methods=['POST'])
def download():
    try:
        file_hash = request.form['hash']
    except KeyError:
        return abort(404, "Empty request")

    if File.query.filter_by(hash=file_hash).first():
        filename = File.query.filter_by(hash=file_hash).first().filename
        file_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], file_hash[0:2])
        return send_file(os.path.join(file_path, file_hash),  attachment_filename=filename, as_attachment=True)
    else:
        abort(404, "File not found")


@app.route('/delete', methods=['POST'])
def delete():
    try:
        file_hash = request.form['hash']
    except KeyError:
        return abort(404, "Empty request")

    if File.query.filter_by(hash=file_hash).first():
        record_to_delete = File.query.filter_by(hash=file_hash).one()
        db.session.delete(record_to_delete)
        db.session.commit()
        file_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], file_hash[0:2])
        shutil.rmtree(file_path)
        return redirect(url_for('main'))
    else:
        abort(404, "File not found")


# ============ API doc ===============
DAO = FilesDAO()

@ns.route('/')
class FileList(Resource):
    @ns.doc('list_files')
    @ns.marshal_list_with(files_api)
    def get(self):
        return DAO.files


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The file identifier')
class FileRes(Resource):
    @ns.doc('get_file')
    @ns.marshal_with(files_api)
    def get(self, filename):
        return DAO.get(filename)

    @ns.doc('delete_file')
    @ns.response(204, 'File deleted')
    def delete(self, file_hash):
        DAO.delete(file_hash)
        return '', 204

    @ns.expect(files_api)
    @ns.marshal_with(files_api)
    def put(self, filename, file_hash):
        return DAO.update(filename, file_hash)

