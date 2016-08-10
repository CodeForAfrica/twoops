"""
Stream listener
"""
import time
import redis
import tweepy
import logging
from pylitwoops.streaming.config import (
        TW_AUTH_CREDENTIALS, SENDER_ID, REDIS, PREFIX, TIME_KEY,
        HEARTBEAT_ACCOUNT)

PRINCIPLE_TW_HANDLE = 'pylitwoops'

LOGGERS = {}


def get_api(auth_only=False):
    """
    returns authenticated API object
    """
    try:
        creds = TW_AUTH_CREDENTIALS.get(PRINCIPLE_TW_HANDLE)
        auth = tweepy.OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
        auth.set_access_token(creds['access_token_key'], creds['access_token_secret'])
        if auth_only:
            return auth
        api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        return api
    except Exception, err:
        api_err = 'Cannot create API object: {}'.format(str(err))
        raise err


def get_redis():
    """
    return <redis.StrictRedis> instance
    """
    return redis.StrictRedis(**REDIS)


def epoch_to_date(time_in_epoch):
    """
    convert time in epoch to formatted datetime
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_in_epoch))


def check_rate_limits(endpoint="/statuses/show/:id"):
    '''
    '''
    try:
        tw = get_api()
        resp = tw.rate_limit_status()
        limits = resp['resources']['statuses'][endpoint]
        seconds_to_reset = limits['reset'] - time.time()
        print "{remaining} out of {limit} | Resetting in %d seconds".format(**limits) % int(seconds_to_reset)
        limits['seconds_to_reset'] = seconds_to_reset
        return limits

    except Exception, err:
        print "ERROR: Cannot get rate limits - %s" % str(err)


def get_users(raw=False):
    redis_client = get_redis()
    users = redis_client.keys("%s*" % PREFIX['user'])
    if raw:
        raw_users = []
        for each in users:
            raw_users.append(each.replace(PREFIX['user'], ''))
        return raw_users
    return users


class Listener(tweepy.StreamListener):
    """
    instance of tweepy's StreamListener
    """
    REDIS_CLIENT = get_redis()
    FILTER = get_users()

    def on_status(self, status):
        """
        do this when a status comes in
        """
        try:
            payload = dict(
                      request_id=status.id,
                      created_at=status.created_at,
                      sender_id=status.user.id,
                      username=status.user.screen_name,
                      avatar=status.user.profile_image_url.replace('_normal', ''),
                      message=str(status.text.encode('utf-8')),
                      saved="",
                      source=status.source
                      )

            prefixed_user_id = "%s%s" % (PREFIX['user'], status.user.id_str)
            if prefixed_user_id in FILTER and not status.user.id_str == HEARTBEAT_ACCOUNT:
                # persist tweet metadata
                store_key = PREFIX['new'] + str(payload['request_id'])
                payload['saved'] = REDIS_CLIENT.set(store_key.strip(), payload)

            if prefixed_user_id in FILTER:
                logging.info('{request_id} | {username} | {message} - {saved}'.format(
                        **payload))

        except Exception, err:
            logging.error('on_status -- {}'.format(str(err)))


    def on_dropped_connection(self,):
        """
        do this when Twitter closes connection
        """
        print "You probably need to restart me"

    
    def on_error(self, status_code):
        """
        handles errors
        """
        if int(status_code) == 420:
            # handle rate limiting
            return False
