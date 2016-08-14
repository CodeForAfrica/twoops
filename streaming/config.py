import os
import logging

LIST_IDS = ['763301230999404544']

LOGGING = {}
LOGGING['location'] = 'logs/log-pylitwoops-streaming.log'
LOGGING['level'] = logging.DEBUG
LOGGING['format'] = '%(asctime)s : %(levelname)s: %(message)s'


TW_AUTH_CREDENTIALS = {}
# pylitwoops
TW_AUTH_CREDENTIALS['pylitwoops'] = {}
TW_AUTH_CREDENTIALS['pylitwoops']['consumer_key'] = os.getenv('TW_CONSUMER_KEY')
TW_AUTH_CREDENTIALS['pylitwoops']['consumer_secret'] = os.getenv('TW_CONSUMER_SECRET')
TW_AUTH_CREDENTIALS['pylitwoops']['access_token_key'] = os.getenv('TW_ACCESS_TOKEN_KEY')
TW_AUTH_CREDENTIALS['pylitwoops']['access_token_secret'] = os.getenv('TW_ACCESS_TOKEN_SECRET')

SENDER_ID = {}
SENDER_ID['pylitwoops'] = '1237372231'

HEARTBEAT_ACCOUNT = "1237372231" # Twitter ID of the account sending heartbeats

redis_host = os.getenv('REDIS_HOST', 'localhost:6379')
REDIS = dict(
        host=redis_host.split(':')[0],
        port=redis_host.split(':')[1],
        db='5',
        password=os.getenv('REDIS_PASSWORD', None),
        socket_timeout=2,
        socket_connect_timeout=2,
        )

PREFIX = dict(
        new='tw-',
        deleted='del-',
        user='user-'
        )

TIME_KEY = "updated-at"

DEFAULT_IMAGE = "http://abs.twimg.com/sticky/default_profile_images/default_profile_4.png"

CACHE_TTL = 3600 # in seconds

PAGESIZE = 10 # no. of tweets per page
