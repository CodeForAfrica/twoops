import boto3
from twoops.data.user_template import template
from twoops.streaming import listener, config
from twoops.monitor import health_check

handle = "davidlemayian"
extras = {'country': 'Kenya', 'occupation':'engineer', 'type':'person'}

def get_user_profile(handle, extras):
    t = listener.get_api()
    member = t.get_user(handle)
    payload = dict(
        request_id=member.id,
        username=member.screen_name,
        name=member.name,
        country=extras['country'],
        occupation=extras['occupation'],
        type=extras['type']
    )
    return member, payload

def index_member_for_search(member):
    """
        Saves the user to CloudSearch
    """
    try:
        member_json = template % (
                            member["request_id"],
                            member["request_id"],
                            member["username"],
                            member["name"],
                            member["country"],
                            member["type"],
                            member["occupation"]
                        )
        cloudsearch_client = boto3.client("cloudsearchdomain", **config.CLOUDSEARCH_USERS)
        response = cloudsearch_client.upload_documents(documents=member_json, contentType='application/json')
        print response
    except Exception, err:
        print "ERROR - index_member_for_search() - %s - %s" % (err, member)



def add_member_to_twitter_list(list_id, members=[]):
    """
    Adds members whose USER_IDs are in `members` to list `list_id`

    @list_id:  an <int> ID of the Twitter List
    @members:  a <list> of user <int> USER_IDs
    """
    t = listener.get_api()
    for member in members:
        assert isinstance(member, int)
    added = t.add_list_members(user_id=members, list_id=int(list_id)) # Twitter API, Adds a user to a twitter list
    print "Added %s members to %s" % (len(members), added.id)
    return added


def add_member_to_redis(member):
    """
    Save the new member to redis
    """
    r = listener.get_redis()
    user_key = "%s%s" % (config.PREFIX['user'], str(member.id))
    print r.set(user_key, member)
    print "Saved member to redis id %s" % (member.id)
    r.save()
    health_check(config.HEALTH_CHECK_IDS["USER_REFRESH"])

def save_user(handle, extras):
    member, payload = get_user_profile(handle, extras)
    index_member_for_search(payload)
    add_member_to_twitter_list(config.LIST_IDS[0], [payload["request_id"]])
    add_member_to_redis(member)

if __name__ == "__main__":
    save_user(handle, extras)s