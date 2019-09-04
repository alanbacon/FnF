import unittest
from unittest import mock

from FnF import splitSep

class TestSplitSep(unittest.TestCase):
 
    def setUp(self):
        pass
 
    @mock.patch('SplitSep.os.sep', '$')
    def test_should_split_paths_using_sep(self):
        paths = '/path1$/path/to'
        splitPaths = splitSep([paths])
        self.assertEqual(splitPaths, [
            [
                '/path1',
                '/path/to'
            ]
        ])


if __name__ == '__main__':
    unittest.main()