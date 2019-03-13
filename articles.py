#Dev 1​ owns the Articles and Users microservices and HTTP Basic Authentication.

import flask

from flask import request, Response, jsonify
from flask_basicauth import BasicAuth
import sqlite3
import logging
import random
import time



logging.basicConfig(level=logging.DEBUG)
random.seed(time.clock())
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# app.config['BASIC_AUTH_USERNAME'] = 'john'
# app.config['BASIC_AUTH_PASSWORD'] = 'matrix'


class customAuth (BasicAuth): 
    def check_credentials(self, username, password):
        #werkzeug.security.generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # get password from DB and determine if this person is truly the account owner
        app.config['BASIC_AUTH_USERNAME'] = username
        app.config['BASIC_AUTH_PASSWORD'] = password
        return True

basic_auth = customAuth(app)

@app.route('/', methods=['GET'])
@basic_auth.required
def home():
    return '''<h1>Welcome to the BLOG</h1>
<p>Meeting and exceeding all your blogadocious needs.</p>'''

# Articles microservice
# Each article consists of text, a title or headline, an author, and timestamps for article’s creation
# and the last time the article was modified.


# Post new article
# Request arguments = author, title, content
@app.route('/api/v1/article/create', methods=['POST'])
@basic_auth.required
def postArticle():

    jsonRequests = request.get_json()
    author = app.config['BASIC_AUTH_USERNAME']
    title = jsonRequests.get('title')
    content = jsonRequests.get('content')
    currentTime = int(time.time())
    last_modified = str(currentTime)
    published = str(currentTime)
    id = str(random.randint(1, 10000000000)) #Generate random id
    url = str(id)
    
    query = '''INSERT INTO articles (id, published, author, title, content, last_modified, url) \
            VALUES (?,?,?,?,?,?,?);'''
    to_filter = []

    if id:
        to_filter.append(id)
    if published:
        to_filter.append(published)
    if author:
        to_filter.append(author)
    if title:
        to_filter.append(title)
    if content:
        to_filter.append(content)
    if last_modified:
        to_filter.append(last_modified)
    if url:
        to_filter.append(url)

    conn = sqlite3.connect('articles.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query, to_filter).fetchall()
    print("Results: ", results)

    conn.commit() 

    #return '201'


# Retrieve an individual article
@app.route('/api/v1/article/', methods=['GET'])
def retrieveArticle():

    jsonRequests = request.get_json()
    url = jsonRequests.get('url')
    
    query = "SELECT content FROM articles WHERE id = ?"
    to_filter = [url]

    conn = sqlite3.connect('articles.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)



# Edit an individual article. The last-modified timestamp should be updated.
@app.route('/api/v1/article/edit', methods=['POST'])
@basic_auth.required
def editArticle():

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

    if article_author == app.config['BASIC_AUTH_USERNAME']:

        query2 = '''UPDATE articles SET content =? WHERE id=?;'''
        to_filter2 = [content, id]
        all_articles = cur.execute(query2, to_filter2).fetchone()
        conn.commit() 
        return "201"
    else:
        return "401"

# Delete a specific existing article
@app.route('/api/v1/article/delete', methods=['DELETE'])
@basic_auth.required
def deleteArticle():


    jsonRequests = request.get_json()
    url = jsonRequests.get('url')

    conn = sqlite3.connect('articles.db')
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
        query2 = '''DELETE FROM articles WHERE id=? AND author=?;'''
        to_filter2 = [url, article_author]

        conn = sqlite3.connect('articles.db')
        conn.row_factory = dict_factory
        cur = conn.cursor()
        all_articles = cur.execute(query2, to_filter2).fetchone()
        conn.commit() 

        return "201"
    else:
        return "401"


# Retrieve the entire contents (including article text) for the ​ n ​ most recent articles
@app.route('/api/v1/article/recent', methods=['GET'])
def recentArticle():

    jsonRequests = request.get_json()
    n = jsonRequests.get('n')

    query = '''SELECT * FROM articles ORDER BY published DESC LIMIT ?'''
    to_filter = [n]


    conn = sqlite3.connect('articles.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_articles = cur.execute(query, to_filter).fetchall()

    return jsonify(all_articles)

# Retrieve metadata for the ​ n ​ most recent articles, including title, author, date, and URL
@app.route('/api/v1/article/meta', methods=['GET'])
def recentMetaArticle():

    jsonRequests = request.get_json()
    n = jsonRequests.get('n')

    query = '''SELECT title, author, published, url FROM articles ORDER BY published DESC LIMIT ?'''
    to_filter = [n]

    conn = sqlite3.connect('articles.db')
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
