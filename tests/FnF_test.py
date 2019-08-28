import unittest

class TestFnF(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_should_pass(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
	unittest.main()