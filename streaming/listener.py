"""
Stream listener
"""
import time
import redis
import tweepy
import logging
from pylitwoops.streaming.config import (
        TW_AUTH_CREDENTIALS, SENDER_ID, FILTER, REDIS, PREFIX, TIME_KEY)

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


class Listener(tweepy.StreamListener):
    """
    instance of tweepy's StreamListener
    """

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
                      message=str(status.text.encode('utf-8'))
                      )

            if status.user.id_str in FILTER:
                # persist tweet metadata
                redis_client = get_redis()
                store_key = PREFIX['new'] + str(payload['request_id'])
                payload['saved'] = redis_client.set(store_key.strip(), payload)

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
