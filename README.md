#  BAZAAR WEB APP Final Project for CS50 HarvardX course
#### Video Demo:  <URL HERE>
#### Description:
BAZAAR is a website where people post or search various announcements for job, selling used items or lost / found items.
Users can post or search by category to make it easier.

The website uses Python and Flask for backend with SQLAlchmey, SQLite database, and HTML/CSS with Bootstrap 5 on frontend.
I chose bootstrap instead of manual HTML/CSS which allowed me faster prototyping and the usage of bootstrap themes. The theme i used can be found on this page https://bootswatch.com/ and its called "Sketchy"

The project uses a python virtual environment for separation of python install from project python files.
Link for zipped complete python project with venv and setup > https://drive.google.com/file/d/1zefh03Wk2KvX_NKmcZn38i1pIu6Dg9QT/view?usp=sharing

# Project Files:
#### app.py
This is the main flask application file, it contains all routes and web app setup.

#### sqlbase.py
Contains mapping of database tables to python sqlalchemy class.

#### Templates Folder
- layout.html is the base layout of all website pages, it contains the navigation bar functions.
- index, login, changepass, myposts, newpost, register, search  HTML files inherit from layout.html and each contain a different body code.

#### Requirements
- Python 3.9.x
- Python virtualenv
- Python libs: flask, slqalchemy, flask_session, wekzeug
#### NOTE
In oreder to run the flask server and test the website you have to download the zipped project that includes all the setup.
Steps:
- Download project.zip from shared link here https://drive.google.com/file/d/1zefh03Wk2KvX_NKmcZn38i1pIu6Dg9QT/view?usp=sharing
- Unzip the archive
- Go into webapp folder
- Open or navigate your terminal to webapp folder
- Activate the virtual environment (I used git bash terminal on windows 10 ) run "source ./venv/scripts/activate"
- Then export flask variables 1. "export FLASK_ENV=production" (or "development") 2. "export FLASK_APP=flaskr/app.py"
- Then run the server locally using:  flask run
- Go to http://127.0.0.1:5000/ to see and test the webapp

