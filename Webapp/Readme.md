# Prerequisities # Local deployment and setting local proxy for cloud mysql

- installed mysql-client on local machine
		
		sudo apt-get install mysql-client

- Created clould mysql instance on google gcp, created users and other passwords other than root
- Test if it works locally with a cloud_sql_proxy (for local development before deploying the app on GAE (google app engine) )
    - At a some directory like /home/user do the following
	    
		    wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
    
		    chmod +x cloud_sql_proxy


    - Start the proxy

	        sudo mkdir /cloudsql; sudo chmod 777 /cloud_sql_proxy

        at the location you have `cloud_sql_proxy` located do the following
	        
	        ./cloud_sql_proxy -instances=<INSTANCE_CONNECTION_NAME> -dir=/clouldsql

        INSTANCE_CONNECTION_NAME can be obtained at the console page.  It should say "Ready for new connections"

    - In other terminal
		    
		    mysql -u <USERNAME> -p -S /cloudsql/<INSTANCE_CONNECTION_NAME>

          
      <USERNAME> can be obtained at the console page. If the password is correct and connection is made, then I should be able to log in to te mysql monitor. You can quit; to exit.

4) run python3 repl at /Webapp and then

	    from classifier import db
	    db.create_all()

5) In the mysql client, check the table is created
	   
	    show DATABASE;
	    use <DATABASE_NAME>
	    show tables

6) run the app python3 app.py

	this should load the /Webapp/instance/application.cfg which should has following fields

	    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://<USER>:<PWD>/<DBNAME>?unix_socket=/cloudsql/<INSTANCE_CONNECTION_NAME>'
	    SECRET_KEY = b'some randome string'
	    WTF_CSRF_SECRET_KEY = b'sme random string'
	    DEBUG=False

7) If everythins is ok, you can see the app running locally and predictions are loaded to the mysql database

# Deployment on google cloud
8) DEPLOY the app with App Engine (Didnot work out)

	 made  /Webapp/app.yaml

		gcloud app deploy.
    
    gave errors with memory

    This seems to be a bug and the solution from https://issuetracker.google.com/issues/129913216 is being pursued

9) Created Dockerfile and executed the following

	    gcloud builds submit --tag gcr.io/furnitue-image-classifier/docker_build_image1

    Even this didnot work. Gave memory error while building torch


8) Cloud run seems to work .

    Made Dockerfile and .dockerignore file in the source code and ran the steps shows at
		    
		    https://cloud.google.com/run/docs/quickstarts/build-and-deploy?hl=da

    The app seems to be woke fine. Make sure to see the service logs to see problems specific to the execution of app in production.






- Before running the flask app 

    - Make a folder ../Webapp/instance/uploads, this is not version controlled and specific to an instance 

    - If the app needs to put into production, create a file name called ../Webapp/instance/application.cfg with the following lines in it. The database uri is specific to google cloud mysql instance. 
	    

            SQLALCHEMY_DATABASE_URI ='mysql+pymysql://<USER>:<PWD>/<DBNAME>?unix_socket=/cloudsql/<INSTANCE_CONNECTION_NAME>'
	        SECRET_KEY = b'some randome string'
	        WTF_CSRF_SECRET_KEY = b'sme random string'
	        DEBUG=False


    - For SQLITE ONLY (if not connecting to mysql database), Inside the venv,when you run python3 run_app.py for the first time it will create a database images.db, but when you do prediction, there may be sqlalchemy error saying no table found. The table need to be created for the first time. go to python3 repl and issue following command

            from classifier import db 
            db.create_all()
            exit()

# Local deployment and setting local proxy for cloud mysql

- installed mysql-client on local machine

		sudo apt-get install mysql-client

- Created clould mysql instance on google gcp, created users and other passwords other than root
- Test if it works locally with a cloud_sql_proxy (for local development before deploying the app on GAE (google app engine) )
    - At a some directory like /home/user do the following

		    wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy

		    chmod +x cloud_sql_proxy


    - Start the proxy

	        sudo mkdir /cloudsql; sudo chmod 777 /cloud_sql_proxy

        at the location you have `cloud_sql_proxy` located do the following

	        ./cloud_sql_proxy -instances=<INSTANCE_CONNECTION_NAME> -dir=/clouldsql

        INSTANCE_CONNECTION_NAME can be obtained at the console page.  It should say "Ready for new connections"

    - In other terminal

		    mysql -u <USERNAME> -p -S /cloudsql/<INSTANCE_CONNECTION_NAME>


      <USERNAME> can be obtained at the console page. If the password is correct and connection is made, then I should be able to log in to te mysql monitor. You can quit; to exit.

4) Create the table for the first time, run python3 repl at /Webapp and then

	    from classifier import db
	    db.create_all()

5) In the mysql client, check the table is created

	    show DATABASE;
	    use <DATABASE_NAME>
	    show tables

6) run the app python3 app.py

	this should load the /Webapp/instance/application.cfg which should has following fields

7) If everythins is ok, you can see the app running locally and predictions are loaded to the mysql database

# Deployment on google cloud
8) DEPLOY the app with App Engine (Didnot work out)

	 made  /Webapp/app.yaml

		gcloud app deploy.

    gave errors with memory

    This seems to be a bug and the solution from https://issuetracker.google.com/issues/129913216 is being pursued

9) Created Dockerfile and executed the following

	    gcloud builds submit --tag gcr.io/furnitue-image-classifier/docker_build_image1

    Even this didnot work. Gave memory error while building torch


8) Cloud run seems to work .

    Made Dockerfile and .dockerignore file in the source code and ran the steps shows at

		    https://cloud.google.com/run/docs/quickstarts/build-and-deploy?hl=da

    The app seems to be woke fine. Make sure to see the service logs to see problems specific to the execution of app in production.






