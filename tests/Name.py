from ..Name import Name

from typing import List

import unittest


class NameTests(unittest.TestCase):
    def test_next_digits(self):
        self.assertEqual(Name.fromStr("1").next(), Name.fromStr("2"))
        self.assertEqual(Name.fromStr("9").next(), Name.fromStr("10"))
        self.assertEqual(Name.fromStr("19").next(), Name.fromStr("20"))

    def test_next_letters(self):
        self.assertEqual(Name.fromStr("a").next(), Name.fromStr("b"))
        self.assertEqual(Name.fromStr("z").next(), Name.fromStr("aa"))
        self.assertEqual(Name.fromStr("az").next(), Name.fromStr("ba"))
        self.assertEqual(Name.fromStr("zz").next(), Name.fromStr("aaa"))

    def test_next_mixed(self):
        # this is arbitary
        self.assertEqual(Name.fromStr("").next(), Name.fromStr("1"))

        self.assertEqual(Name.fromStr("1a").next(), Name.fromStr("1b"))
        self.assertEqual(Name.fromStr("1z").next(), Name.fromStr("1aa"))

        self.assertEqual(Name.fromStr("a1").next(), Name.fromStr("a2"))
        self.assertEqual(Name.fromStr("a9").next(), Name.fromStr("a10"))

        self.assertEqual(Name.fromStr("a1a").next(), Name.fromStr("a1b"))
        self.assertEqual(Name.fromStr("a1z").next(), Name.fromStr("a1aa"))

        self.assertEqual(Name.fromStr("1a1").next(), Name.fromStr("1a2"))
        self.assertEqual(Name.fromStr("1a9").next(), Name.fromStr("1a10"))

    def test_lt(self):
        self.assertTrue(Name.fromStr("a") < Name.fromStr("b"))
        self.assertTrue(Name.fromStr("1") < Name.fromStr("1a"))
        self.assertTrue(Name.fromStr("1a") < Name.fromStr("1b"))
        self.assertTrue(Name.fromStr("1a") < Name.fromStr("2"))

        # This is arbitary:
        self.assertTrue(Name.fromStr("1") < Name.fromStr("a"))

        self.assertFalse(Name.fromStr("a") < Name.fromStr("a"))
        self.assertFalse(Name.fromStr("1b") < Name.fromStr("1a"))
        self.assertFalse(Name.fromStr("1a") < Name.fromStr("1"))

    def test_eq(self):
        self.assertTrue(Name.fromStr("a") == Name.fromStr("a"))
        self.assertTrue(Name.fromStr("1a") == Name.fromStr("1a"))
        self.assertTrue(Name.fromStr("a1") == Name.fromStr("a1"))

        self.assertFalse(Name.fromStr("1") == Name.fromStr("1a"))
        self.assertFalse(Name.fromStr("1") == Name.fromStr("a1"))
        self.assertFalse(Name.fromStr("a") == Name.fromStr("1a"))
        self.assertFalse(Name.fromStr("a") == Name.fromStr("a1"))

    def test_findNext(self):
        names = [Name.fromStr(n) for n in ["1", "2"]]
        self.assertEqual(Name.findNext(names, Name.fromStr("")), Name.fromStr("3"))
        self.assertEqual(Name.findNext(names, Name.fromStr("2")), Name.fromStr("2a"))

        names = [Name.fromStr(n) for n in ["1", "2", "4"]]
        self.assertEqual(Name.findNext(names, Name.fromStr("")), Name.fromStr("3"))
        self.assertEqual(Name.findNext(names, Name.fromStr("2")), Name.fromStr("2a"))

        names = [Name.fromStr(n) for n in ["1", "2", "2a", "2b"]]
        self.assertEqual(Name.findNext(names, Name.fromStr("")), Name.fromStr("3"))
        self.assertEqual(Name.findNext(names, Name.fromStr("2")), Name.fromStr("2c"))

        names = [Name.fromStr(n) for n in ["1", "2", "2a", "2b", "3"]]
        self.assertEqual(Name.findNext(names, Name.fromStr("")), Name.fromStr("4"))
        self.assertEqual(Name.findNext(names, Name.fromStr("2")), Name.fromStr("2c"))

        names = [Name.fromStr(n) for n in ["1", "2", "2a1", "2a2"]]
        self.assertEqual(Name.findNext(names, Name.fromStr("2")), Name.fromStr("2b"))
        self.assertEqual(Name.findNext(names, Name.fromStr("2a")), Name.fromStr("2a3"))

        names = [Name.fromStr(n) for n in ["1", "2", "2a1", "2a2", "2b"]]
        self.assertEqual(Name.findNext(names, Name.fromStr("2")), Name.fromStr("2c"))
        self.assertEqual(Name.findNext(names, Name.fromStr("2a")), Name.fromStr("2a3"))

        names = [Name.fromStr(n) for n in ["1", "2", "2a", "2b", "3", "3a"]]
        self.assertEqual(Name.findNext(names, Name.fromStr("")), Name.fromStr("4"))
        self.assertEqual(Name.findNext(names, Name.fromStr("2")), Name.fromStr("2c"))
        self.assertEqual(Name.findNext(names, Name.fromStr("3")), Name.fromStr("3b"))

        names = [Name.fromStr(n) for n in ["1", "2", "2a", "2", "3", "3a", "3b"]]
        self.assertEqual(Name.findNext(names, Name.fromStr("")), Name.fromStr("4"))
        self.assertEqual(Name.findNext(names, Name.fromStr("2")), Name.fromStr("2b"))
        self.assertEqual(Name.findNext(names, Name.fromStr("3")), Name.fromStr("3c"))

        names = [Name.fromStr(n) for n in ["1", "2", "2a", "2b", "3", "3a", "3b"]]
        self.assertEqual(Name.findNext(names, Name.fromStr("")), Name.fromStr("4"))
        self.assertEqual(Name.findNext(names, Name.fromStr("2")), Name.fromStr("2c"))
        self.assertEqual(Name.findNext(names, Name.fromStr("3")), Name.fromStr("3c"))

    def test_sort(self):
        def getSorted(arr: List[str]) -> List[str]:
            tmp = [Name.fromStr(n) for n in arr]
            tmp.sort()
            return [str(n) for n in tmp]

        self.assertEqual(getSorted(["b", "c", "a"]), ["a", "b", "c"])
        self.assertEqual(getSorted(["2", "3", "1"]), ["1", "2", "3"])
        self.assertEqual(getSorted(["1b", "1c", "1a"]), ["1a", "1b", "1c"])
        self.assertEqual(getSorted(["1b", "2", "1a"]), ["1a", "1b", "2"])
        self.assertEqual(getSorted(["1b", "2b", "1a", "2a"]), ["1a", "1b", "2a", "2b"])
        self.assertEqual(getSorted(["2a", "1a", "2b", "1b"]), ["1a", "1b", "2a", "2b"])
        self.assertEqual(getSorted(["2", "10", "1"]), ["1", "2", "10"])
        self.assertEqual(getSorted(["b", "aa", "a"]), ["a", "b", "aa"])
