# -*- coding: UTF-8 -*-

import json
import os
import random
import re
import string

from app import app, db, BASE_DIR, DATETIME_NEVER
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import flash, redirect, render_template, request, url_for
from forms import PasteForm
from jinja2 import evalcontextfilter, Markup, escape
from models import Paste


__author__ = "cr5315"


try:
    with open(os.path.join(BASE_DIR, "static", "languages.json"), "r") as f:
        LANGUAGES = json.load(f)
except IOError:
    LANGUAGES = ["None"]


_paragraph_re = re.compile(r"(?:\r\n|\r|\n){2,}")


def get_id(length=5):
    return "".join(random.choice(string.ascii_uppercase) for _ in range(length))


def format_time(time):
    return time.strftime("%H:%M:%S %Y-%m-%d")


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    # http://stackoverflow.com/a/21167889/446875
    result = u"\n".join(u"%s" % p.replace("\n", "<br>\n") for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@app.route("/", methods=["GET"])
def main():
    return render_template("index.html", languages=LANGUAGES, show_new_button=False)


@app.route("/p/")
def paste_redirect():
    return redirect(url_for("main"))


@app.route("/p/<string:paste_id>")
def paste(paste_id=None):
    if paste_id is None:
        return redirect(url_for("main"))
    else:
        this_paste = Paste.query.filter_by(paste_id=paste_id).first()

        if this_paste is None:
            return redirect(url_for("main"))

        expires = this_paste.paste_expire
        if expires != DATETIME_NEVER and datetime.now() > expires:
            flash("This paste has expired", "warning")
            return redirect(url_for("main"))
        elif expires != DATETIME_NEVER:
            expires = "Expires: %s" % format_time(expires)
        else:
            expires = "Expires: Never"

        date = "Created: %s" % format_time(this_paste.paste_date)
        language = "Language: %s" % str(this_paste.paste_language)
        clazz = "paste %s" % this_paste.paste_language.lower()
        title = this_paste.paste_title
        text = this_paste.paste_text

        return render_template("paste.html", date=date, expires=expires, title=title, text=text, language=language,
                               clazz=clazz, show_new_button=True)


@app.route("/new", methods=["POST"])
def new():
    form = PasteForm(request.form)
    if request.method == "POST" and form.validate():
        paste_text = request.form["text"]
        paste_title = request.form["title"]
        paste_date = datetime.utcnow()
        paste_language = request.form["language"]

        paste_expire = request.form["expires"].lower()
        if paste_expire == "1 hour":
            paste_expire = datetime.now() + relativedelta(hours=1)
        elif paste_expire == "6 hours":
            paste_expire = datetime.now() + relativedelta(hours=6)
        elif paste_expire == "12 hours":
            paste_expire = datetime.now() + relativedelta(hours=12)
        elif paste_expire == "1 day":
            paste_expire = datetime.now() + relativedelta(days=1)
        elif paste_expire == "1 week":
            paste_expire = datetime.now() + relativedelta(weeks=1)
        else:
            paste_expire = DATETIME_NEVER

        paste_id = get_id()
        while len(Paste.query.filter_by(paste_id=paste_id).all()) != 0:
            paste_id = get_id()

        new_paste = Paste(paste_id=paste_id, paste_title=paste_title, paste_text=paste_text, paste_date=paste_date,
                          paste_expire=paste_expire, paste_language=paste_language)
        db.session.add(new_paste)
        db.session.commit()

        return redirect("p/%s" % paste_id)
    else:
        flash("Please do not leave that field blank", "warning")
        return redirect(url_for("main"))


@app.route("/list")
def list_pastes():
    pastes = Paste.query.order_by(Paste.paste_date).all()
    return render_template("list.html", pastes=pastes, show_new_button=True)


@app.template_filter("date")
def _jinja2_date_filter(date, fmt=None):
    if date != DATETIME_NEVER:
        return "%s" % format_time(date)
    else:
        return "Never"
