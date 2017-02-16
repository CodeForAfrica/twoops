from twoops.streaming import listener
from twoops.streaming.config import LOGGING
import tweepy, logging

print "Creating logger..."
logging.basicConfig(filename=LOGGING['location'],
        level=LOGGING['level'],
        format=LOGGING['format'])
logging.info('Started')


logging.info("Initiating stream...")
lstnr = listener.Listener()
tweepy.Stream(
        listener.get_api(auth_only=True), lstnr).filter(
                follow=listener.get_users(raw=True))
logging.info("Stream started.")
