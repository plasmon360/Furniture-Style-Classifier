import json
from urllib.parse import urlparse
import requests
from urllib.request import urlretrieve
from flask import (flash, redirect, render_template, request,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename
from flask_classifer import app, db, prediction
from flask_classifer.forms_models import URL, PhotoForm, PhotoUpload, User_submission_form
import numpy as np
from pathlib import Path

@app.route('/', methods=['GET', 'POST'])
def home():
    ''' Landing Page '''
    form = PhotoForm()
    url_form = URL()

    def predict_add_to_db(image_bytes):
        ''' Makes Prediction and add the prediction to database'''
        predicted_class, probabilities = prediction.get_prediction(image_bytes)
        db.session.add(
            PhotoUpload(filename=filename,
                        probabilities=json.dumps(probabilities),
                        predicted_class=predicted_class))
        db.session.commit()
        flash(f"{filename} has been successfully uploaded and predicted",
              'success')

    def add_randint(filename):
        ''' Takes filename of Path type and adds a random number at the end of
        filename'''
        return filename.stem + str(np.random.randint(low=1, high=1E6)) + filename.suffix

    if form.validate_on_submit():
        filename = Path(secure_filename(form.upload.data.filename))
        filename = add_randint(filename)
        img_filepath = Path(app.instance_path)/'uploads'/filename
        form.upload.data.save(str(img_filepath))
        predict_add_to_db(form.upload.data)
        return redirect(url_for('prediction_result', filename=filename))

    elif url_form.validate_on_submit():
        filename = Path(urlparse(url_form.URL_str.data).path)
        filename = add_randint(filename)
        img_filepath = Path(app.instance_path)/'uploads'/filename
        r = requests.get(url_form.URL_str.data, headers = {        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',})
        with open(img_filepath,'wb') as f:
            f.write(r.content)
        #img_filepath, _ = urlretrieve(url_form.URL_str.data,
        #                              filename=img_filepath)
        predict_add_to_db(img_filepath)
        return redirect(url_for('prediction_result', filename=filename))

    return render_template('home.html',
                           title='home',
                           url_form=url_form,
                           form=form)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    ''' Sends the filepath of filename '''
    filepath = send_from_directory(app.instance_path, 'uploads/' + filename)
    return filepath


@app.route('/prediction')
def prediction_result():
    ''' Displays the prediction result'''
    filename = request.args.get('filename')
    data = PhotoUpload.query.filter_by(filename=filename).first()
    if (data.predicted_class != 'Unable to predict'):
        return render_template('prediction.html',
                               title='Prediction',
                               form=User_submission_form(),
                               filename=data.filename,
                               predicted_class=data.predicted_class,
                               probabilities=json.loads(data.probabilities))
    else:
        return render_template('prediction.html',
                               title='Prediction',
                               form=User_submission_form(),
                               filename=data.filename,
                               predicted_class=data.predicted_class)
