"""
Lists manipulation

Usage:
    python scripts/lists.py create <list-name> <private/public>

    python scripts/lists.py add <list-id> <user-id-1>,<user-id-2>,<user-id-3>

    python scripts/lists.py list_by_id <list-id>

    python scripts/lists.py list_by_name <name> <list-name>

    python scripts/lists.py import <from-list> <to-list>

    python scripts/lists.py refresh <list-id>

"""
import sys, time
from pylitwoops.streaming import listener, config
from pylitwoops.worker.check import chunkify
from pylitwoops.monitor import health_check
from pylitwoops.streaming import config


def new_list(list_name, mode='private'):
    """
    creates a new private (unless specified by `mode`) Twitter List
    """
    t = listener.get_api()
    created = t.create_list(name=list_name, mode=mode)
    print "Created %s list: %s - %s" % (mode, created.name, created.id)
    return created


def add_list_member(list_id, members=[]):
    """
    Adds members whose USER_IDs are in `members` to list `list_id`

    @list_id:  an <int> ID of the Twitter List
    @members:  a <list> of user <int> USER_IDs
    """
    t = listener.get_api()
    for member in members:
        assert isinstance(member, int)
    added = t.add_list_members(user_id=members, list_id=int(list_id))
    print "Added %s members to %s" % (len(members), added.id)
    return added


def list_members(list_id):
    """
    Returns up to 500 members of list `list_id`
    """
    t = listener.get_api()
    members = t.list_members(list_id=int(list_id), count=500)
    for member in members:
        print "%s :: @%s" % (member.id, member.screen_name)
    print "%s members" % len(members)
    return members


def list_members_by_name(owner_name, list_slug):
    """
    Returns up to 500 members of the list `list_slug` owned by `owner_name`
    """
    t = listener.get_api()
    _list = t.get_list(owner_screen_name=str(owner_name), slug=str(list_slug))
    members = t.list_members(owner_screen_name=str(owner_name), slug=str(list_slug), count=500)
    for member in members:
        print "%s :: @%s" % (member.id, member.screen_name)
    print "%s members in %s's list '%s' list_id: %s" % (len(members), owner_name, list_slug, _list.id)
    return members


def refresh(list_id):
    """
    Fetches members of list `list_id` from Twitter and adds them to cache.
    """
    r = listener.get_redis()
    members = list_members(list_id)
    for member in members:
        user_key = "%s%s" % (config.PREFIX['user'], str(member.id))
        print r.set(user_key, member._json)
    print "Saved %s members from list %s" % (len(members), list_id)
    r.save()
    health_check(config.HEALTH_CHECK_IDS["USER_REFRESH"])


def _import(from_list_id, to_list_id):
    """
    Imports users from Twitter List `from_list_id` to Twitter List `to_list_id`

    @from_list_id:  <int>  The ID of the Twitter List from which to import
    @to_list_id:    <int>  The ID of the Twitter List to add imported users
    """
    t = listener.get_api()
    from_list = t.get_list(list_id=int(from_list_id))
    to_list = t.get_list(list_id=int(to_list_id))
    print "Importing members of %s's list '%s' to %s's list '%s'..." % (
            from_list.user.screen_name,
            from_list.name,
            to_list.user.screen_name,
            to_list.name
            )
    time.sleep(4)
    from_members = list_members(int(from_list_id))
    to_members = []
    for member in from_members:
        to_members.append(member.id)

    chunks = chunkify(to_members, 50)
    for chunk in chunks:
        add_list_member(int(to_list_id), chunk)
        print "imported %s members from %s to %s" % (len(chunk), from_list_id, to_list_id)


if __name__ == "__main__":
    actions = ['create', 'add', 'list_by_id', 'list_by_name', 'refresh', 'import']
    action = sys.argv[1]
    if action not in actions:
        print "Unknown action"
        sys.exit(2)
    if action == 'create':
        list_name = sys.argv[2]
        mode = sys.argv[3]
        new_list(list_name, mode)
    elif action == 'add':
        list_id = sys.argv[2]
        members = []
        for _id in sys.argv[3].split(","):
            members.append(int(_id))
        add_list_member(list_id, members)
    elif action == 'list_by_id':
        list_id = sys.argv[2]
        list_members(int(list_id))
    elif action == 'list_by_name':
        owner_name = sys.argv[2]
        list_slug = sys.argv[3]
        list_members_by_name(owner_name, list_slug)
    elif action == 'refresh':
        list_id = sys.argv[2]
        refresh(list_id)
    elif action == 'import':
        from_list_id = sys.argv[2]
        to_list_id = sys.argv[3]
        _import(from_list_id, to_list_id)
