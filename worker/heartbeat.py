"""
"""
import uuid
from pylitwoops.streaming import listener

def heart_beat():
    tw = listener.get_api()
    msg = "heartbeat - %s" % str(uuid.uuid4())
    updated = tw.update_status(msg)
    print "Heartbeat: %s" % updated.id
    return updated.id

if __name__ == '__main__':
    heart_beat()
