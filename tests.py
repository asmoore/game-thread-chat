#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
tests.py
--------------

Tests for the Game Thread Chat.

"""
import unittest
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import utils
import tasks
from models import *

class UtilsTest(unittest.TestCase):

	def test_fetch_box(self):
		utils.fetch_box("20150206","0021400757")


	def test_fetch_comments(self):
		utils.fetch_comments("2v1ww7")


	def test_fetch_comments_all(self):
		utils.fetch_comments_all()


	def test_fetch_game_list(self):
		utils.fetch_game_list("20150206")


	def test_fetch_thread_id(self):
		utils.fetch_thread_id("Miami", "San Antonio")


	def test_get_top_scorers(self):
		utils.get_top_scorers("20150206")


	def test_get_top_users(self):
		utils.get_top_users("20150206")


class TasksTest(unittest.TestCase):

	def test_add_games(self):
		tasks.add_games()


	def test_update_comments(self):
		tasks.update_comments()


	def test_update_comments_all(self):
		tasks.update_comments_all()


	def test_update_games(self):
		tasks.update_games()


	def test_update_thread_ids(self):
		tasks.update_thread_ids()


if __name__ == '__main__':
	engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])
	Session = sessionmaker(bind=engine)    
	session = Session()
	session._model_changes = {}
	unittest.main()

