import os
import logging

LIST_IDS = ['763301230999404544']

LOGGING = {}
LOGGING['location'] = 'logs/log-twoops-streaming.log'
LOGGING['level'] = logging.DEBUG
LOGGING['format'] = '%(asctime)s : %(levelname)s: %(message)s'

PRINCIPLE_TW_HANDLE = 'twoops'

consumerkeys = eval(os.getenv('TW_CONSUMER_KEYS'))
consumersecrets = eval(os.getenv('TW_CONSUMER_SECRETS'))
tokenkeys = eval(os.getenv('TW_ACCESS_TOKEN_KEYS'))
tokensecrets = eval(os.getenv('TW_ACCESS_TOKEN_SECRETS'))

TW_AUTH_CREDENTIALS = {}
# twoops
TW_AUTH_CREDENTIALS['twoops'] = {}
TW_AUTH_CREDENTIALS['twoops']['consumer_key'] = consumerkeys[0]
TW_AUTH_CREDENTIALS['twoops']['consumer_secret'] = consumersecrets[0]
TW_AUTH_CREDENTIALS['twoops']['access_token_key'] = tokenkeys[0]
TW_AUTH_CREDENTIALS['twoops']['access_token_secret'] = tokensecrets[0]

TW_AUTH_CREDENTIALS['twoops_one'] = {}
TW_AUTH_CREDENTIALS['twoops_one']['consumer_key'] = consumerkeys[1]
TW_AUTH_CREDENTIALS['twoops_one']['consumer_secret'] = consumersecrets[1]
TW_AUTH_CREDENTIALS['twoops_one']['access_token_key'] = tokenkeys[1]
TW_AUTH_CREDENTIALS['twoops_one']['access_token_secret'] = tokensecrets[1]

SENDER_ID = {}
SENDER_ID['twoops'] = '1237372231'

HEARTBEAT_ACCOUNT = "1237372231" # Twitter ID of the account sending heartbeats

redis_host = os.getenv('REDIS_HOST', 'localhost:6379')
redis_databases = dict(
        tweets=5,
        users=1
        )
REDIS = dict(
        host=redis_host.split(':')[0],
        port=redis_host.split(':')[1],
        password=os.getenv('REDIS_PASSWORD', None),
        socket_timeout=2,
        socket_connect_timeout=2,
        )

PREFIX = dict(
        new='tw-',
        deleted='del-',
        user='user-',
        recommend="rec-",
        alerts="alert-"
        )

TIME_KEY = "updated-at"

DEFAULT_IMAGE = "http://abs.twimg.com/sticky/default_profile_images/default_profile_4.png"

CACHE_TTL = 3600 # in seconds

PAGESIZE = 15 # no. of tweets per page

HEALTH_CHECK_IDS = dict(
        HEARTBEAT=os.getenv("HEALTHCHECK_ID_HEARTBEAT"),
        DELETECHECK=os.getenv("HEALTHCHECK_ID_DELETECHECK"),
        USER_REFRESH=os.getenv("HEALTHCHECK_ID_USERREFRESH"),
        HEARTBEAT_ON_RECEIVE=os.getenv("HEALTHCHECK_ID_HEARTBEAT_ON_RECEIVE")
        )

EXPORT_FILE = "/tmp/twoops-export.csv"

CLOUDSEARCH = dict(
        endpoint_url=os.getenv("CLOUDSEARCH_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET"),
        region_name=os.getenv("AWS_REGION")
        )
