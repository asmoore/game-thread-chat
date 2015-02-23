#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
utils.py
--------------

Utility functions for Game Thread Chat.

"""
import json
import os
import urllib2
import re
from datetime import datetime
from operator import itemgetter

import praw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import *


def create_child_comment(thread_id, access_token, refresh_token, body, parent_id):
    """Create a child comment"""
    REDIRECT_URL = "http://127.0.0.1:5000/auth"
    GTC_CLIENT_ID = os.environ['GTC_CLIENT_ID']
    GTC_SECRET = os.environ['GTC_SECRET']
    r = praw.Reddit('OAuth gamethread chat by /u/catmoon')
    r.set_oauth_app_info(GTC_CLIENT_ID, GTC_SECRET, REDIRECT_URL)
    info = {'access_token':access_token,'scope':{'identity','edit','submit'},'refresh_token':refresh_token}
    r.set_access_credentials(**info)
    submission = r.get_submission('http://www.reddit.com/r/nba/comments/'+thread_id+'/_/'+parent_id)
    parent = submission.comments[0]
    comment = parent.reply(body)
    return True


def create_top_level_comment(thread_id, access_token, refresh_token, body):
    """Create a top-level comment"""
    REDIRECT_URL = "http://127.0.0.1:5000/auth"
    GTC_CLIENT_ID = os.environ['GTC_CLIENT_ID']
    GTC_SECRET = os.environ['GTC_SECRET']
    r = praw.Reddit('OAuth gamethread chat by /u/catmoon')
    r.set_oauth_app_info(GTC_CLIENT_ID, GTC_SECRET, REDIRECT_URL)
    info = {'access_token':access_token,'scope':{'identity','edit','submit'},'refresh_token':refresh_token}
    r.set_access_credentials(**info)
    submission = r.get_submission(submission_id=thread_id)
    comment = submission.add_comment(body)
    return True


def fetch_box(date, game_id):
    """Fetch boxscore json."""
    url = "http://data.nba.com/json/cms/noseason/game/"+str(date)+"/"+str(game_id)+"/boxscore.json"
    response = urllib2.urlopen(url)
    data = response.read()
    return data


def fetch_comments():
    """Fetch comments json."""
    r = praw.Reddit(user_agent='catmoon using praw')
    comment_list = []
    subreddit = r.get_subreddit('nba')
    nba_comments = subreddit_comments = subreddit.get_comments()
    for comment in nba_comments:
        if hasattr(comment,'body'):
            try:
                comment_list.append({"author": comment.author.name, 
                                     "body": comment.body, 
                                     "author_flair_css_class": comment.author_flair_css_class, 
                                     "comment_id": comment.id, 
                                     "score": comment.score,
                                     "created_utc": comment.created_utc, 
                                     "emitted": "false",
                                     "thread_id": (comment.link_id).split("_",1)[1]})
            except:
                pass
    return json.dumps(comment_list)


def fetch_game_list(date):
    """Fetch list of games from data.nba.com"""
    url = "http://data.nba.com/json/cms/noseason/scoreboard/" + str(date) + "/games.json"
    response = urllib2.urlopen(url)
    data = json.load(response)
    return data["sports_content"]["games"]["game"]


def fetch_thread_id(home_name, visitor_name):
    """Fetch the the thread_id of a game from reddit using praw"""
    r = praw.Reddit(user_agent='catmoone using praw')
    submissions = r.get_subreddit('nba').get_hot(limit=100)
    thread_id = ""
    for submission in submissions:
        story = submission.title.encode("utf8")
        if re.search('GAME THREAD(.*)'+visitor_name+'(.*)'+home_name,str(story),re.IGNORECASE):
            thread_id = submission.id
    return thread_id


def get_top_scorers(date):
    """Get the leading scorers from games on specified date"""
    games = db.session.query(Game).filter_by(game_date=date).all()
    player_list = []
    for game in games:
        if game.scoreJSON == "":
            pass
        else:
            try:
                scoreJSON = json.loads(game.scoreJSON)
                home = scoreJSON["sports_content"]["game"]["home"]["players"]
                for player in home["player"]:
                    player["team_key"] = scoreJSON["sports_content"]["game"]["home"]["team_key"]
                    player_list.append(player)
                visitor = scoreJSON["sports_content"]["game"]["visitor"]["players"]
                for player in visitor["player"]:
                    player["team_key"] = scoreJSON["sports_content"]["game"]["visitor"]["team_key"]
                    player_list.append(player)
            except:
                return []
    sorted_players = sorted(player_list, key=lambda x: int(x["points"]))
    sorted_players = sorted_players[::-1]
    return sorted_players[0:10]


def get_top_users(date):
    """Get the leading scorers from games on specified date"""
    comments = db.session.query(Comment).all()
    user_list = []
    for comment in comments:
        for user in user_list:
            if comment.author == user["author"]:
                user["comments"] = str(int(user["comments"]) + 1)
                break
        else:
            user_list.append({"author":comment.author, "comments":"1", "author_flair_css_class": comment.author_flair_css_class})
    sorted_users = sorted(user_list, key=lambda x: int(x["comments"]))
    sorted_users = sorted_users[::-1]
    return sorted_users[0:10]


if __name__ == '__main__':
    engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)    
    session = Session()
    session._model_changes = {}

