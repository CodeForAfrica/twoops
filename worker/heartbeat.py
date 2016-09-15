"""
"""
import uuid
from pylitwoops.monitor import health_check
from pylitwoops.streaming import listener, config

def heart_beat():
    tw = listener.get_api()
    msg = "heartbeat - %s" % str(uuid.uuid4())
    updated = tw.update_status(msg)
    health_check(config.HEALTH_CHECK_IDS["HEARTBEAT"])
    print "Heartbeat: %s" % updated.id
    return updated.id

if __name__ == '__main__':
    heart_beat()
