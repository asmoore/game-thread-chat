#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
tasks.py
--------------

Tasks functions for Game Thread Chat.

"""
import sys
import os
import time
from datetime import datetime, timedelta
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists

import utils
from models import *


def add_games():
    """Initiate today's games."""
    ## Make sure that the production server is set to EST timezone
    today = datetime.today().strftime('%Y%m%d')
    game_list = utils.fetch_game_list(today)
    for game in game_list:
        game_id = game["id"]
        # Don't add the game if it already exists
        if db.session.query(Game).filter_by(game_id=game_id).first():
            pass
        else:
            thread_id = ""
            game_date = today
            home_key = game["home"]["team_key"]
            visitor_key = game["visitor"]["team_key"]
            home_name = game["home"]["nickname"]
            visitor_name = game["visitor"]["nickname"]
            home_score = game["home"]["score"]
            visitor_score = game["visitor"]["score"]
            game_status = game["period_time"]["game_status"]
            game_time = game["time"]
            game_location = game["arena"]+", "+game["city"]+", "+game["state"]
            period_value = game["period_time"]["period_status"]
            new_game = Game(game_id=game_id, thread_id=thread_id,
                            game_date=game_date, home_key=home_key,
                            visitor_key=visitor_key,home_name=home_name,
                            visitor_name=visitor_name,home_score=home_score,
                            visitor_score=visitor_score,game_status=game_status,
                            game_time=game_time,game_location=game_location,
                            period_value=period_value)
            db.session.add(new_game)
    db.session.commit()
    return True


def run_updates():
    """
    run comment and boxscore updates every "sleep_time" seconds. 

    I need to do this because Heroku's task scheduler will run a job as 
    frequently as every 10 minutes. Schedule this task which will run for 10 
    minutes and then Heroku will kill it when it runs again.
    
    """

    sleep_time = 5
    while True:
        update_thread_ids()
        update_comments()
        update_games()
        time.sleep(sleep_time)
    return True


def update_comments():
    """Update comments for each game."""
    today = datetime.today().strftime('%Y%m%d')
    games = db.session.query(Game).filter_by(game_date=today).all()
    for game in games:
        if game.thread_id == "":
            pass
        else:
            JSONcomments = json.loads(utils.fetch_comments(game.thread_id))
            for JSONcomment in JSONcomments:
                match = False
                for comment in game.comments:
                    if comment.comment_id == JSONcomment["comment_id"]:
                        match = True
                if match == False:
                    comment = Comment(author = JSONcomment["author"],
                                      body = JSONcomment["body"],
                                      author_flair_css_class = JSONcomment["author_flair_css_class"], 
                                      comment_id = JSONcomment["comment_id"], 
                                      score = JSONcomment["score"],
                                      created_utc = JSONcomment["created_utc"],
                                      emitted = "false")
                    game.comments.append(comment)  
        db.session.commit()
    return True


def update_comments_all():
    """Update comments for each game."""
    new_comments = json.loads(utils.fetch_comments_all())
    today = datetime.today().strftime('%Y%m%d')
    games = db.session.query(Game).filter_by(game_date=today).all()
    for new_comment in new_comments:
        for game in games:
            if new_comment["thread_id"] == game.thread_id:
                if db.session.query(exists().where(Comment.comment_id==new_comment["comment_id"])).scalar():
                    pass
                else:            
                    comment = Comment(author = new_comment["author"],
                                      body = new_comment["body"],
                                      author_flair_css_class = new_comment["author_flair_css_class"], 
                                      comment_id = new_comment["comment_id"], 
                                      score = new_comment["score"],
                                      created_utc = new_comment["created_utc"],
                                      emitted = "false")
                    game.comments.append(comment)  
    db.session.commit()
    return True


def update_games():
    """update the scores and game status for each game."""
    date = datetime.today().strftime('%Y%m%d')
    game_list = utils.fetch_game_list(date)
    for game in game_list:
        game_id = game["id"]
        gameDB = db.session.query(Game).filter_by(game_id=game_id).first()            
        if gameDB:
            gameDB.home_score = game["home"]["score"]
            gameDB.visitor_score = game["visitor"]["score"]
            gameDB.game_status = game["period_time"]["game_status"]
            gameDB.period_value = game["period_time"]["period_status"]
    db.session.commit()
    return True


def update_thread_ids():
    """Update thread_id for each game."""
    today = datetime.today().strftime('%Y%m%d')
    games = db.session.query(Game).filter_by(game_date=today).all()
    for game in games:
        if game.thread_id == "":
            thread_id = utils.fetch_thread_id(game.home_name,game.visitor_name)
            game.thread_id = thread_id
        else:
            pass
    db.session.commit()
    return True


if __name__ == '__main__':
    engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)    
    session = Session()
    session._model_changes = {}

    if '-add_games' in sys.argv:
        add_games()
    elif '-update_scores' in sys.argv:
        update_scores()
    elif '-update_comments' in sys.argv:
        update_comments()
    elif '-update_games' in sys.argv:
        update_games()
    elif '-run_updates' in sys.argv:
        run_updates()
    else:
        print "no arguments"
