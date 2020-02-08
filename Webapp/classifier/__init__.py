from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='static', template_folder='templates',instance_relative_config=True)
app.config.from_object('classifier.default_settings')
app.config.from_pyfile('application.cfg', silent=True)
db = SQLAlchemy(app)
from classifier import routes
