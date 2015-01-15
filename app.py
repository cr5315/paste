__author__ = "cr5315"

from datetime import datetime
import os
import string
import random

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, validators

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "paste.db")
db = SQLAlchemy(app)


class Paste(db.Model):
    num = db.Column(db.Integer, primary_key=True)
    paste_id = db.Column(db.String(5), unique=True)
    paste_date = db.Column(db.DateTime)
    paste_title = db.Column(db.Text)
    paste_text = db.Column(db.Text)

    def __init__(self, paste_id, paste_title, paste_text, paste_date=None,):
        self.paste_id = paste_id
        self.paste_title = paste_title
        self.paste_text = paste_text
        if paste_date is None:
            paste_date = datetime.now()
        self.paste_date = paste_date

    def __repr__(self):
        return "<Paste %r>" % self.paste_id


class PasteForm(Form):
    title = StringField("Title (Optional)")
    text = TextAreaField("", [validators.Length(min=1)])


def get_id(length=5):
    return "".join(random.choice(string.ascii_uppercase) for i in range(length))


def format_time(time):
    return time.strftime("%H:%M:%S %Y-%m-%d")


@app.route("/", methods=["GET"])
def main():
    return render_template("index.html", date="", title="", show_new_button=False)


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

        date = format_time(this_paste.paste_date)
        title = this_paste.paste_title
        text = this_paste.paste_text

        return render_template("paste.html", date=date, title=title, text=text, show_new_button=True)


@app.route("/new", methods=["POST"])
def new():
    form = PasteForm(request.form)
    if request.method == "POST" and form.validate():
        paste_text = request.form["text"]
        paste_title = request.form["title"]
        paste_date = datetime.now()

        paste_id = get_id()
        while len(Paste.query.filter_by(paste_id=paste_id).all()) != 0:
            paste_id = get_id()

        new_paste = Paste(paste_id=paste_id, paste_title=paste_title, paste_text=paste_text, paste_date=paste_date)
        db.session.add(new_paste)
        db.session.commit()

        return redirect("p/%s" % paste_id)
    else:
        flash("Please do not leave that field blank", "warning")
        return redirect(url_for("main"))


if __name__ == "__main__":
    app.debug = False
    app.secret_key = "JQOLZVYRILIJPQYFIQVONZAFW"
    app.run()