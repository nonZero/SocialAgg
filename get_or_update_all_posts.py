#!/usr/bin/env python3

import facebook
import pymongo
import sys
import dateutil.parser
import collections


def get_update():
    client = pymongo.MongoClient()
    db = client.get_database('socialagg')
    pages = db.get_collection('pages')
    posts = db.get_collection('posts')

    with open("TOKEN.txt") as f:
        TOKEN = f.read().strip()
    graph = facebook.GraphAPI(access_token=TOKEN, version='2.5')
    for page in pages.find():
        allposts = graph.get_object("{}/posts".format(page['id']),
                                    fields="message,created_time,shares,likes.summary(True).limit(0)",
                                    limit=100)['data']
        new_rez = [p for p in allposts if 'message' in p]
        c = collections.Counter()
        for post in new_rez:

            likes = post['likes']['summary']['total_count']

            shares = post['shares']['count'] if 'shares' in post else 0
            result = posts.update_one(
                {'id': post['id']},
                {'$set': {
                          'page_id': page['id'],
                          'id': post['id'],
                          'time': dateutil.parser.parse(post['created_time'], ignoretz=True),
                          'message': post['message'],
                          'shares': shares,
                          'likes': likes
                }}, upsert=True)
            key = 'new' if result.upserted_id else "updated"
            c[key] += 1
        print("OK", c.most_common())


if __name__ == '__main__':
    get_update()