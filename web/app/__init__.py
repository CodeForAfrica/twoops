"""
Flask app
"""
import os, redis, datetime
from flask import (Flask, g, request, session, redirect,
                   url_for, render_template, jsonify)
from flask_script import Manager
from pylitwoops.streaming import config as config_file
from pylitwoops.streaming.listener import get_api

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
        
    return render_template("index.html",
            entries=deleted_tweets,
            last_updated=last_updated,
            delete_count=delete_count)


@app.route('/tracked-users')
def tracked_users():
    '''
    users.html
    '''
    redis_client = get_redis()
    tw_api = get_api()
    users = []
    for user in app.config['FILTER']:
        user_key = "%s%s" % (app.config['PREFIX']['user'], user)
        try:
            user_payload = eval(redis_client.get(user_key))
        except TypeError:
            user_payload = None

        if user_payload:
            print "Cache hit"
        if not user_payload:
            print "Cache miss"
            user_payload = tw_api.get_user(user)._json
            redis_client.set(user_key, user_payload, ex=app.config['CACHE_TTL'])

        if not str(user_payload['id']) == app.config['HEARTBEAT_ACCOUNT']:
            users.append(dict(
                screen_name=user_payload['screen_name'],
                avatar=user_payload['profile_image_url'],
                user_id=user_payload['id'],
                bio=user_payload['description']
                ))

    return render_template('users.html', users=users)



manager = Manager(app)

if __name__ == "__main__":
    manager.run()
