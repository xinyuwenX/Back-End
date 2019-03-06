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


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Comments microservice</h1>
<p>Users can post comments on each article. As with the tags microservice, individual articles are referred to by URL. Each comment has an author and a date.</p>'''


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/post_comment', methods=['POST'])
def post_comment():
    query_parameters = request.args

    author = query_parameters.get('author')
    date = query_parameters.get('date')


    query = "INSERT INTO comments VALUES"
    to_filter = []

    if author:
        query += ' author=? AND'
        to_filter.append(author)
    if date:
        query += ' date=? AND'
        to_filter.append(date)
    if not (author or date):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('comments.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

@app.route('/delete_comment', methods=['DELETE'])
def delete_comment():

    return jsonify()


@app.route('/retrieve_comment_article', methods=['GET'])
def retrieve_comment_article():

    return jsonify()


@app.route('/retrieve_comment_recent', methods=['GET'])
def retrieve_comment_recent():

    return jsonify()


app.run()