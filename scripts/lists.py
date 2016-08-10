"""
Lists manipulation

Usage:
    python scripts/lists.py create test-two private

    python scripts/lists.py add 763292547754131456 3332342333,183165874,726748106,295663598,2515899612

    python scripts/lists.py list 763292547754131456

"""
import sys
from pylitwoops.streaming import listener, config


def new_list(list_name, mode='private'):
    t = listener.get_api()
    created = t.create_list(name=list_name, mode=mode)
    print "Created %s list: %s - %s" % (mode, created.name, created.id)
    return created


def add_list_member(list_id, members=[]):
    t = listener.get_api()
    for member in members:
        assert isinstance(member, int)
    added = t.add_list_members(user_id=members, list_id=int(list_id))
    print "Added %s members to %s" % (len(members), added.id)
    return added


def list_members(list_id):
    t = listener.get_api()
    members = t.list_members(list_id=int(list_id), count=500)
    for member in members:
        print "%s :: @%s" % (member.id, member.screen_name)
    return members



if __name__ == "__main__":
    actions = ['create', 'add', 'list']
    action = sys.argv[1]
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
    elif action == 'list':
        list_id = sys.argv[2]
        list_members(int(list_id))
