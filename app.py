from collections import namedtuple

import os
import shutil
import hashlib
from flask import Flask, url_for, render_template, request, redirect, send_file, make_response, abort


UPLOAD_FOLDER = 'store'

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

File = namedtuple('File', 'name hash')
files = []


# ----------- remove in prod
if not os.path.exists(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])):
    os.makedirs(os.path.join(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])))
# -----------


def hash_filename(filename):
    hashed_filename = hashlib.sha224(filename.encode('utf-8')).hexdigest()
    files.append(File(filename, hashed_filename))
    return hashed_filename


@app.route('/', methods=['GET'])
def page():
    return redirect(url_for('main'))


@app.route('/main', methods=['GET'])
def main():
    return render_template('home.html', files=files)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        try:
            file = request.files['file']
        except KeyError:
            return abort(404, "Empty request")

        hash = hash_filename(file.filename)
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


