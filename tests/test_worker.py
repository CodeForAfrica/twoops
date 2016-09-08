"""
pylitwoops.worker.check tests
"""

import random
import unittest
from pylitwoops.streaming.listener import get_api

class WorkerTestCase(unittest.TestCase):
    
    def setUp(self,):
        pass


    def test_twitter_api(self,):
        '''
        '''
        twitter_clients = get_api(multi=True)
        self.assertIsInstance(twitter_clients, list)





if __name__ == '__main__':
    unittest.main()
