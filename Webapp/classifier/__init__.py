from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config.update(
    dict(SECRET_KEY="powerful secretkey",
         WTF_CSRF_SECRET_KEY="a csrf secret key"))
db = SQLAlchemy(app)
from classifier import routes
