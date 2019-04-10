# Dev 1​ owns the Articles and Users microservices and HTTP Basic Authentication.

import flask

from flask import request, Response, jsonify
import sqlite3
import logging
import time

logging.basicConfig(level=logging.DEBUG)
app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome to the BLOG</h1>
<p>Meeting and exceeding all your blogadocious needs.</p>'''


# Articles microservice
# Each article consists of text, a title or headline, an author, and timestamps for article’s creation
# and the last time the article was modified.


# Post new article
# Request arguments = author, title, content
@app.route('/articles/create', methods=['POST'])
def postArticle():
    jsonRequests = request.get_json()
    author = app.config['BASIC_AUTH_USERNAME']
    title = jsonRequests.get('title')
    content = jsonRequests.get('content')
    url = jsonRequests.get('url')
    currentTime = datetime('now')

    timestamp_modified = currentTime
    timestamp_create = currentTime

    # query = '''INSERT INTO articles (id, published, author, title, content, last_modified, url) \
    #         VALUES (?,?,?,?,?,?,?);'''
    query = '''INSERT INTO articles (url, content, title, author, timestamp_create, timestamp_modified) \
            VALUES (?,?,?,?,?,?,?);'''
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
    print("Results: ", results)

    conn.commit()

    # return '201'


# Retrieve an individual article
@app.route('/articles/', methods=['GET'])
def retrieveArticle():
    jsonRequests = request.get_json()
    url = jsonRequests.get('url')

    query = "SELECT content FROM articles WHERE url = ?"
    to_filter = [url]

    conn = sqlite3.connect('blog.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)


# Edit an individual article. The last-modified timestamp should be updated.
@app.route('/articles/edit', methods=['POST'])
def editArticle():
    jsonRequests = request.get_json()
    url = jsonRequests.get('url')
    content = jsonRequests.get('content')
    id = url

    conn = sqlite3.connect('blog.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    query1 = '''SELECT author FROM articles WHERE url = ?'''
    to_filter1 = [url]

    author_check = cur.execute(query1, to_filter1).fetchone()
    article_author = author_check.get("author")

    if article_author == app.config['BASIC_AUTH_USERNAME']:

        query2 = '''UPDATE articles SET content =? WHERE url=?;'''
        to_filter2 = [content, id]
        all_articles = cur.execute(query2, to_filter2).fetchone()
        conn.commit()
        return "201"
    else:
        return "401"


# Delete a specific existing article
@app.route('/articles/delete', methods=['DELETE'])
def deleteArticle():
    jsonRequests = request.get_json()
    url = jsonRequests.get('url')

    conn = sqlite3.connect('blog.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    query1 = '''SELECT author FROM articles WHERE url = ?'''
    to_filter1 = [url]
    author_check = cur.execute(query1, to_filter1).fetchone()
    print(author_check)
    article_author = ''
    if (author_check):
        article_author = author_check.get("author")
        print(article_author)
    else:
        print("no author found")

    if article_author == app.config['BASIC_AUTH_USERNAME']:
        # Assuming author is authorized
        query2 = '''DELETE FROM articles WHERE url=? AND author=?;'''
        to_filter2 = [url, article_author]

        conn = sqlite3.connect('blog.db')
        conn.row_factory = dict_factory
        cur = conn.cursor()
        all_articles = cur.execute(query2, to_filter2).fetchone()
        conn.commit()

        return "201"
    else:
        return "401"


# Retrieve the entire contents (including article text) for the ​ n ​ most recent articles
@app.route('/articles/recent', methods=['GET'])
def recentArticle():
    jsonRequests = request.get_json()
    n = jsonRequests.get('n')

    query = '''SELECT * FROM articles ORDER BY timestamp_create DESC LIMIT ?'''
    to_filter = [n]

    conn = sqlite3.connect('blog.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_articles = cur.execute(query, to_filter).fetchall()

    return jsonify(all_articles)


# Retrieve metadata for the ​ n ​ most recent articles, including title, author, date, and URL
@app.route('/articles/meta', methods=['GET'])
def recentMetaArticle():
    jsonRequests = request.get_json()
    n = jsonRequests.get('n')

    query = '''SELECT title, author, timestamp_create, url FROM articles ORDER BY timestamp_create DESC LIMIT ?'''
    to_filter = [n]

    conn = sqlite3.connect('blog.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_articles = cur.execute(query, to_filter).fetchall()

    return jsonify(all_articles)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


app.run()
