
Before running the app make a folder ../Webapp/flask_classifier/instance/uploads

For SQLITE

Inside the venv,when you run python3 run_app.py for the first time it will create a database images.db 

but when you do prediction, there may be sqlalchemy error saying no table found. 

The table need to be created for the first time. 

go to python3 repl and issue following command

from classifier import db 
db.create_all()
exit()


