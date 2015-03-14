# -*- coding: utf-8 -*-
"""
    flaskext.session.sessions
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Server-side Sessions and SessionInterfaces.

    :copyright: (c) 2014 by Shipeng Feng.
    :license: BSD, see LICENSE for more details.

    :copyright: (c) 2015  Viswa Vutharkar
    :license: BSD, see LICENSE for more details.
"""

from datetime import datetime
from uuid import uuid4
try:
    import cPickle as pickle
except ImportError:
    import pickle

from flask.sessions import SessionInterface, SessionMixin
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.datastructures import CallbackDict


class ServerSideSession(CallbackDict, SessionMixin):
    """Baseclass for server-side based sessions."""
    
    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.permanent = True
        self.modified = False


class FlaskSQLAlchemySession(ServerSideSession):
    pass


class NullSessionInterface(SessionInterface):
    """Used to open a :class:`flask.sessions.NullSession` instance.
    """
    
    def open_session(self, app, request):
        return None


class FlaskSQLAlchemySessionInterface(SessionInterface):
    """Uses the Flask-SQLAlchemy from a flask app as a session backend.

    :param app: A Flask App instance.
    :param key_prefix: A prefix that is added to all store keys.
    """

    serializer = pickle
    session_class = FlaskSQLAlchemySession

    def __init__(self, app, key_prefix):
        self.app = app
        self.db = SQLAlchemy(app)
        self.key_prefix = key_prefix

        class SqlSession(self.db.Model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            session_id = self.db.Column(self.db.String(256), unique=True)
            data = self.db.Column(self.db.Text)
            expiry = self.db.Column(self.db.DateTime)

            def __init__(self, session_id, data, expiry):
                self.session_id = session_id
                self.data = data
                self.expiry = expiry

            def __repr__(self):
                return '<Session data %s>' % self.data
        self.db.create_all()
        self.sql_session_model = SqlSession

    def _generate_sid(self):
        return str(uuid4())

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            session_id = self.key_prefix + sid
            saved_session = self.sql_session_model.query.filter_by(
                session_id=session_id).first()
            if saved_session:
                if saved_session.expiry > datetime.utcnow():
                    try:
                        val = saved_session.data
                        data = self.serializer.loads(str(val))

                        return self.session_class(data, sid=sid)

                    except Exception as e:
                        print "some exception %s" % e.message
                        self.db.delete(saved_session)
                        self.db.session.commit()
                else:
                    # saved session expired. Delete it
                    self.db.delete(saved_session)
                    self.db.session.commit()

        sid = self._generate_sid()
        return self.session_class(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        if not session:
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return

        session_id = self.key_prefix + session.sid
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        new_expiry = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))

        saved_session = self.sql_session_model.query.filter_by(
            session_id=session_id).first()

        if saved_session:
            if session.modified:
                # update the saved session only if session
                # was modified since last save
                saved_session.data = val
                saved_session.expiry = new_expiry
                self.db.session.commit()
        else:
            # create new session object
            new_session = self.sql_session_model(session_id, val, new_expiry)
            self.db.session.add(new_session)
            self.db.session.commit()

        session.modified = False
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=new_expiry, httponly=httponly,
                            domain=domain, path=path, secure=secure)
