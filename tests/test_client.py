import unittest
from basepy.client import BaseClient
from basepy.utils import BASE_MAINNET_CHAIN_ID

class TestBaseClient(unittest.TestCase):
    def test_connection(self):
        client = BaseClient()
        self.assertTrue(client.is_connected())
        self.assertEqual(client.get_chain_id(), BASE_MAINNET_CHAIN_ID)

if __name__ == '__main__':
    unittest.main()
