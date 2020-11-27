from skypull import skypull
import unittest


class TestHTTPResponses(unittest.TestCase):
    def setUp(self):
        self.client = skypull.SkyGrab()

    def test_empty_events(self):
        with self.assertRaises(Exception) as context:
            self.client.get_events()
        self.assertTrue('No parameters specified' in str(context.exception))

    def test_default_invoices(self):
        self.assertIsInstance(self.client.get_invoices(), list)

    def test_get_zone_inventory(self):
        self.assertIsInstance(self.client.get_sold_inventory(), list)

    def test_get_inventory(self):
        self.assertIsInstance(self.client.get_inventory(), list)

    def test_get_vendors(self):
        self.assertIsInstance(self.client.get_vendors(), list)


if __name__ == '__main__':
    unittest.main()
