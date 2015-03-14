import unittest

import flask
from flask.ext.session import Session


class FlaskSessionTestCase(unittest.TestCase):
    
    def test_null_session(self):
        app = flask.Flask(__name__)
        Session(app)

        def expect_exception(f, *args, **kwargs):
            try:
                f(*args, **kwargs)
            except RuntimeError as e:
                self.assertTrue(e.args and 'session is unavailable' in e.args[0])
            else:
                self.assertTrue(False, 'expected exception')
        with app.test_request_context():
            self.assertTrue(flask.session.get('missing_key') is None)
            expect_exception(flask.session.__setitem__, 'foo', 42)
            expect_exception(flask.session.pop, 'foo')

    def test_flasksqlalchemy_session(self):
        app = flask.Flask(__name__)
        app.config['SESSION_TYPE'] = 'flask-sqlalchemy'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['SECRET_KEY'] = \
            '\xfb\x12\xdf\xa1@i\xd6>V\xc0\xbb\x8fp\x16#Z\x0b\x81\xeb\x16'
        app.config['DEBUG'] = True

        Session(app)
        @app.route('/set', methods=['POST'])
        def set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'
        @app.route('/get')
        def get():
            return flask.session['value']

        c = app.test_client()
        self.assertEqual(c.post('/set', data={'value': '42'}).data, b'value set')
        self.assertEqual(c.get('/get').data, b'42')


if __name__ == "__main__":
    unittest.main()
