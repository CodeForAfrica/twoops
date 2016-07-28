"""
check if tweet has been deleted
"""
import datetime
from pylitwoops.streaming.listener import get_redis, get_api, tweepy

def main():
    twitter_client = get_api()
    redis_client = get_redis()
    entries = redis_client.keys("*")
    print "Going through %s entries" % len(entries)
    for entry in entries:
        saved_status = eval(redis_client.get(entry))
        try:
            status = twitter_client.get_status(str(entry))
            print "%s intact" % entry
        except tweepy.error.TweepError, err:
            if err.message[0]['code'] == 144:
                print "{request_id} Deleted!!!  --  {username} said {message}".format(**saved_status)
            else:
                print "Unexpected response for %s -- %s" % (entry, err)


if __name__ == '__main__':
    main()
