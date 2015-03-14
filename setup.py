"""
Flask-SessionSql
-------------

Flask-SessionSql is an extension for Flask that adds support for
Server-side Session to your application where the persistence backend
is the FlaskSQLAlchemy.

"""
from setuptools import setup


setup(
    name='Flask-SessionSql',
    version='0.1.1',
    url='https://github.com/vvutharkar/flask-sessionsql',
    license='BSD',
    author='Viswa Vutharkar',
    author_email='vutharkar@gmail.com',
    description='Adds server-side session support to your Flask application '
                'with Flask-SQLAlchemy as the persistence mechanism ',
    long_description=__doc__,
    packages=['flask_sessionsql'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.8'
    ],
    test_suite='test_session',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
