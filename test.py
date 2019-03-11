import unittest
from main import simple_get

class TestSimple_Get(unittest.TestCase):
    def test_bad_url(self):
        url = 'bad'
        result = simple_get(url)
        self.assertEqual(result, None)

    def test_good_url(self):
        url = 'http://books.toscrape.com/catalogue/page-50.html'
        result = simple_get(url)
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
