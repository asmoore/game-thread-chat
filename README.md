# Introduction

This is a site that turns game threads into a live chat room.

The major dependencies are flask, SQLAlchemy, flask-socketIO, and praw.

#How the site works

##app.py

App.py runs the web server. A thread is used to continuously emit comments. Currently it short-polls the database, which isn't ideal. Using sqlalchemy events is an update I plan to make.

##initiate.py

Initiate the SQLAlchemy database.

##models.py

There is a one-to-many relation for the database. For each Game there are many Comment objects.

##Tasks.py

These are all backend tasks that are run periodicially. On Heroku, Task Scheduler is used to run them daily, hourly, or every ten minutes.

##Utils.py

These are all the utility functins used to:

* fetch JSON data from reddit or NBA.com

* get lists from the database