#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
views.py
--------------

Main views for Game Thread Chat.

"""

from gevent import monkey
monkey.patch_all()

from datetime import datetime, timedelta
import time
import os
import json
import sys

from flask import Flask, flash, render_template, session, request, redirect, url_for, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import praw

from models import *
import utils

from gamethreadchat import app

#######################
#### configuration ####
#######################


sockets = Sockets(app)

REDIRECT_URL = os.environ['REDIRECT_URL']
GTC_CLIENT_ID = os.environ['GTC_CLIENT_ID']
GTC_SECRET = os.environ['GTC_SECRET']

r = praw.Reddit('OAuth gamethread chat by /u/catmoon')
r.set_oauth_app_info(GTC_CLIENT_ID, GTC_SECRET, REDIRECT_URL)

#######################
#### routes ####
#######################


@sockets.route('/echo')
def echo_socket(ws):
    while True:
        time.sleep(2)
        today = datetime.today().strftime('%Y%m%d')
        games = db.session.query(Game).filter_by(game_date = today).all()        
        for game in games:
            if game.scoreJSON:
                scoreJSON = json.loads(game.scoreJSON)
                ws.send({'message': scoreJSON, 'category': 'score', 'thread': game.thread_id})
            if game.comments:
                for comment in game.comments:
                    if comment.emitted == "true":
                        pass
                    else:
                        comment.emitted = "true"
                        comment_dict = {"author": comment.author, 
                                     "body": comment.body, 
                                     "author_flair_css_class": comment.author_flair_css_class, 
                                     "comment_id": comment.id, 
                                     "score": comment.score,
                                     "created_utc": comment.created_utc, 
                                     "emitted": "true"}
                        message = json.dumps({'message': comment_dict,'category':'comment', 'thread': 'asda'})
                        ws.send(message)
        db.session.commit()


#OAuth2 with reddit 
@app.route("/auth/", methods = ['GET'])
def auth():
    code = request.args.get('code', '')
    info = r.get_access_information(code)
    r.set_access_credentials(**info)
    user = r.get_me()
    session['access_token'] = info['access_token']
    session['refresh_token'] = info['refresh_token']
    session['username'] = user.name
    session['logged_in'] = True    
    return redirect(url_for('home'))


#Home page
@app.route("/", methods = ['GET'])
def home():
    authorize_url = r.get_authorize_url('DifferentUniqueKey','identity edit submit',refreshable = True)
    today = datetime.today().strftime('%Y%m%d')
    yesterday = (datetime.now()-timedelta(1)).strftime('%Y%m%d')
    games = db.session.query(Game).filter_by(game_date = today).all()
    gameslist = [];
    top_users = utils.get_top_users(yesterday)
    top_scorers = utils.get_top_scorers(yesterday)
    for game in games:
        gameslist.append({"game_date": game.game_date, 
                    "home_key": game.home_key,
                    "visitor_key": game.visitor_key,
                    "home_name": game.home_name,
                    "visitor_name": game.visitor_name,
                    "home_score": game.home_score,
                    "visitor_score": game.visitor_score,
                    "game_status": game.game_status,
                    "game_time": game.game_time,
                    "game_location": game.game_location,
                    "period_value": game.period_value,
                    "game_id": game.id,
                    "thread_id": game.thread_id})
    return render_template("home.html", gameslist = gameslist, authorize_url = authorize_url, top_users = top_users, top_scorers = top_scorers)


#Chat page
@app.route("/chat/<thread_id>/", methods = ['GET'])
def chat(thread_id):
    authorize_url = r.get_authorize_url('DifferentUniqueKey',{'identity','edit','submit'},refreshable = True)
    games = db.session.query(Game).filter_by(thread_id = thread_id).all()
    comment_list = []
    for game in games: 
        if game.comments:
            for comment in game.comments:
                comment_dict = {"author": comment.author, 
                             "body": comment.body, 
                             "author_flair_css_class": comment.author_flair_css_class, 
                             "comment_id": comment.comment_id, 
                             "score": comment.score,
                             "created_utc": comment.created_utc, 
                             "emitted": "true"}
                comment_list.append(comment_dict)
    comment_list = sorted(comment_list, key = lambda k: k['created_utc'], reverse = True) 
    return render_template("chat.html", thread_id = thread_id,
                            home_key = game.home_key, visitor_key = game.visitor_key,
                            home_name = game.home_name, visitor_name = game.visitor_name,
                            home_score = game.home_score, visitor_score = game.visitor_score,
                            comment_list = comment_list, authorize_url = authorize_url)    


@app.route("/submit/", methods = ['GET','POST'])
def submit():
    if request.method == "POST":
        comment_text = request.json['comment']
        thread_id = request.json['thread_id']
        parent_id = request.json['parent_id']
        if comment_text == "":
            return jsonify(success = 0, error_msg = "try typing something!")
        else:
            if parent_id == "":
                utils.create_top_level_comment(thread_id, session['access_token'], session['refresh_token'], comment_text)
            else:
                utils.create_child_comment(thread_id, session['access_token'], session['refresh_token'], comment_text, parent_id)
    return jsonify(success = 1)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

