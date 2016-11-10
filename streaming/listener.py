"""
Stream listener
"""
import time
import redis
import tweepy
import logging
from pylitwoops.monitor import health_check
from pylitwoops.streaming import config
from pylitwoops.streaming.config import (
        TW_AUTH_CREDENTIALS, SENDER_ID, REDIS, PREFIX, TIME_KEY,
        HEARTBEAT_ACCOUNT, PRINCIPLE_TW_HANDLE)

LOGGERS = {}


def get_api(auth_only=False, multi=False):
    """
    auth_only: return the OauthHandler object if True; else return the API object
    multi:     return multiple API client objects (if available), else: only return one API client object
    """
    try:
        api_objects = []
        auth_objects = []
        for account in TW_AUTH_CREDENTIALS:
            creds = TW_AUTH_CREDENTIALS.get(account)
            auth = tweepy.OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
            auth.set_access_token(creds['access_token_key'], creds['access_token_secret'])
            auth_objects.append(auth)

            api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
            api_objects.append(api)

        if auth_only:
            return auth_objects[0] if not multi else auth_objects

        return api_objects[0] if not multi else api_objects
    
    except Exception, err:
        api_err = 'Cannot create API object: {}'.format(str(err))
        raise err


def get_redis(db=5):
    """
    return <redis.StrictRedis> instance
    """
    REDIS["db"] = db
    return redis.StrictRedis(**REDIS)


def epoch_to_date(time_in_epoch):
    """
    convert time in epoch to formatted datetime
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_in_epoch))



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

    def on_status(self, status):
        """
        do this when a status comes in
        """
        try:
            filter_ = get_users()
            redis_client = get_redis()
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
            if prefixed_user_id in filter_ and not status.user.id_str == HEARTBEAT_ACCOUNT:
                # persist tweet metadata
                store_key = PREFIX['new'] + str(payload['request_id'])
                payload['saved'] = redis_client.set(store_key.strip(), payload)

            if prefixed_user_id in filter_:
                logging.info('{request_id} | {username} | {message} - {saved}'.format(
                        **payload))

            if status.user.id_str == HEARTBEAT_ACCOUNT:
                health_check(config.HEALTH_CHECK_IDS["HEARTBEAT_ON_RECEIVE"])

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
