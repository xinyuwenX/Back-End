'''
========================================================================================================================
Comments microservice
Users can post comments on each article.
As with the tags microservice, individual articles are referred to by URL.
Each comment has an author and a date.

Author: Xinyu Wen & Jason Hasselle
Email: xinyuwen@csu.fullerton.edu, Jhasselle@csu.fullerton.edu
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

# Checks to see if there has been an update to the db since the request header 'If-Modified-Since'.
def updateExists():
    jsonRequests = request.get_json()
    requestLastModified = jsonRequests.get('If-Modified-Since')

    conn = sqlite3.connect('comments.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    query1 = '''SELECT MAX(date) FROM comments;'''

    queryResults = cur.execute(query1).fetchone()
    dbEntryLastModified = float(queryResults.get("MAX(date)"))

    if requestLastModified:
        if  dbEntryLastModified > requestLastModified:
            return True, dbEntryLastModified
        else:
            return False, dbEntryLastModified
    else:
        return True, dbEntryLastModified


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
    requestNeedsUpdate, timeOfLatestUpdate = updateExists()
    if requestNeedsUpdate:

        jsonRequests = request.get_json()

        url = jsonRequests.get('url')
        limit = jsonRequests.get('limit')

        if url and limit:
            query = f'''SELECT comment FROM comments WHERE url="{url}" order by date desc limit {limit} ;'''
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = dict_factory
            cur = conn.cursor()

            results = cur.execute(query).fetchall()

            return Response(json.dumps(results), status=200, headers={"Last-Modified":timeOfLatestUpdate})
        else:
            return Response(status=404, headers={"Last-Modified":timeOfLatestUpdate})
    else:
        return Response(status=304)
    


# Retrieve the number of comments on a given article
# Request url
@app.route('/comments/retrieve_number', methods=['GET'])
@requires_auth
def retrieve_number():

    requestNeedsUpdate, timeOfLatestUpdate = updateExists()
    if requestNeedsUpdate:

        jsonRequests = request.get_json()
        url = jsonRequests.get('url')

        query = "SELECT count(*) FROM comments WHERE"
        to_filter = []

        if url:
            query += ' url=? AND'
            to_filter.append(url)
            query = query[:-4] + ';'

            conn = sqlite3.connect(DATABASE)
            conn.row_factory = dict_factory
            cur = conn.cursor()

            results = cur.execute(query, to_filter).fetchall()

            return Response(json.dumps(results), status=200, headers={"Last-Modified":timeOfLatestUpdate})

        else:
            return Response(status=404, headers={"Last-Modified":timeOfLatestUpdate})
    else:
        return Response(status=304)


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
        return Response(status=415)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query).fetchall()
    conn.commit()

    return Response(status=204)

# Post a new comment on an article with basic auth
# Request comment, url, author
@app.route('/comments/add_comments', methods=['POST'])
@requires_auth
def add_comments():

    auth = request.authorization
    author = auth.username

    jsonRequests = request.get_json()
    comment = jsonRequests.get('comment')
    url = jsonRequests.get('url')
    currentTime = time.time()

    query = '''INSERT INTO comments (comment, url, author, date) VALUES (?,?,?,?);'''
    to_filter = []

    if comment and url:
        to_filter.append(comment)
        to_filter.append(url)
        to_filter.append(author)
        to_filter.append(currentTime)
    else:
        return Response(status=415)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factorya
    cur = conn.cursor()
    results = cur.execute(query, to_filter).fetchall()
    conn.commit()

    return Response(status=201)
 

# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()
