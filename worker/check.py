"""
check if tweet has been deleted
"""
import datetime, time, math
from pylitwoops.streaming.listener import (
        get_redis, get_api, tweepy, PREFIX, TIME_KEY,
        check_rate_limits)


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
    twitter_client = get_api()
    redis_client = get_redis()
    entries = redis_client.keys("%s*" % PREFIX['new'])

    chunk_size = 160  # because twitter api rate limit is 180
    chunks = chunkify(entries, chunk_size)
    print "[%s] - Going through %s entries... Broken down in %s chunks" % (
            datetime.datetime.now(), len(entries), len(chunks))

    for chunk in chunks:
        # run chunk; then check rate limit
        delete_count = 0
        for entry in chunk:
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


        if len(chunks) > 1:
            # can we run another chunk at current rate limits?
            rate_limits = check_rate_limits()
            if rate_limits['remaining'] >= chunk_size:
                print "[%s]: Remaining allowance in this window: {remaining} | No time to sleep".format(**rate_limits) % datetime.datetime.now()
                continue
            else:
                print "[%s]: Allowance in this window: {remaining} | Sleeping for {seconds_to_reset} secs".format(**rate_limits) % datetime.datetime.now()
                sleep_time = rate_limits['seconds_to_reset'] + 1

                now = time.asctime() + '|' + str(delete_count)
                print "Last update: %s | Last run delete count: %s" % (now, delete_count)
                redis_client.set(TIME_KEY, now)
                time.sleep(sleep_time)

                continue

        now = time.asctime() + '|' + str(delete_count)
        print "Last update: %s | Last run delete count: %s" % (now, delete_count)
        redis_client.set(TIME_KEY, now)

if __name__ == '__main__':
    main()
