"""
"""
import uuid
from pylitwoops.streaming import listener

def heart_beat():
    tw = listener.get_api()
    updated = tw.update_status(str(uuid.uuid4()))
    print "Heartbeat: %s" % updated.id
    return updated.id
