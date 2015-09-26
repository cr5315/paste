from datetime import datetime
import os
import string
import random
import re

from dateutil.relativedelta import relativedelta
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from jinja2 import evalcontextfilter, Markup, escape
from wtforms import Form, StringField, TextAreaField, validators


__author__ = "cr5315"


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATETIME_NEVER = datetime(year=1970, month=1, day=1)
DB_FILENAME = "paste.db"
LANGUAGES = []
_paragraph_re = re.compile(r"(?:\r\n|\r|\n){2,}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, DB_FILENAME)
db = SQLAlchemy(app)

try:
    with open("languages.txt", "r") as f:
        for line in f:
            LANGUAGES.append(line)
except IOError:
    LANGUAGES = ["None"]


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


class PasteForm(Form):
    title = StringField("Title (Optional)")
    text = TextAreaField("", [validators.Length(min=1)])


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


if __name__ == "__main__":
    app.debug = True
    app.secret_key = "JQOLZVYRILIJPQYFIQVONZAFW"
    app.run()
