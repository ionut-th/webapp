

#  BAZAAR WEB APP Final Project for CS50 HarvardX course
#### Video Demo:  <URL HERE>
#### Description:
BAZAAR is a website where people post or search various announcements for job, selling used items or lost / found items.

The website uses Python and Flask for backend with SQLAlchmey, SQLite database, and HTML/CSS with Bootstrap 5 on frontend.
I chose bootstrap instead of manual HTML/CSS which allowed me faster prototyping and the usage of bootstrap themes. The theme i used can be found on this page https://bootswatch.com/ and its called "Sketchy"

The project uses a python virtual environment for separation of python install from project python files.
Link for zipped complete python project with venv and setup > LINK TODO

# Project Files:
#### app.py
This is the main flask application file, it contains all routes and web app setup.

#### sqlbase.py
Contains mapping of database tables to python sqlalchemy class.

#### Templates Folder
- layout.html is the base layout of all website pages, it contains the navigation bar functions.
- index, login, changepass, myposts, newpost, register, search  HTML files inherit from layout.html and each contain a different body code.


