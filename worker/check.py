"""
check if tweet has been deleted
"""
import boto3
import requests
import datetime, time, math
from pylitwoops.streaming import config
from pylitwoops.monitor import health_check
from pylitwoops.streaming.listener import (
        get_redis, tweepy, PREFIX, TIME_KEY)
from pylitwoops.data.tweet_template import template
#from pylitwoops.web import app


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


def index_for_search(status_payload):
    """
    """
    try:
        status_payload_json = template % (status_payload["request_id"],
                status_payload["username"], status_payload["request_id"], status_payload["message"])
        cloudsearch_client = boto3.client("cloudsearchdomain", **config.CLOUDSEARCH)
        cloudsearch_client.upload_documents(documents=status_payload_json, contentType='application/json')
    except Exception, err:
        print "ERROR - index_for_search() - %s - %s" % (err, status_payload)

        
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
            saved_status = eval(redis_client.get(entry))
            status_id = entry.replace(PREFIX['new'], '')
            sender_id = saved_status["sender_id"]

            try: # check if it's still on twitter
                status = requests.get("https://twitter.com/{username}/status/{request_id}".format(
                    **saved_status))
                print "%s check | %s" % (entry, status.status_code)
                status.raise_for_status()

            except requests.exceptions.HTTPError:
                deleted = redis_client.delete(entry)
                print "ERR: %s -- %s" % (entry, deleted)
                 
                if status.status_code == 404:
                    store_key = PREFIX['deleted'] + str(status_id)
                    saved_status['saved'] = redis_client.set(store_key, saved_status)
                    print "DELETED!!!  --  {request_id}  --  {username}: {message} -- {saved}".format(**saved_status)

                    # append to user deleted list
                    sender_key = "user-" + str(sender_id)
                    size = redis_client_user.rpush(sender_key, store_key)
                    print "rpush'ed %s - new size: %s" % (sender_key, size)

                    # send out alerts
                    subscribers_key = config.PREFIX["alerts"] + str(sender_id)
                    subscribers = redis_client.lrange(subscribers_key, 0, -1)
                    for subscriber in subscribers:
                        subject = "Twoops Alert: @{username} deleted a tweet".format(**saved_status)
                        #app.send_mail(subscriber, subject, saved_status)
                    print "%s has %s subscribers" % (saved_status["sender_id"], len(subscribers))

                    # index for search
                    index_for_search(saved_status)
                    delete_count += 1
                else:
                    print "Unexpected response for %s -- %s: %s" % (
                            entry, status.status_code, status.reason)


            except Exception, other_error:
                print "Unexpected response for %s -- %s" % (entry, other_error)


    duration = datetime.datetime.now() - start_time
    now = time.asctime() + '|' + str(delete_count)
    print "Last updated: %s | Latest delete count: %s | Duration: %s seconds" % (now, delete_count, duration.seconds)
    redis_client.set(TIME_KEY, now)
    health_check(config.HEALTH_CHECK_IDS["DELETECHECK"])



if __name__ == '__main__':
    main()
