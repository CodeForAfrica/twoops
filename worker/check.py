"""
check if tweet has been deleted
"""
import datetime, time
from pylitwoops.streaming.listener import (
        get_redis, get_api, tweepy, PREFIX, TIME_KEY)

def main():
    twitter_client = get_api()
    redis_client = get_redis()
    entries = redis_client.keys("%s*" % PREFIX['new'])
    print "Going through %s entries" % len(entries)
    delete_count = 0
    for entry in entries:
        saved_status = eval(redis_client.get(entry))
        status_id = entry.replace(PREFIX['new'], '')

        try: # check if it's still on twitter
            status = twitter_client.get_status(status_id)
            print "%s check" % entry
        except tweepy.error.TweepError, err:
            deleted = redis_client.delete(entry)
            print "ER: %s -- %s -- %s" % (entry, err, deleted)
             
            if err.message[0]['code'] == 144:
                store_key = PREFIX['deleted'] + str(status_id)
                saved_status['saved'] = redis_client.set(store_key, saved_status)
                print "DELETED!!!  --  {request_id}  --  {username}: {message} -- {saved}".format(**saved_status)
                delete_count += 1
            else:
                print "Unexpected response for %s -- %s" % (entry, err)
        except Exception, other_error:
            print "Unexpected response for %s -- %s" % (entry, other_error)

    
    now = time.asctime()
    print "Last update: %s | Last run delete count: %s" % (now, delete_count)
    redis_client.set(TIME_KEY, now)


if __name__ == '__main__':
    main()
