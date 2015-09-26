# -*- coding: UTF-8 -*-

from app import db, DATETIME_NEVER
from datetime import datetime


__author__ = "cr5315"


class Paste(db.Model):
    num = db.Column(db.Integer, primary_key=True)
    paste_id = db.Column(db.String(5), unique=True)
    paste_date = db.Column(db.DateTime)
    paste_expire = db.Column(db.DateTime)
    paste_language = db.Column(db.Text)
    paste_title = db.Column(db.Text)
    paste_text = db.Column(db.Text)

    def __init__(self, paste_id, paste_title, paste_text, paste_date=None, paste_expire=None, paste_language=None):
        self.paste_id = paste_id
        self.paste_title = paste_title
        self.paste_text = paste_text
        if paste_date is None:
            paste_date = datetime.now()
        self.paste_date = paste_date
        if paste_expire is None:
            paste_expire = DATETIME_NEVER
        self.paste_expire = paste_expire
        if paste_language is None:
            paste_language = "None"
        self.paste_language = paste_language

    def __repr__(self):
        return "<Paste %r>" % self.paste_id
