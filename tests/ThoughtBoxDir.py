import unittest
import tempfile
import os

from typing import List, Dict

from ..ThoughtBoxDir import ThoughtBoxDir
from ..ThoughtBox import ThoughtBox
from ..Thought import Thought
from ..Name import Name
from ..Tag import Tag
from ..Link import Link


class ThoughtBoxDirTests(unittest.TestCase):
    def equalDict(self, thought: Thought, dict: Dict[str, List[str]]):
        self.assertEqual(str(thought.title), dict["title"])
        self.assertEqual([t.title for t in thought.tags], dict["tags"])
        self.assertEqual([str(l.target) for l in thought.links], dict["links"])

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.dir_name = self.dir.name
        self.tbd = ThoughtBoxDir(self.dir_name)

    def tearDown(self):
        self.dir.cleanup()

    def test_getName_getPath(self):
        name = Name.fromStr("1a")
        self.assertTrue(name == self.tbd.getName(self.tbd.getPath(name)))

        path = os.path.join(self.dir_name, "1b.tb")
        self.assertEqual(path, str(self.tbd.getPath(self.tbd.getName(path))))
        self.assertEqual(Name.fromStr("1b"), self.tbd.getName(path))

    def test_createNew(self):
        name_1 = Name.fromStr("1")
        name_1n = name_1.next()
        name_a = Name.fromStr("a")
        name_an = name_a.next()

        self.assertEqual(len(os.listdir(self.dir_name)), 0)

        self.assertEqual(name_1, self.tbd.createNew(name_1))
        self.assertEqual(name_a, self.tbd.createNew(name_a))

        dir_list = os.listdir(self.dir_name)
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1), start=self.dir_name),
            os.listdir(self.dir_name),
        )
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_a), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_1n), start=self.dir_name),
            os.listdir(self.dir_name),
        )
        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_an), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        self.assertEqual(name_1n, self.tbd.createNew(name_1))
        self.assertEqual(name_an, self.tbd.createNew(name_a))

        dir_list = os.listdir(self.dir_name)
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1n), start=self.dir_name),
            os.listdir(self.dir_name),
        )
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_an), start=self.dir_name),
            os.listdir(self.dir_name),
        )

    def test_createNew_override(self):
        name_1 = Name.fromStr("1")
        name_1n = name_1.next()

        self.assertEqual(len(os.listdir(self.dir_name)), 0)

        path = self.tbd.getPath(self.tbd.createNew(name_1))

        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_1n), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        with open(path, "w") as tf:
            tf.write("# hello\n")
            tf.write("hello\n")
            tf.write("# references\n")
            tf.write("# tags\n")

        dir_list = os.listdir(self.dir_name)
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1), start=self.dir_name),
            os.listdir(self.dir_name),
        )
        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_1n), start=self.dir_name),
            os.listdir(self.dir_name),
        )
        with open(path, "r") as tf:
            self.assertTrue(tf.readline() == "# hello\n")

        self.assertEqual(name_1, self.tbd.createNew(name_1, force_override=True))
        path = self.tbd.getPath(name_1)

        dir_list = os.listdir(self.dir_name)
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1), start=self.dir_name),
            os.listdir(self.dir_name),
        )
        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_1n), start=self.dir_name),
            os.listdir(self.dir_name),
        )
        with open(path, "r") as tf:
            self.assertFalse(tf.readline() == "# hello\n")

    def test_read(self):
        name_1 = Name.fromStr("1")
        path = self.tbd.getPath(self.tbd.createNew(name_1))

        content = ["hello", "some text with #inline_tag", "some text with [[1a1]]"]

        with open(path, "w") as tf:
            tf.write("# hello\n")
            for l in content:
                tf.write(f"{l}\n")
            tf.write("# sources\n")
            tf.write("sources 1\n")
            tf.write("# tags\n")
            tf.write("tag1, tag 2\n")

        thought = self.tbd.read(name_1)
        self.equalDict(
            thought,
            {
                "title": "hello",
                "content": content,
                "tags": [
                    "inline_tag",
                    "tag1",
                    "tag 2",
                ],
                "sources": ["sources 1"],
                "links": ["1a1"],
            },
        )

    def test_writeDotGraph(self):
        self.skipTest("Not yet implimented")

    def test_rename(self):
        name_1 = Name.fromStr("1")
        name_a = Name.fromStr("a")

        self.assertEqual(len(os.listdir(self.dir_name)), 0)

        self.assertEqual(name_1, self.tbd.createNew(name_1))

        dir_list = os.listdir(self.dir_name)
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1), start=self.dir_name),
            os.listdir(self.dir_name),
        )
        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_a), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        self.tbd.rename(name_1, name_a)

        dir_list = os.listdir(self.dir_name)
        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_1), start=self.dir_name),
            os.listdir(self.dir_name),
        )
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_a), start=self.dir_name),
            os.listdir(self.dir_name),
        )

    def test_rename_raise(self):
        name_1 = Name.fromStr("1")
        name_a = Name.fromStr("a")

        with self.assertRaises(FileNotFoundError) as check:
            self.tbd.rename(name_1, name_a)

        self.assertEqual(name_1, self.tbd.createNew(name_1))
        self.assertEqual(name_a, self.tbd.createNew(name_a))

        with self.assertRaises(FileExistsError) as check:
            self.tbd.rename(name_1, name_a)

    def test_delete(self):
        name_1 = Name.fromStr("1")
        name_a = Name.fromStr("a")

        self.assertEqual(len(os.listdir(self.dir_name)), 0)

        self.assertEqual(name_1, self.tbd.createNew(name_1))
        self.assertEqual(name_a, self.tbd.createNew(name_a))

        dir_list = os.listdir(self.dir_name)
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1), start=self.dir_name),
            os.listdir(self.dir_name),
        )
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_a), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        self.tbd.delete(name_1)

        dir_list = os.listdir(self.dir_name)
        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_1), start=self.dir_name),
            os.listdir(self.dir_name),
        )
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_a), start=self.dir_name),
            os.listdir(self.dir_name),
        )

    def test_delete_raise(self):
        name_1 = Name.fromStr("1")

        with self.assertRaises(FileNotFoundError) as check:
            self.tbd.delete(name_1)

        self.assertEqual(name_1, self.tbd.createNew(name_1))

        self.tbd.delete(name_1)
