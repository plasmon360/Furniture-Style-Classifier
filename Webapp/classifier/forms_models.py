from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, TextAreaField, validators, SelectField, ValidationError
from classifier import db
import requests


class ImageForm(FlaskForm):
    ''' Form for uploading a photo'''
    upload = FileField(label='Upload Furniture Picture',
                       validators=[
                           FileRequired(),
                           FileAllowed(['png', 'jpg', 'jpeg'], 'Images only!')
                       ])
    submit = SubmitField('Submit File')


def is_url_image(image_url):
    ''' validator function to check if the image url is png/jpeg/jpg without downloading whole file'''
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(
        image_url,
        headers={
            'user-agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        })
    if r.headers["content-type"] in image_formats:
        return True
    return False


class URL(FlaskForm):
    ''' Form for submitting an URL'''
    URL_str = TextAreaField(label='URL', validators=[validators.URL()], default = "https://upload.wikimedia.org/wikipedia/commons/e/e6/The_Egg_Chair.jpg")

    # Check if the url points to an image file
    def validate_URL_str(form, field):
        if not is_url_image(field.data):
            raise ValidationError('Not a valid image URL')

    submit = SubmitField('Submit URL')


class UserSubmissionForm(FlaskForm):
    ''' Form for user to submit the correct label '''
    myChoices = [('Mid-Century Modern', 'Mid-Century Modern'),
                 ('Rustic', 'Rustic'), ('Arts and Crafts', 'Arts and Crafts'),
                 ('Traditional', 'Traditional'),
                 ('Transitional', 'Transitional'), ('Other', 'Other')]
    selection = SelectField(u'Furniture Style',
                            choices=myChoices,
                            coerce=str,
                            validators=[validators.InputRequired()])
    submit = SubmitField('Submit')


class ImageModel(db.Model):
    '''Data model for uploaded photo or URL'''
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.Text, unique=False, nullable=False)
    uploaded_time = db.Column(db.DateTime(), default=datetime.utcnow)
    probabilities = db.Column(db.String(100), unique=False, nullable=True)
    predicted_class = db.Column(db.String(20), unique=False, nullable=True)
    user_input = db.Column(db.String(20), unique=False, nullable=True)

    def __repr__(self):
        return f"{self.filename}: Uploaded: {self.uploaded_time}"
