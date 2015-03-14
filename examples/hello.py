# -*- coding: utf-8 -*-
"""
    Hello
    ~~~~~

    Flask-SessionSql demo.

    :copyright: (c) 2014 by Viswa Vutharkar.
    :license: BSD, see LICENSE for more details.
"""
from flask import Flask, session
from flask.ext.session import Session


SESSION_TYPE = 'flask-sqlalchemy'


app = Flask(__name__)
app.config.from_object(__name__)
Session(app)


@app.route('/set/')
def set():
    session['key'] = 'value'
    return 'ok'


@app.route('/get/')
def get():
    return session.get('key', 'not set')


if __name__ == "__main__":
    app.run(debug=True)
