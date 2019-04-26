'''
========================================================================================================================
Articles microservice

Author: Jason Hasselle
Email: JHasselle@csu.fullerton.edu
========================================================================================================================
'''
import flask
from functools import wraps
from flask import Flask, request, Response, jsonify, json
import sqlite3
import logging
import time

# logging.basicConfig(level=logging.DEBUG)
app = flask.Flask(__name__)
app.config["DEBUG"] = True

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


# Checks to see if there has been an update to the db since the request header 'If-Modified-Since'.
def updateExists():
    jsonRequests = request.get_json()
    requestLastModified = jsonRequests.get('If-Modified-Since')

    conn = sqlite3.connect('articles.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    query1 = '''SELECT MAX(timestamp_modified) FROM articles;'''

    queryResults = cur.execute(query1).fetchone()
    dbEntryLastModified = float(queryResults.get("MAX(timestamp_modified)"))

    if requestLastModified:
        if  dbEntryLastModified > requestLastModified:
            return True, dbEntryLastModified
        else:
            return False, dbEntryLastModified
    else:
        return True, dbEntryLastModified



# Articles microservice
# Each article consists of text, a title or headline, an author, and timestamps for article’s creation
# and the last time the article was modified.


# GET Methods


@app.route('/articles', methods=['GET'])
@requires_auth
def articles():

    return 'Welcome to the Articles microservice.'


# Retrieve an individual article
@app.route('/articles/get', methods=['GET'])
@requires_auth
def retrieveArticle():

    requestNeedsUpdate, timeOfLatestUpdate = updateExists()
    if requestNeedsUpdate:

        jsonRequests = request.get_json()
        url = jsonRequests.get('url')

        query = "SELECT content FROM articles WHERE url = ?"
        to_filter = [url]

        conn = sqlite3.connect('articles.db')
        conn.row_factory = dict_factory
        cur = conn.cursor()
        results = cur.execute(query, to_filter).fetchall()

        return Response(json.dumps(results), status=200, headers={"Last-Modified":timeOfLatestUpdate})
    else:
        return Response(status=304)



# Retrieve metadata for the ​ n ​ most recent articles, including title, author, date, and URL
@app.route('/articles/meta', methods=['GET'])
@requires_auth
def recentMetaArticle():
    requestNeedsUpdate, timeOfLatestUpdate = updateExists()
    if requestNeedsUpdate:
        jsonRequests = request.get_json()
        n = jsonRequests.get('n')

        query = '''SELECT title, author, timestamp_create, url FROM articles ORDER BY timestamp_create DESC LIMIT ?'''
        to_filter = [n]

        conn = sqlite3.connect('articles.db')
        conn.row_factory = dict_factory
        cur = conn.cursor()
        all_articles = cur.execute(query, to_filter).fetchall()

        return Response(json.dumps(all_articles), status=200, headers={"Last-Modified":timeOfLatestUpdate})
    else:
        return Response(status=304, headers={"Last-Modified":timeOfLatestUpdate})



# Retrieve the entire contents (including article text) for the ​ n ​ most recent articles
@app.route('/articles/recent', methods=['GET'])
@requires_auth
def recentArticle():
    requestNeedsUpdate, timeOfLatestUpdate = updateExists()
    if requestNeedsUpdate:

        jsonRequests = request.get_json()
        n = jsonRequests.get('n')

        query = '''SELECT * FROM articles ORDER BY timestamp_create DESC LIMIT ?'''
        to_filter = [n]

        conn = sqlite3.connect('articles.db')
        conn.row_factory = dict_factory
        cur = conn.cursor()
        all_articles = cur.execute(query, to_filter).fetchall()

        return Response(json.dumps(all_articles), status=200, headers={"Last-Modified":timeOfLatestUpdate})
    else:
        return Response(status=304, headers={"Last-Modified":timeOfLatestUpdate})


# Put Methods


# Post new article
# Request arguments = author, title, content
@app.route('/articles/create', methods=['POST'])
@requires_auth
def createArticle():

    auth = request.authorization
    author = auth.username

    jsonRequests = request.get_json()
    title = jsonRequests.get('title')
    content = jsonRequests.get('content')
    url = jsonRequests.get('url')
    currentTime = time.time()
    timestamp_modified = currentTime
    timestamp_create = currentTime

    query = '''INSERT INTO articles (url, content, title, author, timestamp_create, timestamp_modified) \
            VALUES (?,?,?,?,?,?);'''
    to_filter = []

    if url:
        to_filter.append(url)
    if content:
        to_filter.append(content)
    if title:
        to_filter.append(title)
    if author:
        to_filter.append(author)
    if timestamp_create:
        to_filter.append(timestamp_create)
    if timestamp_modified:
        to_filter.append(timestamp_modified)

    conn = sqlite3.connect('articles.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query, to_filter).fetchall()

    conn.commit()

    # return jsonify(results)

    return Response(status=201)



# Delete a specific existing article
@app.route('/articles/delete', methods=['DELETE'])
@requires_auth
def deleteArticle():

    auth = request.authorization
    author = auth.username

    jsonRequests = request.get_json()
    url = jsonRequests.get('url')

    conn = sqlite3.connect('articles.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    # Assuming author is authorized
    query2 = '''DELETE FROM articles WHERE url=? AND author=?;'''
    to_filter2 = [url, author]

    conn = sqlite3.connect('articles.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_articles = cur.execute(query2, to_filter2).fetchone()
    conn.commit()

    return Response(status=202)

    

# Edit an individual article. The last-modified timestamp should be updated.
@app.route('/articles/edit', methods=['POST'])
@requires_auth
def editArticle():

    auth = request.authorization
    author = auth.username

    jsonRequests = request.get_json()
    url = jsonRequests.get('url')
    content = jsonRequests.get('content')
    id = url

    conn = sqlite3.connect('articles.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    query1 = '''SELECT author FROM articles WHERE url = ?'''
    to_filter1 = [url]

    author_check = cur.execute(query1, to_filter1).fetchone()
    article_author = author_check.get("author")

    if article_author == author:

        query2 = '''UPDATE articles SET content =? WHERE url=?;'''
        to_filter2 = [content, id]
        all_articles = cur.execute(query2, to_filter2).fetchone()
        conn.commit()
        return Response(status=201)
    else:
        return Response(status=401)



@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The articles resource could not be found.</p>", 404


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


app.run()
