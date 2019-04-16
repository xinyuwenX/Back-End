'''
========================================================================================================================
Tags microservice
Each article can be have one or more tags associated with it.
Since this API is exposed separately from the Articles API, individual articles are referred to by URL.

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

DATABASE = 'tags.db'

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

# Tags microservice main page
@app.route('/tags', methods=['GET'])
@requires_auth
def tags():
    return '<p>Tags microservice</p>'


# Retrieve the tags for an individual URL
@app.route('/tags/retrieve_tags', methods=['GET'])
@requires_auth
def retrieve_tags():
    query_parameters = request.args
    url = query_parameters.get('url')

    query = "SELECT tag FROM tags WHERE"
    to_filter = []

    if url:
        query += ' url=?'
        to_filter.append(url)
    if not (url):
        return page_not_found(404)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)


# Retrieve a list of URLs with a given tag
@app.route('/tags/retrieve_urls', methods=['GET'])
@requires_auth
def retrieve_urls():
    query_parameters = request.args
    tag = query_parameters.get('tag')

    query = "SELECT url FROM tags WHERE"
    to_filter = []

    if tag:
        query += ' tag=?'
        to_filter.append(tag)
    if not (tag):
        return page_not_found(404)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)


# Remove one or more tags from an individual URL with basic auth
@app.route('/tags/remove_tags', methods=['DELETE'])
@requires_auth
def remove_tags():
    query = "DELETE FROM tags WHERE url = "

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

# Add tags to a new or an existing URL with basic auth
@app.route('/tags/add_tags', methods=['POST'])
@requires_auth
def add_tags():
    query = 'insert into tags(id, tag, url) values '

    if request.headers['Content-Type'] == 'application/json':
        query += '('
        query += json.request.data.decode()
        query += ');'
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