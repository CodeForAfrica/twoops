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
                        send_email_alert(subscriber, subject, saved_status)
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


def send_email_alert(to, subject, message):
    try:
        endpoint = 'https://api.sendgrid.com/v3/mail/send'
        payload = {
            "personalizations":[{
                "to":[{
                        "email": to
                    }]
                }],
            "from": {
                "email": "support@codeforafrica.org"
            },
            "subject": subject,
            "content": [{
                    "type": "text/html", "value": get_template(to, message)
                }]
            }
        headers = {
            'Authorization': 'Bearer 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',
            'Content-Type': 'application/json'
        }
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
        return response
    except Exception, err:
        print "ERROR: Could not send email alert - %s -- %s" % (message, err)

def get_template(to, message):
    markup = '<html><head><link href="https://fonts.googleapis.com/css?family=Poppins" rel="stylesheet" type="text/css"></head>'
    markup += '<body style=\'font-family:"poppins"; font-size:18px; color:#333;"\'>'
    markup += '<div style="background-color:#f0f0f0;width:100%;height:450px">'
    markup += '<div style="background-color:#0D68A8; color:#fff;height:80px;padding:20px 0px;">'
    markup += '<div style="margin:0 auto;font-size:30px;border:3px solid #fff;padding:5px;width:128px;">Tw<i>oops</i>!</center></div>'
    markup += '<br clear="all"><br clear="all">'
    markup += '<div style="margin:0 auto; width:600px; height:auto;padding:20px;background-color:#fff;color:#333;">'
    markup += '<div style=""><h4><a href="">@'+ message['username'].encode('utf-8') +'</a> deleted this tweet just now:</h4> '
    markup += '<h1>'+ message['message'].encode('utf-8') +'</h1></div><br>'
    markup += '<a href="https://twoops.codeforafrica.tech/tweet?id='+ str(message['request_id']) +'">View this tweet</a>'
    markup += '<br><br><br>'
    markup += '<small>This was sent to you because you subscribed to <a href="https://twoops.codeforafrica.tech/">Twoops!</a><br>'
    markup += '<a href="https://twoops.codeforafrica.tech/unsubscribe?email='+ to +'&user_id='+ str(message['sender_id']) +'">Unsubscribe</a></small>'
    markup += '</div></div></body></html>'
    return markup

# Sample request
# send_mail('muthoni90@gmail.com', 'Test email', {'username': 'muthonieve', 'message': 'I can\'t believe I tweeted this', 'request_id': '23123', 'user_id':'121233'})

if __name__ == '__main__':
    main()
