Flask-Session
=============

.. module:: flask.ext.sessionsql

Welcome to Flask-SessionSql's documentation.  Flask-SessionSql is an extension
 for
`Flask`_ that adds support for Server-side ``Session`` to your application.
Flask 0.8 or newer is required, if you are using an older version, check
`Support for Old and New Sessions`_ out.

.. _Flask: http://flask.pocoo.org/
.. _Support for Old and New Sessions: http://flask.pocoo.org/snippets/52/

If you are not familiar with Flask, I highly recommend you to give it a try.
Flask is a microframework for Python and it is really Fun to work with.  If
you want to dive into its documentation, check out the following links:

-   `Flask Documentation <http://flask.pocoo.org/docs/>`_

Installation
------------

Install the extension with the following command::

    $ easy_install Flask-SessionSql

or alternatively if you have pip installed::
    
    $ pip install Flask-SessionSql

Quickstart
----------

Flask-SessionSql is really easy to use.

Basically for the common use of having one Flask application all you have to
do is to create your Flask application, load the configuration of choice and
then create the :class:`Session` object by passing it the application.

The ``Session`` instance is not used for direct access, you should always use
:class:`flask.session`::
    
    from flask import Flask, session
    from flask.ext.session import Session

    app = Flask(__name__)
    # Check Configuration section for more details
    SESSION_TYPE = 'flask-sqlalchemy'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    SQLALCHEMY_ECHO = False
    SECRET_KEY = \
            '\xfb\x12\xdf\xa1@i\xd6>V\xc0\xbb\x8fp\x16#Z\x0b\x81\xeb\x16'
    DEBUG = True

    app.config.from_object(__name__)
    Session(app)

    @app.route('/set/')
    def set():
        session['key'] = 'value'
        return 'ok'

    @app.route('/get/')
    def get():
        return session.get('key', 'not set')

You may also set up your application later using :meth:`~Session.init_app`
method::
    
    sess = Session()
    sess.init_app(app)

Configuration
-------------

The following configuration values exist for Flask-SessionSql.
Flask-SessionSql loads these values from your Flask application config, so you
should configure your app first before you pass it to Flask-SessionSql.  Note
that these values cannot be modified after the ``init_app`` was applyed so
make sure to not modify them at runtime.

The following configuration values are builtin configuration values within
Flask itself that are related to session.  **They are all understood by 
Flask-Session, for example, you should use PERMANENT_SESSION_LIFETIME
to control your session lifetime.**

================================= =========================================
``SESSION_COOKIE_NAME``           the name of the session cookie
``SESSION_COOKIE_DOMAIN``         the domain for the session cookie.  If
                                  this is not set, the cookie will be
                                  valid for all subdomains of
                                  ``SERVER_NAME``.
``SESSION_COOKIE_PATH``           the path for the session cookie.  If
                                  this is not set the cookie will be valid
                                  for all of ``APPLICATION_ROOT`` or if
                                  that is not set for ``'/'``.
``SESSION_COOKIE_HTTPONLY``       controls if the cookie should be set
                                  with the httponly flag.  Defaults to
                                  `True`.
``SESSION_COOKIE_SECURE``         controls if the cookie should be set
                                  with the secure flag.  Defaults to
                                  `False`.
``PERMANENT_SESSION_LIFETIME``    the lifetime of a permanent session as
                                  :class:`datetime.timedelta` object.
                                  Starting with Flask 0.8 this can also be
                                  an integer representing seconds.
================================= =========================================

A list of configuration keys also understood by the extension:

============================= ==============================================
``SESSION_TYPE``              Specifies which type of session interface to
                              use.  Built-in session types:

                              - **null**: NullSessionInterface (default)
                              - **flask-sqlalchemy**:
                              FlaskSQLAlchemySEssionInterface
``SQLALCHEMY_DATABASE_URI``   Database connection string

``SQLALCHEMY_ECHO``           See Sql Alchemy doc

============================= ==============================================

Basically you only need to configure ``SESSION_TYPE``.

.. note::
    
    All non-null sessions in Flask-SessionSql are permanent.

Built-in Session Interfaces
---------------------------

:class:`NullSessionInterface`
`````````````````````````````

If you do not configure a different ``SESSION_TYPE``, this will be used to
generate nicer error messages.  Will allow read-only access to the empty
session but fail on setting.

