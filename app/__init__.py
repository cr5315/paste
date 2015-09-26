# -*- coding: UTF-8 -*-

import os

from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

__author__ = "cr5315"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATETIME_NEVER = datetime(year=1970, month=1, day=1)
DB_FILENAME = "paste.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, DB_FILENAME)
db = SQLAlchemy(app)

import views
