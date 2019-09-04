import unittest
from unittest import mock
import os
import sys

from FnF import PathStr


class TestPathStr(unittest.TestCase):

    def setUp(self):
        if not os.sep == '/':
            print('tests only work on platforms that use "/" as a separator')
            sys.exit(1)

    def test_shouldSubClassString(self):
        ps = PathStr('/path/to')
        self.assertTrue(issubclass(type(ps), str))

    def test_shouldBehaveAsString_iterable(self):
        ps = PathStr('/path/to')
        s = ''
        for i, char in enumerate(ps):
            self.assertEqual(ps[i], char)
            s = s + char

        self.assertEqual(s, '/path/to')

    def test_shouldBeUsableAsDictKey(self):
        ps = PathStr('/path/to')
        d = {
            ps: 1
        }
        self.assertEqual(d[ps], 1)

    def test_shouldBehaveAsString_concatenation(self):
        ps = PathStr('/path/to')
        s = '/file'
        self.assertEqual(ps + s, '/path/to/file')

    def test_PathStrInit_withString(self):
        ps = PathStr('/path/to/file.ext')
        self.assertEqual(ps.path, '/path/to/')
        self.assertEqual(ps.filename, 'file')
        self.assertEqual(ps.ext, '.ext')
        self.assertFalse(ps.ispathstyle)
        self.assertEqual(ps.getPathAsList(), ['', 'path', 'to', 'file.ext'])

    def test_PathStrInit_withEmptyString(self):
        ps = PathStr('')
        self.assertEqual('', ps.path)
        self.assertEqual('', ps.filename)
        self.assertEqual('', ps.ext)
        self.assertFalse(ps.ispathstyle)
        self.assertEqual([], ps.getPathAsList())

    def test_PathStrInit_withSingleSlash(self):
        ps = PathStr('/')
        self.assertEqual('/', ps.path)
        self.assertEqual('', ps.filename)
        self.assertEqual('', ps.ext)
        self.assertTrue(ps.ispathstyle)
        self.assertEqual([''], ps.getPathAsList())

    def test_PathStrInit_withArray(self):
        ps = PathStr(['path', 'to'])
        self.assertEqual('path/to', ps)
        self.assertEqual('path/', ps.path)
        self.assertEqual('to', ps.filename)
        self.assertEqual('', ps.ext)
        self.assertFalse(ps.ispathstyle)
        self.assertEqual(['path', 'to'], ps.getPathAsList())

    def test_PathStrInit_withArrayAndSlashMarkers(self):
        ps = PathStr(['', 'path', 'to', ''])
        self.assertEqual('/path/to/', ps)
        self.assertEqual('/path/to/', ps.path)
        self.assertEqual('', ps.filename)
        self.assertEqual('', ps.ext)
        self.assertTrue(ps.ispathstyle)
        self.assertEqual(['', 'path', 'to', ''], ps.getPathAsList())

    def test_PathStrInit_withArrayDoubleSlashMarker(self):
        ps = PathStr(['', ''])
        self.assertEqual('/', ps)
        self.assertEqual('/', ps.path)
        self.assertEqual('', ps.filename)
        self.assertEqual('', ps.ext)
        self.assertTrue(ps.ispathstyle)
        self.assertEqual([''], ps.getPathAsList())

    def test_PathStrInit_withArraySingleSlashMarker(self):
        ps = PathStr([''])
        self.assertEqual('/', ps)
        self.assertEqual('/', ps.path)
        self.assertEqual('', ps.filename)
        self.assertEqual('', ps.ext)
        self.assertTrue(ps.ispathstyle)
        self.assertEqual([''], ps.getPathAsList())

    def test_PathStrInit_withEmptyArray(self):
        ps = PathStr([])
        self.assertEqual('', ps)
        self.assertEqual('', ps.path)
        self.assertEqual('', ps.filename)
        self.assertEqual('', ps.ext)
        self.assertFalse(ps.ispathstyle)
        self.assertEqual([], ps.getPathAsList())

    def test_PathStrParent_ofFile(self):
        ps = PathStr('/path/to/file.ext')
        self.assertEqual('/path/to/', ps.getParentFolder())

    def test_PathStrParent_ofFolder(self):
        ps = PathStr('/path/to/')
        self.assertEqual('/path/', ps.getParentFolder())
        self.assertEqual(['', 'path', ''], ps.getPathAsList())

    def test_PathStrRelativeTo_root(self):
        ps = PathStr('/path/to/file.ext')
        relativeTo = '/'
        relPs = ps.getPathRelativeTo(relativeTo)
        self.assertEqual('./path/to/file.ext', relPs)

    def test_PathStrRelativeTo_sameLevel(self):
        ps = PathStr('/path/to/file.ext')
        relativeTo = '/path/'
        relPs = ps.getPathRelativeTo(relativeTo)
        self.assertEqual('./to/file.ext', relPs)

    def test_PathStrRelativeTo_upOne(self):
        ps = PathStr('/path/to/file.ext')
        relativeTo = '/path/other/'
        relPs = ps.getPathRelativeTo(relativeTo)
        self.assertEqual('../to/file.ext', relPs)

    def test_PathStrRelativeTo_upTwo(self):
        ps = PathStr('/path/to/')
        relativeTo = '/path/other/another/'
        relPs = ps.getPathRelativeTo(relativeTo)
        self.assertEqual('../../to/', relPs)

    def test_PathStrRelativeTo_upOneNoRoot(self):
        ps = PathStr('path/to/file.ext')
        relativeTo = 'path/other/'
        relPs = ps.getPathRelativeTo(relativeTo)
        self.assertEqual('../to/file.ext', relPs)

    def test_PathStrRelativeTo_differentRoots(self):
        ps = PathStr('path/to/file.ext')
        relativeTo = 'other/'
        with self.assertRaises(RuntimeError) as context:
            ps.getPathRelativeTo(relativeTo)
            self.assertTrue(
                'relative paths can only be calculated from paths with a common root'
                in context.exception
            )

    @mock.patch('PathStr.os.stat')
    def test_exists_exists(self, mock_stat):
        mock_stat.return_value = {}
        ps = PathStr('/path/to/file.ext')
        self.assertTrue(ps.exists)

    @mock.patch('PathStr.os.stat')
    def test_exists_noExists(self, mock_stat):
        mock_stat.side_effect = FileNotFoundError()
        ps = PathStr('/path/to/file.ext')
        self.assertFalse(ps.exists)

    @mock.patch('PathStr.os.stat')
    def test_isdir_noExists(self, mock_stat):
        mock_stat.side_effect = FileNotFoundError()
        ps = PathStr('/path/to/')
        self.assertFalse(ps.isdir)

    @mock.patch('PathStr.stat.ST_MODE', 'ST_MODE')
    @mock.patch('PathStr.stat.S_ISDIR')
    @mock.patch('PathStr.os.stat')
    def test_isdir_false(self, mock_stat, mock_S_ISDIR):
        mock_stat.return_value = {'ST_MODE': 42}
        mock_S_ISDIR.return_value = False
        ps = PathStr('/path/to/')
        self.assertFalse(ps.isdir)

    @mock.patch('PathStr.stat.ST_MODE', 'ST_MODE')
    @mock.patch('PathStr.stat.S_ISDIR')
    @mock.patch('PathStr.os.stat')
    def test_isdir_true(self, mock_stat, mock_S_ISDIR):
        mock_stat.return_value = {'ST_MODE': 42}
        mock_S_ISDIR.return_value = True
        ps = PathStr('/path/to/')
        self.assertTrue(ps.isdir)

    def test_join_1(self):
        ps = PathStr('/path/to/')
        ps2 = PathStr('/other')
        ps3 = PathStr.join(ps, ps2)
        self.assertEqual('/path/to/other', ps3)

    def test_join_2(self):
        ps = PathStr('/path/to/')
        ps2 = PathStr('other')
        ps3 = PathStr.join(ps, ps2)
        self.assertEqual('/path/to/other', ps3)

    def test_join_3(self):
        ps = PathStr('/path/to/')
        ps2 = PathStr('./other')
        ps3 = PathStr.join(ps, ps2)
        self.assertEqual('/path/to/other', ps3)

    def test_join_4(self):
        ps = PathStr('/path/to/')
        ps2 = PathStr('../other')
        ps3 = PathStr.join(ps, ps2)
        self.assertEqual('/path/other', ps3)

    def test_join_5(self):
        ps = PathStr('/path/./to/')
        ps2 = PathStr('../../other')
        ps3 = PathStr.join(ps, ps2)
        self.assertEqual('/other', ps3)

    def test_join_6(self):
        ps = PathStr('/path/to/')
        ps2 = PathStr('../other')
        ps3 = PathStr('../another')
        ps4 = PathStr.join(ps, ps2, ps3)
        self.assertEqual('/path/another', ps4)

    def test_join_7(self):
        ps = PathStr('/path/to/')
        ps2 = PathStr('../../../other')
        with self.assertRaises(RuntimeError) as context:
            PathStr.join(ps, ps2)
            self.assertTrue(
                'too many "../", overflowed in front of path'
                in context.exception
            )

    def test_lt_1(self):
        ps1 = PathStr('wallpaper-266390[1]')
        ps2 = PathStr('wallpaper-2656946')
        self.assertLess(ps1, ps2)

    def test_lt_2(self):
        ps1 = PathStr('wallpaper-2656946')
        ps2 = PathStr('wallpaper-2656946[1]')
        self.assertLess(ps1, ps2)

    def test_lt_3(self):
        ps1 = PathStr('wallpaper-365')
        ps2 = PathStr('wallpaper-2656946')
        self.assertLess(ps1, ps2)

    def test_lt_4(self):
        ps1 = PathStr('/path1/wallpaper-365')
        ps2 = PathStr('/path2/wallpaper-265')
        self.assertLess(ps1, ps2)

    def test_lt_5(self):
        ps1 = PathStr('/pathA/wallpaper-365')
        ps2 = PathStr('/pathB/wallpaper-265')
        self.assertLess(ps1, ps2)

    def test_lt_6(self):
        ps1 = PathStr('/pathA/wallpaper')
        ps2 = PathStr('/pathA/wallpaper')
        self.assertFalse(ps1 < ps2)
        self.assertFalse(ps2 < ps1)

if __name__ == '__main__':
    unittest.main()
