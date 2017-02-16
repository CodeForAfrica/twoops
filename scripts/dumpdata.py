from twoops.streaming.listener import get_redis, PREFIX
from twoops.streaming import config
import csv, datetime


def export_deleted_tweets():
    '''
    exports deleted tweets to csv
    '''
    redis_client = get_redis()
    with open(config.EXPORT_FILE, 'w') as outputfile:
        csvwriter = csv.writer(outputfile)
        csvwriter.writerow(["id", "user", "text"])
        for tweet in redis_client.keys(config.PREFIX["deleted"] + "*"):
            try:
                tweet_payload = eval(redis_client.get(tweet))
                csvwriter.writerow(
                        [tweet_payload.get("request_id"),
                            tweet_payload.get("username"),
                            tweet_payload.get("message")] )
            except Exception, err:
                print "Failed for %s -- %s" % (tweet, err)


if __name__ == "__main__":
    export_deleted_tweets()
