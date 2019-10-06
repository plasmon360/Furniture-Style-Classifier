from flask import request


from werkzeug.utils import secure_filename
from flask_classifer import app, db
from flask_classifer.forms_models import PhotoForm, PhotoUpload, URL
from flask import render_template, redirect, url_for, flash, send_from_directory
import os
from pathlib import Path
from datetime import datetime
from flask_classifer import prediction
import json
from urllib.request import urlretrieve
from urllib.parse import urlparse
from PIL import Image


@app.route('/', methods=['GET', 'POST'])
def home():
    form = PhotoForm()
    url_form = URL()

    def predict_add_to_db(image_bytes):
        predicted_class, probabilities = prediction.get_prediction(image_bytes)
        db.session.add(PhotoUpload(filename=filename, probabilities=json.dumps(
            probabilities), predicted_class=predicted_class))
        db.session.commit()
        flash(f"{filename} has been successfully uploaded and predicted", 'success')

    if form.validate_on_submit():
        uploaded_file = form.upload.data
        filename = secure_filename(uploaded_file.filename)
        img_filepath = os.path.join(app.instance_path, 'uploads', filename)
        uploaded_file.save(img_filepath)
        predict_add_to_db(image_bytes=uploaded_file)
        return redirect(url_for('prediction_result', filename=filename))
    elif url_form.validate_on_submit():
        filename = os.path.basename(urlparse(url_form.URL_str.data).path)
        img_filepath = os.path.join(app.instance_path, 'uploads', filename)
        img_filepath, _ = urlretrieve(
            url_form.URL_str.data, filename=img_filepath)
        predict_add_to_db(img_filepath)
        return redirect(url_for('prediction_result', filename=filename))

    return render_template('home.html', title='home', url_form=url_form, form=form)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filepath = send_from_directory(app.instance_path, 'uploads/'+filename)
    return filepath


@app.route('/prediction')
def prediction_result():
    filename = request.args.get('filename')
    data = PhotoUpload.query.filter_by(filename=filename).first()
    return render_template('prediction.html', title='Prediction', filename=data.filename, predicted_class=data.predicted_class, probabilities=json.loads(data.probabilities))
