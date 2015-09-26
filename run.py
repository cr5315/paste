# -*- coding: UTF-8 -*-

from app import app, db

__author__ = "cr5315"


if __name__ == "__main__":
    db.create_all()
    app.run(debug=False)
