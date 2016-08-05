import os
import logging

FILTER = ["1237372231", "89910973", "35390608", "81811976", "147654165",
        "3332342333", "183165874", "726748106", "295663598", "2515899612",
        "3378377920", "2936714848", "126955629", "333935142", "37601149",
        "96399121", "2942978628", "3412969648", "4631536043", "3416421"]

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
        deleted='del-'
        )

TIME_KEY = "updated-at"

DEFAULT_IMAGE = "http://abs.twimg.com/sticky/default_profile_images/default_profile_4.png"
