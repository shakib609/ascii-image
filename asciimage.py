#! /usr/bin/env python3
import os

from flask import (Flask, render_template, request, redirect, url_for,
                   send_from_directory, send_file)
from flask_script import Manager
from werkzeug.utils import secure_filename

from lib import asciimage

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
manager = Manager(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and\
                filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form')
def upload():
    return render_template('upload.html')


@app.route('/up', methods=['POST'])
def save_image():
    if 'photo' in request.files:
        file = request.files['photo']
        if not file.filename:
            flash('No files selected!')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        if file and allowed_file(filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('uploaded_file', filename=filename))
    return redirect(request.url)


@app.route('/success/<filename>')
def uploaded_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    asciimage_str = asciimage(filepath, maxLen=150)
    os.remove(filepath)
    return render_template('success.html', asciimage_str=asciimage_str)

if __name__ == '__main__':
    manager.run()