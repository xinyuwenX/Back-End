import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect('tags.db')


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Project 1</h1>
<p>In this project, you will work in a team to build a set of microservices for a blog platform.</p>'''


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/add_tags_new', methods=['POST'])
def add_tags_new():
    query_parameters = request.args

    tag = query_parameters.get('tag')
    article = query_parameters.get('article')

    query = "INSERT INTO tags VALUES"
    to_filter = []

    if tag:
        query += ' tag=? AND'
        to_filter.append(tag)
    if article:
        query += ' article=? AND'
        to_filter.append(article)
    if not (tag or article):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)


@app.route('/add_tags_existing', methods=['POST'])
def add_tags_existing():

    return jsonify()


@app.route('/remove_tags', methods=['DELETE'])
def remove_tags():

    return jsonify()


@app.route('/retrieve_tags', methods=['GET'])
def retrieve_tags():

    return jsonify()

@app.route('/retrieve_urls', methods=['GET'])
def retrieve_urls():

    return jsonify()


app.run()