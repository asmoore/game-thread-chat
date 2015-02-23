#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
models.py
--------------

Data models for Game Thread Chat.

"""
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

from initiate import db

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String, unique=False)
    thread_id = db.Column(db.String, unique=False)
    game_date = db.Column(db.String(8), unique=False)
    home_key = db.Column(db.String(3), unique=False)
    visitor_key = db.Column(db.String(3), unique=False)
    home_name = db.Column(db.String, unique=False)
    visitor_name = db.Column(db.String, unique=False)
    home_score = db.Column(db.String(3), unique=False)
    visitor_score = db.Column(db.String(3), unique=False)
    game_status = db.Column(db.String, unique=False)
    game_time = db.Column(db.String, unique=False)
    game_location = db.Column(db.String, unique=False)
    period_value = db.Column(db.String, unique=False)
    scoreJSON = db.Column(db.String, unique=False)
    comments = db.relationship('Comment', backref='game',
                                lazy='dynamic')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, unique=False)
    body = db.Column(db.String, unique=False) 
    author_flair_css_class = db.Column(db.String, unique=False) 
    comment_id = db.Column(db.String, unique=False) 
    score = db.Column(db.String, unique=False)
    created_utc = db.Column(db.String, unique=False)
    emitted = db.Column(db.String, unique=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))