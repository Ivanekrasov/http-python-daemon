from collections import namedtuple

import os
import hashlib
from flask import Flask, url_for, render_template, request, redirect, flash, send_file

UPLOAD_FOLDER = 'store'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

File = namedtuple('File', 'name hash')
files = []

# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# ----------- remove in prod
if not os.path.exists(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])):
    os.makedirs(os.path.join(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])))
# -----------


def hash_filename(filename):
    hashed_filename = hashlib.sha224(filename.encode('utf-8')).hexdigest()
    files.append(File(filename, hashed_filename))
    return hashed_filename

# def allowed_file(filename):
#     return filename[-3:].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def page():
    return redirect(url_for('main'))


@app.route('/main', methods=['GET'])
def main():
    return render_template('index.html', files=files)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        hash = hash_filename(file.filename)
        path_name = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], hash[0:2])
        if not os.path.exists(path_name):
            os.makedirs(path_name)

        file.save(os.path.join(path_name, hash))

    return redirect(url_for('main'))


@app.route('/download', methods=['POST'])
def download():
    hash = request.form['hash']
    if hash == '':
        flash('No input hash')
        return redirect(request.url)
    if [file.hash == hash for file in files]:
        filename = [file.name for file in files if file.hash == hash][0]
        file_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], hash[0:2])
        return send_file(os.path.join(file_path, hash),  attachment_filename=filename, as_attachment=True)

