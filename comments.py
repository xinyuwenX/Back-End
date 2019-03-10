from flask import Flask, request, jsonify, json
import sqlite3

app = Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '<h1>Project 1</h1>'


@app.route('/comments', methods=['GET'])
def comments():
    return '<h1>Comments microservice</h1>'



@app.route('/comments/retrieve_comments', methods=['GET'])
def retrieve_comments():
    query_parameters = request.args

    url = query_parameters.get('url')

    query = "SELECT comment FROM comments WHERE"
    to_filter = []

    if url:
        query += ' url=? AND'
        to_filter.append(url)
    if not (url):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)



@app.route('/comments/retrieve_number', methods=['GET'])
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

    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)



@app.route('/comments/remove_comments', methods=['DELETE'])
def remove_comments():
    query = "DELETE FROM comments WHERE "

    if request.headers['Content-Type'] == 'text/plain':
        query += "'"
        query += request.data.decode()
        query += "';"
    else:
        return "415 Unsupported Media Type ;)"

    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query).fetchall()
    conn.commit()

    return jsonify(results)


@app.route('/comments/add_comments', methods=['POST'])
def add_comments():
    query = 'insert into comments(id, comment, url, author, date) values '

    if request.headers['Content-Type'] == 'text/plain':
        query += '('
        query += request.data.decode()
        query += ');'
    else:
        return "415 Unsupported Media Type ;)"

    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query).fetchall()
    conn.commit()

    return jsonify(results)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404



app.run()