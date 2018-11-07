from collections import namedtuple

import os
import shutil
from flask import url_for, render_template, request, redirect, send_file, make_response, abort, flash
from config import app, File
from hash_file import hash_file
# import hashlib
# ----------- remove in prod


# File = namedtuple('File', 'name hash')
# files = []



if not os.path.exists(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])):
    os.makedirs(os.path.join(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])))
# -----------


@app.route('/', methods=['GET'])
def page():
    return redirect(url_for('main'))


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
        hash = request.form['hash']
    except KeyError:
        return abort(404, "Empty request")

    if [file.hash == hash for file in files]:
        filename = [file.name for file in files if file.hash == hash][0]
        file_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], hash[0:2])
        return send_file(os.path.join(file_path, hash),  attachment_filename=filename, as_attachment=True)
    else:
        abort(404, "File not found")


@app.route('/delete', methods=['POST'])
def delete():
    try:
        hash = request.form['hash']
    except KeyError:
        return abort(404, "Empty request")

    if [file.hash == hash for file in files]:
        file_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], hash[0:2])
        shutil.rmtree(file_path)
        files.remove([file for file in files if file.hash == hash][0])
        return redirect(url_for('main'))
    else:
        abort(404, "File not found")


