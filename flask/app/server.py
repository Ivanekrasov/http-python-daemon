# http://flask.pocoo.org/docs/patterns/fileuploads/
import os
from flask import Flask, request, redirect, url_for, send_from_directory, send_file, abort, flash
from werkzeug.utils import secure_filename
import hashlib

UPLOAD_FOLDER = 'store'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])):
    os.makedirs(os.path.join(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])))

def allowed_file(filename):
    return filename[-3:].lower() in ALLOWED_EXTENSIONS


name_table = []


def new_file(filename, hashed_filename):
    name_table.append({id: len(name_table) + 1,
                       filename: filename,
                       hash: hashed_filename
                       })


@app.route('/', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            hashed_filename = hashlib.sha224(file.filename.encode('utf-8')).hexdigest()
            new_file(file.filename, hashed_filename)
            if not os.path.exists(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], hashed_filename[0:2])):
                os.makedirs(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], hashed_filename[0:2]))

            file.save(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], hashed_filename[0:2], hashed_filename))
    return '''
        <!doctype html>
        <title>http daemon</title>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form><br>
        <form method=get enctype=multipart/form-data>
          <input type=text name=hash placeholder="Put file hash here">
          <input type=submit value=Download>
        </form>
        '''


@app.route("/hash/", methods=['POST', 'GET'])
def download_button_clicked():
    if any(d['hash'] == 'hashed_filename' for d in name_table):
        filename = list(filter(lambda person: person['hash'] == '111', name_table)[0].get('name'))
        return redirect(url_for('uploaded_file',
                                filename=filename))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)





if __name__ == '__main__':
	app.run(debug=True)
