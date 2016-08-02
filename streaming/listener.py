"""
Stream listener
"""
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
        api = tweepy.API(auth)
        return api
    except Exception, err:
        api_err = 'Cannot create API object: {}'.format(str(err))
        raise err


def get_redis():
    """
    return <redis.StrictRedis> instance
    """
    return redis.StrictRedis(**REDIS)

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


    def on_error(self, status_code):
        """
        handles errors
        """
        if int(status_code) == 420:
            # handle rate limiting
            return False
