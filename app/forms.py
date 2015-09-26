# -*- coding: UTF-8 -*-

from wtforms import Form, StringField, TextAreaField, validators


__author__ = 'Ben Butzow'


class PasteForm(Form):
    title = StringField("Title (Optional)")
    text = TextAreaField("", [validators.Length(min=1)])
