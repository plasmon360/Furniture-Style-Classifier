from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, TextAreaField, validators
from flask_classifer import db


class PhotoForm(FlaskForm):
    ''' Form for uploading a photo'''
    upload = FileField(label='Upload Furniture Picture',
                       validators=[
                           FileRequired(),
                           FileAllowed(['png', 'jpg', 'jpeg'], 'Images only!')
                       ])
    submit = SubmitField('Submit File')


class URL(FlaskForm):
    ''' Form for submitting an URL'''
    URL_str = TextAreaField(label='URL', validators=[validators.URL()])
    submit = SubmitField('Submit URL')


class PhotoUpload(db.Model):
    '''Data model for uploaded photo or URL'''
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(20), unique=False, nullable=False)
    uploaded_time = db.Column(db.DateTime(), default=datetime.utcnow)
    probabilities = db.Column(db.String(100), unique=False, nullable=True)
    predicted_class = db.Column(db.String(20), unique=False, nullable=True)
    user_input = db.Column(db.String(20), unique=False, nullable=True)

    def __repr__(self):
        return f"{self.filename}: Uploaded: {self.uploaded_time}"
