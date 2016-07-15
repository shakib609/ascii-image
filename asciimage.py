#! /usr/bin/env python3
import os

from flask import (Flask, render_template, flash, redirect, request, url_for)
from flask_script import Manager
from werkzeug.utils import secure_filename

from lib import asciimage

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
UPLOAD_FOLDER = os.path.join(os.path.abspath('.'), 'uploads')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('SECRET_KEY') or 'YOud asdfjln2304u,./f'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

manager = Manager(app)


def allowed_file(filename):
    return '.' in filename and\
                filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form', methods=['GET'])
def upload():
    return render_template('upload.html')


@app.route('/form', methods=['POST'])
def save_image():
    if 'photo' in request.files:
        file = request.files['photo']

        if not file.filename:
            flash('No files selected!')
            return redirect(url_for('upload'))

        filename = secure_filename(file.filename)

        if file and allowed_file(filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.mkdir(app.config['UPLOAD_FOLDER'])
            file.save(filepath)
            return redirect(url_for('success',
                                    filename=filename))
        else:
            flash('Format not Allowed. jpg only!')
        return redirect(url_for('upload'))
    flash('Select a file please!')
    return redirect(url_for('upload'))


@app.route('/ascii-image/<filename>')
def success(filename):

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash('''You have to reupload the image.
We delete your image after processing.''')
        return redirect(url_for('upload'))
    asciimage_str = asciimage(filepath, maxLen=140)
    os.remove(filepath)
    return render_template('ascii-image.html', asciimage_str=asciimage_str)


@app.errorhandler(413)
def file_too_large(err):
    flash('File Size limit 4.0 Mb! Upload another file.')
    return render_template('upload.html'), 413

if __name__ == '__main__':
    manager.run()
