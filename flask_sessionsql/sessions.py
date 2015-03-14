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
        if not sid:
            sid = self._generate_sid()
            return self.session_class(sid=sid)
        session_id = self.key_prefix + sid
        record = self.sql_session_model.query.filter_by(
            session_id=session_id).first()

        sql_session = record if record and record.expiry > datetime.utcnow()\
            else None

        if sql_session is not None:
            try:
                val = sql_session.data
                data = self.serializer.loads(val)
                return self.session_class(data, sid=sid)
            except:
                return self.session_class(sid=sid)
        return self.session_class(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                session_id = self.key_prefix + session.sid
                sql_session = self.sql_session_model.query.filter_by(
                    session_id=session_id).first()

                self.db.delete(sql_session)
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain, path=path)
            return

        # Modification case.  There are upsides and downsides to
        # emitting a set-cookie header each request.  The behavior
        # is controlled by the :meth:`should_set_cookie` method
        # which performs a quick check to figure out if the cookie
        # should be set or not.  This is controlled by the
        # SESSION_REFRESH_EACH_REQUEST config flag as well as
        # the permanent flag on the session itself.
        #if not self.should_set_cookie(app, session):
        #    return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))

        sql_session = self.sql_session_model(self.key_prefix + session.sid,
                                             val, expires)
        self.db.session.add(sql_session)
        self.db.session.commit()

        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=expires, httponly=httponly,
                            domain=domain, path=path, secure=secure)
