"""
loop through all deleted tweets and index them on another redis
database by sender_id
"""
import datetime
from pylitwoops.streaming import config
from pylitwoops.streaming import listener


if __name__ == "__main__":
    redis_users = listener.get_redis(config.redis_databases["users"])
    redis_tweets = listener.get_redis(config.redis_databases["tweets"])
    for entry in redis_tweets.keys("del-*"):
        sender_id = eval(redis_tweets.get(entry))["sender_id"]
        sender_key = "user-" + str(sender_id)
        added = redis_users.rpush(sender_key, entry)
        print "%s - %s - %s" % (sender_key, entry, added)
