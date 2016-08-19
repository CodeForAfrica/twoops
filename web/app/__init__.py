"""
Flask app
"""
import os, redis, datetime
from flask import (Flask, g, request, session, redirect,
                   url_for, render_template, jsonify)
from flask_script import Manager
from pylitwoops.streaming import config as config_file
from pylitwoops.streaming.listener import get_api
from pylitwoops.worker.check import chunkify
from flask_paginate import Pagination

app = Flask(__name__,
            template_folder=os.getenv('TEMPLATES'),
            static_folder=os.getenv('STATIC'))
app.config.from_object(config_file)


def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = redis.StrictRedis(**app.config['REDIS'])
    return g.redis



@app.route('/')
def counties():
    '''
    index.html
    '''
    args = request.args.copy()
    redis_client = get_redis()

    try:
        last_updated, delete_count = redis_client.get(app.config['TIME_KEY']).split('|')
    except:
        last_updated = delete_count = "0"
    entries = redis_client.keys("%s*" % app.config['PREFIX']['deleted'])
    print entries
    deleted_tweets = []
    for entry in entries:
        deleted_tweet = eval(redis_client.get(entry))
        if str(deleted_tweet.get('sender_id')) == app.config['HEARTBEAT_ACCOUNT']:
            continue
        if "avatar" not in deleted_tweet:
            deleted_tweet['avatar'] = app.config['DEFAULT_IMAGE']
        deleted_tweets.append(deleted_tweet)
    sorted_deleted_tweets = sorted(deleted_tweets, key=lambda k: k['created_at'], reverse=True)
    chunks = chunkify(sorted_deleted_tweets, app.config["PAGESIZE"])
    print "page count: %s" % len(chunks)
        
    return render_template("index.html",
            entries=sorted_deleted_tweets,
            last_updated=last_updated,
            delete_count=delete_count,
            page=int(args.get("page", 0)),
            pages=chunks,
            pagecount=len(chunks)
            )


@app.route('/tracked-users')
def tracked_users():
    '''
    users.html
    '''
    redis_client = get_redis()
    users = []
    page = request.args.get('page', type=int, default=1)
    per_page = 9
    for user in redis_client.keys("%s*" % app.config['PREFIX']['user']):
        user_payload = eval(redis_client.get(user))

        if not str(user_payload['id']) == app.config['HEARTBEAT_ACCOUNT']:
            users.append(dict(
                screen_name=user_payload['screen_name'],
                avatar=user_payload['profile_image_url'],
                user_id=user_payload['id'],
                bio=user_payload['description']
                ))
    pagination = Pagination(page=page, total=len(users), search='', record_name='users')
    return render_template('users.html', users=users[per_page * page : per_page * page + 9], pagination=pagination,)



manager = Manager(app)

if __name__ == "__main__":
    manager.run()
