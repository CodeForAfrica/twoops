import os
import logging

FILTER = ["1237372231", "89910973"]

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
