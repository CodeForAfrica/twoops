"""
check if tweet has been deleted
"""
import requests
import datetime, time, math
from pylitwoops.streaming.listener import (
        get_redis, tweepy, PREFIX, TIME_KEY)


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
                status = requests.get("https://twitter.com/{username}/status/{request_id}".format(**saved_status))
                print "%s check | %s" % (entry, status.status_code)
                status.raise_for_status()

            except requests.exceptions.HTTPError:
                deleted = redis_client.delete(entry)
                print "ERR: %s -- %s" % (entry, deleted)
                 
                if status.status_code == 404:
                    store_key = PREFIX['deleted'] + str(status_id)
                    saved_status['saved'] = redis_client.set(store_key, saved_status)
                    print "DELETED!!!  --  {request_id}  --  {username}: {message} -- {saved}".format(**saved_status)
                    delete_count += 1
                else:
                    print "Unexpected response for %s -- %s: %s" % (entry, status.status_code, status.reason)


            except Exception, other_error:
                print "Unexpected response for %s -- %s" % (entry, other_error)


    duration = datetime.datetime.now() - start_time
    now = time.asctime() + '|' + str(delete_count)
    print "Last update: %s | Last run delete count: %s | Duration: %s seconds" % (now, delete_count, duration.seconds)
    redis_client.set(TIME_KEY, now)

if __name__ == '__main__':
    main()
