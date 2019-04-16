'''
========================================================================================================================
Comments microservice
Users can post comments on each article.
As with the tags microservice, individual articles are referred to by URL.
Each comment has an author and a date.

Author: Xinyu Wen
Email: xinyuwen@csu.fullerton.edu
========================================================================================================================
'''
import flask
from functools import wraps
from flask import Flask, request, Response, jsonify, json
import sqlite3
import logging
import time

app = Flask(__name__)
app.config["DEBUG"] = True

DATABASE = 'comments.db'

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

# Let the database return items from the database as dictionaries
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Comments microservice main page
@app.route('/comments', methods=['GET'])
@requires_auth
def comments():
    return '<p>Comments microservice</p>'


# Retrieve the n most recent comments on a URL
# Request url and number
@app.route('/comments/retrieve_comments', methods=['GET'])
@requires_auth
def retrieve_comments():
    query_parameters = request.args

    url = query_parameters.get('url')
    limit = query_parameters.get('limit')

    query = "SELECT comment FROM comments WHERE"
    to_filter = []

    if url:
        query += ' url=?'
        to_filter.append(url)
    if limit:
        query += ' order by date desc limit ?'
        to_filter.append(limit)
    if not (url or limit):
        return page_not_found(404)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)


# Retrieve the number of comments on a given article
# Request url
@app.route('/comments/retrieve_number', methods=['GET'])
@requires_auth
def retrieve_number():
    query_parameters = request.args

    url = query_parameters.get('url')

    query = "SELECT count(*) FROM comments WHERE"
    to_filter = []

    if url:
        query += ' url=? AND'
        to_filter.append(url)
    if not (url):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)


# Delete an individual comment with basic auth
# Request url
@app.route('/comments/remove_comments', methods=['DELETE'])
@requires_auth
def remove_comments():
    query = "DELETE FROM comments WHERE "

    if request.headers['Content-Type'] == 'application/json':
        query += "'"
        query += json.request.data.decode()
        query += "';"
    else:
        return "415 Unsupported Media Type ;)"

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query).fetchall()
    conn.commit()

    return jsonify(results)

# Post a new comment on an article with basic auth
# Request comment, url, author
@app.route('/comments/add_comments', methods=['POST'])
@requires_auth
def add_comments():
    query = 'INSERT INTO comments(id, comment, url, author, date) VALUES '

    if request.headers['Content-Type'] == 'application/json':
        query += '('
        query += json.request.data.decode()
        query += ",datetime('now'));"
    else:
        return "415 Unsupported Media Type ;)"

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query).fetchall()
    conn.commit()

    return jsonify(results)

# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404



app.run()