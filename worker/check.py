"""
check if tweet has been deleted
"""
import boto3
import requests, json
import datetime, time, math
from twoops.streaming import config
from twoops.monitor import health_check
from twoops.streaming.listener import (
        get_redis, tweepy, PREFIX, TIME_KEY)
from twoops.data.tweet_template import template
from twoops.worker.celery_checker import check_tweet

def chunkify(list_, size):
    '''
    break down list to chunks of size `size` each.

    returns a list of lists of size `size`

    @list:   a <list> element
    @size:   the maximum chunk size.  an <int>
    '''
    if len(list_) <= size:
        return [list_]
    else:
        chunks = len(list_) / float(size)
        resp = []
        limit = 0
        for item in range(1, int(math.ceil(chunks)) + 1):
            resp.append(list_[limit:limit+size])
            limit += size
        return resp

        
def main():
    """
    """
    start_time = datetime.datetime.now()
    redis_client = get_redis()
    redis_client_user = get_redis(config.redis_databases["users"])
    entries = redis_client.keys("%s*" % PREFIX['new'])

    chunk_size = 160  # because twitter api rate limit is 180
    chunks = chunkify(entries, chunk_size)
    print "[%s] - Going through %s entries... Broken down in %s chunks" % (
            datetime.datetime.now(), len(entries), len(chunks))

    for chunk in chunks.__reversed__():
        # run chunk; then check rate limit
        delete_count = 0
        for entry in chunk:
            check_tweet.delay(entry)

    duration = datetime.datetime.now() - start_time
    now = time.asctime() + '|' + str(delete_count)
    print "Last updated: %s | Latest delete count: %s | Duration: %s seconds" % (now, delete_count, duration.seconds)
    #redis_client.set(TIME_KEY, now)
    #health_check(config.HEALTH_CHECK_IDS["DELETECHECK"])


if __name__ == '__main__':
    main()
