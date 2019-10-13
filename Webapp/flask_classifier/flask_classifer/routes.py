import json
from pathlib import Path
from urllib.parse import urlparse
import numpy as np
import requests
from flask import (flash, redirect, render_template, request,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename

from flask_classifer import app, db, prediction
from flask_classifer.forms_models import (URL, ImageForm, ImageModel,
                                          UserSubmissionForm)


@app.route('/', methods=['GET', 'POST'])
def home():
    ''' Landing Page '''
    Image_form = ImageForm()
    url_form = URL()

    def predict_add_to_db(image_bytes):
        ''' Makes Prediction and add the prediction to database'''
        predicted_class, probabilities = prediction.get_prediction(image_bytes)
        db.session.add(
            ImageModel(filename=filename,
                        probabilities=json.dumps(probabilities),
                        predicted_class=predicted_class))
        db.session.commit()
        flash(f"Image has been successfully uploaded and predicted",
              'success')

    def add_randint(filename):
        ''' Takes filename of Path type and adds a random number at the end of
        filename'''
        return filename.stem + str(np.random.randint(
            low=1, high=1E6)) + filename.suffix

    if Image_form.validate_on_submit():
        filename = Path(secure_filename(Image_form.upload.data.filename))
        filename = add_randint(filename)
        img_filepath = Path(app.instance_path) / 'uploads' / filename
        Image_form.upload.data.save(str(img_filepath))
        predict_add_to_db(Image_form.upload.data)
        return redirect(url_for('prediction_result', filename=filename))

    elif url_form.validate_on_submit():
        filename = Path(urlparse(url_form.URL_str.data).path)
        filename = add_randint(filename)
        img_filepath = Path(app.instance_path) / 'uploads' / filename
        headers = {
            'user-agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }
        r = requests.get(url_form.URL_str.data, headers)
        with open(img_filepath, 'wb') as f:
             f.write(r.content)
        predict_add_to_db(img_filepath)
        return redirect(url_for('prediction_result', filename=filename))

    return render_template('home.html',
                           title='home',
                           url_form=url_form,
                           form=Image_form)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    ''' Sends the filepath of filename '''
    filepath = send_from_directory(app.instance_path, 'uploads/' + filename)
    return filepath


@app.route('/prediction', methods=['GET', 'POST'])
def prediction_result():
    ''' Displays the prediction result and takes input from user if the prediction is wrong '''
    user_form = UserSubmissionForm()
    filename = request.args.get('filename')
    data = ImageModel.query.filter_by(filename=filename).first()
    if user_form.validate_on_submit():
        user_input = user_form.selection.data
        data.user_input = user_input
        db.session.commit()
        flash(f'Thank you for giving your feedback.', 'success')
        return redirect(url_for('prediction_result', filename=filename))

    return render_template('prediction.html',
                           title='Prediction',
                           form=user_form,
                           filename=data.filename,
                           predicted_class=data.predicted_class,
                           probabilities=json.loads(data.probabilities))
