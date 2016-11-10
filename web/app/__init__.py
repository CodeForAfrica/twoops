"""
Flask app
"""
import os, redis, datetime
from flask import (Flask, g, request, session, redirect,
                   url_for, render_template, jsonify)
from flask_script import Manager
from pylitwoops.streaming import config as config_file
from pylitwoops.streaming.listener import get_api
from pylitwoops.streaming.listener import get_redis as _get_redis
from pylitwoops.worker.check import chunkify
from flask_paginate import Pagination
import math

app = Flask(__name__,
            template_folder=os.getenv('TEMPLATES'),
            static_folder=os.getenv('STATIC'))
app.config.from_object(config_file)


def get_redis(users_only=False):
    if not hasattr(g, 'redis'):
        g.redis = _get_redis(5)
        g.redis_user = _get_redis(1)
    if users_only:
        return g.redis_user
    return g.redis



@app.route('/')
def home():
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
        
    return render_template("index.html",
            entries=sorted_deleted_tweets,
            last_updated=last_updated,
            delete_count=delete_count,
            page=int(args.get("page", 0)),
            pages=chunks,
            pagecount=len(chunks),
            landing=True,
            pagesize=app.config["PAGESIZE"]
            )


@app.route('/tracked-users')
def tracked_users():
    '''
    users.html
    '''
    redis_client = get_redis()
    users = []
    page = request.args.get('page', type=int, default=0)
    per_page = 9
    keys = redis_client.keys("%s*" % app.config['PREFIX']['user'])
    for user in keys[page * per_page: page * per_page + per_page]:
        user_payload = eval(redis_client.get(user))
        
        lenkey = "user-" + str(user_payload["id"])
        user_delete_count = redis_client_user.llen(lenkey)

        if not str(user_payload['id']) == app.config['HEARTBEAT_ACCOUNT']:
            users.append(dict(
                screen_name=user_payload['screen_name'],
                avatar=user_payload['profile_image_url'],
                user_id=user_payload['id'],
                bio=user_payload['description'],
                delete_count=user_delete_count
                ))
    pagination = Pagination(page=page, total=len(users), search='', record_name='users')
    pagecount = int(math.ceil( float(len(keys))/per_page))
    return render_template('users.html', users=users, pagination=pagination, pagecount=pagecount, page=page, users_page=True)

@app.route('/about')
def about():
    '''
    about.html
    '''
    return render_template('about.html', about=True)

@app.route('/tweet/<tweet_id>')
def tweet(tweet_id):
    '''
    tweet.html
    '''
    redis_client = get_redis()
    store_key = app.config['PREFIX']['deleted'] + str(tweet_id)
    payload = redis_client.get(store_key)
    payload = eval(payload) if payload else {}
    print "RETURNED %s" % payload
    return render_template('tweet.html', payload=payload, tweet_page=True)

@app.route('/user/<user_id>')
def user(user_id):
    '''
    user.html
    '''
    redis_client = get_redis()
    redis_client_user = get_redis(users_only=True)
    store_key = "user-" + str(user_id)
    user_profile = eval(redis_client.get(store_key))
    user_deleted_tweets = redis_client_user.lrange(store_key, 0, -1)
    user_tweets = []
    for tweet_id in user_deleted_tweets:
        tweet_payload = eval(redis_client.get(tweet_id))
        user_tweets.append(tweet_payload)
    print "get user %s - %s" % (user_id, len(user_tweets))
    return render_template('user.html', payload=user_tweets, user=user_profile)


@app.route('/stories')
def stories():
    '''
    stories.html
    '''
    return render_template('stories.html', stories=True)

@app.route('/recommend')
def recommend():
    '''
    Recieves a handle to track
    '''
    handle = request.args.get('handle', None)
    if handle:
        redis_client = get_redis()
        key = app.config["PREFIX"]["recommend"] + str(handle)
        redis_client.set(key, "https://twitter.com/%s" % handle)
    return jsonify({'success': True})

@app.route('/subscribe-to-alerts', methods=["GET", "POST"])
def subscribe_to_alerts():
    '''
    Recieves a email to send alerts to
    '''
    email = request.args.get('email', None)
    user_id = request.args.get('user_id', None)
    if email:
        redis_client = get_redis()
        key = app.config["PREFIX"]["alerts"] + str(user_id)
        redis_client.rpush(key, email)
    return jsonify({'success': False})


manager = Manager(app)

if __name__ == "__main__":
    manager.run()
