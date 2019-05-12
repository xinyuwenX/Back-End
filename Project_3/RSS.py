import datetime
import flask
import requests
from flask import Flask, request, Response, jsonify, json
from functools import wraps
import logging
from rfeed import Item, Feed, Guid
from httpcache import CachingHTTPAdapter, HTTPCache

app = flask.Flask("RSS")

DomainName = "http://localhost/"
Auth = (
    "username",
    "password",
)
sess = requests.Session()
sess.mount(DomainName, CachingHTTPAdapter())

@app.route("/rss", methods=["GET"])
def rss_feed():
    # A full feed containing the full text for each article, its tags as RSS categories, and a comment count.

    # ArticlesResult = sess.get(DomainName + "articles/recent/10", auth=Auth, headers={"If-Modified-Since":"88888888888888888"}).json()
    ArticlesResult = requests.request('GET', DomainName + "articles/recent/10", auth=Auth, headers={"If-Modified-Since":"88888888888888888"})

    if ArticlesResult.status_code == 304:
        return Response(status=304)


    #json.dumps(results)

    jsonResponse = ArticlesResult.json()

    TagsResult = []
    CommentCount = []

    for i in jsonResponse:
        CommentCount.append(
            # requests.request('GET', DomainName + "comments/" + i["url"], auth=Auth, headers={"If-Modified-Since":"0"}).json()
            sess.get(DomainName + "comments/" + i["url"], auth=Auth, headers={"If-Modified-Since":"88888888888888888"}).json()
        )

    items = []

    for index, article in enumerate(jsonResponse):
        if CommentCount[index]:

            items.append(
                Item(
                    title=article["title"],
                    link=DomainName + "articles/" + article["url"],
                    description=article["content"],
                    author=article["author"],
                    guid=Guid(DomainName + "articles/" + article["url"]),
                    comments=CommentCount[index]
                    # pubDate= datetime.datetime.utcfromtimestamp(article["timestamp_create"])
                    # pubDate=1000000
                )
            )
        else:
            items.append(
                Item(
                    title=article["title"],
                    link=DomainName + "articles/" + article["url"],
                    description=article["content"],
                    author=article["author"],
                    guid=Guid(DomainName + "articles/" + article["url"])
                )
            )

    rssFeed = Feed(
        title="Blog RSS Feed",
        link=DomainName + "RSS",
        description="RSS feed of our awesome blog",
        language="en-US",
        lastBuildDate=datetime.datetime.now(),
        items=items
    )

    
    # return Response(json.dumps(CommentCount[0]), headers={"Last-Modified":"0"})
    return Response(rssFeed.rss(), headers={"Last-Modified":"0", "Cache-Control": "max-age=30"})
    


# @app.route("/rss/summary", methods=["GET"])
# def rss_feed_summary():

#     # A summary feed listing the title, author, date, and link for the 10 most recent articles.
#     jsonResult = sess.get(DomainName + "articles/recent/10", auth=Auth).json()
#     items = []

#     for i in jsonResult["articles"]:
#         items.append(
#             Item(
#                 title=i["title"],
#                 link=DomainName + "articles/" + i["url"],
#                 author=i["author"],
#                 guid=Guid(DomainName + "articles/" + i["url"]),
#                 pubDate=datetime.datetime.utcfromtimestamp(i["timestamp_create"]),
#             )
#         )

#     rssFeedSummary = Feed(
#         title="Blog Summary RSS Feed",
#         link=DomainName + "RSS/Summary",
#         description="RSS summary feed of our awesome blog",
#         language="en-US",
#         lastBuildDate=datetime.datetime.now(),
#         items=items
#     )

#     return Response(rssFeedSummary.rss(), headers={"Last-Modified":"0"})
#     # return flask.Response(rssFeedSummary.rss(), mimetype="text/xml")


# @app.route("/rss/comments/<article_url>", methods=["GET"])
# def rss_feed_comments(article_url):
#     res = sess.get(DomainName + "comments/" + article_url + "/9999", auth=Auth)

#     if res.status_code == 404:
#         return Response(status=404)

#     # A comment feed for each article
#     CommentsResult = res.json()

#     items = []

#     for comment in CommentsResult["comments"]:
#         items.append(
#             Item(
#                 title=comment["author"],
#                 link=DomainName + "articles/" + article_url,
#                 description=comment["text"],
#                 author=comment["author"],
#                 guid=Guid(comment["uuid"]),
#                 pubDate=datetime.datetime.utcfromtimestamp(comment["time"]),
#             )
#         )

#     rssFeedComments = Feed(
#         title="Blog post comment RSS Feed",
#         link=DomainName + "RSS/Comments/" + article_url,
#         description="RSS feed of of the comment section of a blog",
#         language="en-US",
#         lastBuildDate=datetime.datetime.now(),
#         items=items,
#     )

#     return flask.Response(rssFeedComments.rss(), mimetype="text/xml")

