For local development of the app and setting proxy for cloud mysql

1) install mysql-client on local machine
sudo apt-get install mysql-client

2) Created clould mysql instance on google gcp
    create users and other passwords other than root


3) Test if it works locally with a cloud_sql_proxy (for local development before deploying the app on GAE (google app engine) )
    0) At a some directory like /home/user do the following
    1)wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
    2)chmod +x cloud_sql_proxy


    3) Start the proxy

        sudo mkdir /cloudsql; sudo chmod 777 /cloud_sql_proxy

        at the location you have cloud_sql_proxy located do the following
        ./cloud_sql_proxy -instances=<INSTANCE_CONNECTION_NAME> -dir=/clouldsql

        INSTANCE_CONNECTION_NAME can be obtained at the console page
        it should say "Ready for new connections"

    4) in other terminal
    mysql -u <USERNAME> -p -S /cloudsql/<INSTANCE_CONNECTION_NAME>

        <USERNAME> can be obtained at the console page.

        if password is correct and connection is made, then I should be able to log in to te mysql monitor. You can quit; to exit.

4) run python3 repl at /Webapp and then

    from classifier import db
    db.create_all()

5) In the mysql client

    check the table is created
    show DATABASE;
    use <DATABASE_NAME>
    show tables

6) run the app python3 run_app.py

this should load the /Webapp/instance/application.cfg which should has following fields

    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://<USER>:<PWD>/<DBNAME>?unix_socket=/cloudsql/<INSTANCE_CONNECTION_NAME>'
    SECRET_KEY = b'some randome string'
    WTF_CSRF_SECRET_KEY = b'sme random string'
    DEBUG=False

7) If everythins is ok, you can see an predictions are loaded to the database in mysql client locally



DEPLOY the app with App Engine (Didnot work out)

    make /Webapp/app.yaml

    8) Tried gcloud app deploy.
    gave errors with memory

    This seems to be a bug and the solution from https://issuetracker.google.com/issues/129913216 is being pursued

    9) Created Dockerfile and executed the following

    gcloud builds submit --tag gcr.io/furnitue-image-classifier/docker_build_image1

    Even this didnot work. Gave memory error while building torch


8) Cloud run seems to work .

    Made Dockerfile and .dockerignore file in the source code and ran the steps shows at
    https://cloud.google.com/run/docs/quickstarts/build-and-deploy?hl=da

    The app seems to be woke fine.




