"""
pylitwoops.worker.check tests
"""

import random
import unittest
from pylitwoops.streaming.listener import get_api
from pylitwoops.worker.check import loop

class WorkerTestCase(unittest.TestCase):
    
    def setUp(self,):
        pass


    def test_twitter_api(self,):
        '''
        '''
        twitter_clients = get_api(multi=True)
        self.assertIsInstance(twitter_clients, list)


    def test_loop(self,):
        random_list_one = ["one"]
        random_list_two = ["one", "two"]
        random_list_three = ["one", "two", "three"]
        random_list_four = ["one", "two", "three", "four"]

        self.assertTrue( loop(0, random_list_one) == 0 )

        self.assertTrue( loop(0, random_list_two) == 1 )
        self.assertTrue( loop(1, random_list_two) == 0 )

        self.assertTrue( loop(0, random_list_three) == 1 )
        self.assertTrue( loop(1, random_list_three) == 2 )
        self.assertTrue( loop(2, random_list_three) == 0 )
        
        self.assertTrue( loop(0, random_list_four) == 1 )
        self.assertTrue( loop(1, random_list_four) == 2 )
        self.assertTrue( loop(2, random_list_four) == 3 )
        self.assertTrue( loop(3, random_list_four) == 0 )



if __name__ == '__main__':
    unittest.main()
