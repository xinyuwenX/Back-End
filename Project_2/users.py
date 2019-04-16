#Dev 1​ owns the Articles and Users microservices and HTTP Basic Authentication.
from functools import wraps
import flask
from flask import request, Response, jsonify
from flask_basicauth import BasicAuth
import sqlite3
import logging


# logging.basicConfig(level=logging.DEBUG)
app = flask.Flask(__name__)
app.config["DEBUG"] = True

class customAuth (BasicAuth):
    def check_credentials(self, username, password):
        #werkzeug.security.generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        # get password from DB and determine if this person is truly the account owner
        app.config['BASIC_AUTH_USERNAME'] = username
        app.config['BASIC_AUTH_PASSWORD'] = password
        return True

basic_auth = customAuth(app)

@app.route('/users', methods=['GET'])
@basic_auth.required
def home():
    return '''<h1>Welcome to Project 2 in users</h1>'''

@app.route('/users/create', methods=['POST'])
@basic_auth.required
def createUser():

    conn = sqlite3.connect('users.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    name = app.config['BASIC_AUTH_USERNAME']
    email = name

    query1 = '''SELECT * FROM users WHERE email = ?;'''
    to_filter1 = [email]

    account_check = cur.execute(query1, to_filter1).fetchone()

    accountName = ''

    if account_check:
        accountName = account_check.get("email")

    if accountName != app.config['BASIC_AUTH_USERNAME']:

        query2 = '''INSERT INTO users (name, email, password) values (?,?,?);'''
        to_filter2 = [app.config['BASIC_AUTH_USERNAME'], email, app.config['BASIC_AUTH_PASSWORD']]
        response = cur.execute(query2, to_filter2).fetchone()
        conn.commit()
        return Response('User created successfully.', 200, {})
    else:
        error_401()

    

@app.route('/users/delete', methods=['POST'])
@basic_auth.required
def deleteUser():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    name = app.config['BASIC_AUTH_USERNAME']
    email = name

    query1 = '''SELECT * FROM users WHERE email = ?;'''
    to_filter1 = [name]

    account_check = cur.execute(query1, to_filter1).fetchone()

    accountName = ''

    if account_check:
        accountName = account_check.get("name")

    if accountName == app.config['BASIC_AUTH_USERNAME']:

        query2 = '''DELETE FROM users WHERE name=?;'''

        to_filter2 = [app.config['BASIC_AUTH_USERNAME']]
        response = cur.execute(query2, to_filter2).fetchone()
        conn.commit()
        return '201'
    else:
        error_401()


@app.route('/users/changepassword', methods=['POST'])
@basic_auth.required
def changeUserPassword():

    jsonRequests = request.get_json()
    newPassword = jsonRequests.get('password')

    conn = sqlite3.connect('blog.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    name = app.config['BASIC_AUTH_USERNAME']

    query1 = '''SELECT * FROM users WHERE name = ? AND password = ?;'''
    to_filter1 = [name, app.config['BASIC_AUTH_PASSWORD']]

    account_check = cur.execute(query1, to_filter1).fetchone()

    accountName = ''
    accountPassword = ''

    if account_check:
        accountName = account_check.get("name")
        accountPassword = account_check.get("password")

    if accountName == app.config['BASIC_AUTH_USERNAME'] and accountPassword == app.config['BASIC_AUTH_PASSWORD']:

        #query2 = '''DELETE FROM users WHERE name=? AND password=?;'''
        query2 = '''UPDATE users SET password =? WHERE name=?;'''

        to_filter2 = [newPassword, app.config['BASIC_AUTH_USERNAME']]
        response = cur.execute(query2, to_filter2).fetchone()
        conn.commit()
        return Response('Password successfully changed.', 200, {'WWW-Authenticate':'Basic realm="Login Required"'})
    else:
        error_401()

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.errorhandler(401)
def error_401(error):
    return Response('Invalid username or password.', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

app.run()
