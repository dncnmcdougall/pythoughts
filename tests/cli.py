import unittest
import tempfile
import os

from typing import List, Dict

from ..cli import parse
from ..Name import Name
from ..Tag import Tag
from ..Link import Link
from ..ThoughtBoxDir import ThoughtBoxDir
from ..ThoughtBox import ThoughtBox
from ..Thought import Thought

class CliTests(unittest.TestCase):
    def _addThought(
        self, name: str, title: str, tags: List[str], links: List[str]
    ) -> Thought:

        t = Thought(
            name=Name.fromStr(name),
            title=title,
            tags=[Tag.fromStr(t) for t in tags],
            links=[Link.fromStr(name, l) for l in links],
            content=[],
            sources=[],
        )
        self.tb.addOrUpdate(t)
        return t

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.dir_name = self.dir.name
        self.tbd = ThoughtBoxDir(self.dir_name)

        self.db_file = tempfile.NamedTemporaryFile()
        self.tb = ThoughtBox(self.db_file.name, explicitly_create_tables=True)

    def tearDown(self):
        self.dir.cleanup()
        self.db_file.close()

    def test_create(self):
        name_1 = Name.fromStr("1")
        name_1n = name_1.next()

        self.assertEqual(len(os.listdir(self.dir_name)), 0)

        args = ['create',str(name_1),'--box',self.dir_name]
        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, ['INFO:root:Created: '+str(name_1)])

        dir_list = os.listdir(self.dir_name)
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_1n), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, ['INFO:root:Created: '+str(name_1n)])

        dir_list = os.listdir(self.dir_name)
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1n), start=self.dir_name),
            os.listdir(self.dir_name),
        )

    def test_create_default(self):
        name_1 = Name.fromStr("1")
        name_1n = name_1.next()

        self.assertEqual(len(os.listdir(self.dir_name)), 0)

        args = ['create','--box',self.dir_name]
        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, ['INFO:root:Created: '+str(name_1)])

        dir_list = os.listdir(self.dir_name)
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_1n), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, ['INFO:root:Created: '+str(name_1n)])

        dir_list = os.listdir(self.dir_name)
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1n), start=self.dir_name),
            os.listdir(self.dir_name),
        )


    def test_create_override(self):
        name_1 = Name.fromStr("1")
        name_1n = name_1.next()

        self.assertEqual(len(os.listdir(self.dir_name)), 0)

        args = ['create',str(name_1),'--box',self.dir_name, '--override']
        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, ['INFO:root:Created: '+str(name_1)])

        dir_list = os.listdir(self.dir_name)
        self.assertIn(
            os.path.relpath(self.tbd.getPath(name_1), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_1n), start=self.dir_name),
            os.listdir(self.dir_name),
        )

        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, ['INFO:root:Created: '+str(name_1)])

        dir_list = os.listdir(self.dir_name)
        self.assertNotIn(
            os.path.relpath(self.tbd.getPath(name_1n), start=self.dir_name),
            os.listdir(self.dir_name),
        )

    def _createFourThoughts(self):
        """
        links:
        1 -> 2 -> 4 -> 1
          -> 3 <>

        tags:
          first  -> 1
          second -> 2
          cat    -> 1,4
          dog    -> 2,3
          mouse  -> 3,4
        """
        self.first = self._addThought(
            name="1", title="first", tags=["first", "cat"], links=["2", "3"]
        )

        self.second = self._addThought(
            name="2", title="second", tags=["second", "dog"], links=["4"]
        )

        self.third = self._addThought(
            name="3", title="third", tags=["dog", "mouse"], links=["4"]
        )

        self.forth = self._addThought(
            name="4", title="forth", tags=["cat", "mouse"], links=["1", "3"]
        )

    def test_read(self):
        self._createFourThoughts()

        args = ['read','--by=name','--database',self.db_file.name]
        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, [
                         'INFO:root:1: first',
                         'INFO:root:2: second',
                         'INFO:root:3: third',
                         'INFO:root:4: forth'
                         ])

    def test_read_by_tags(self):
        self._createFourThoughts()

        args = ['read','--by=tag','--database',self.db_file.name]
        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, [
                         'INFO:root:cat: 1, 4',
                         'INFO:root:dog: 2, 3',
                         'INFO:root:first: 1',
                         'INFO:root:mouse: 3, 4',
                         'INFO:root:second: 2'
                         ])

    def test_read_by_detail(self):
        self._createFourThoughts()

        args = ['read','--by=detail','--database',self.db_file.name]
        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, [
                         'INFO:root:1: first',
                         'INFO:root:tags: cat, first',
                         'INFO:root:links: 2, 3',
                         'INFO:root:2: second',
                         'INFO:root:tags: dog, second',
                         'INFO:root:links: 4',
                         'INFO:root:3: third',
                         'INFO:root:tags: dog, mouse',
                         'INFO:root:links: 4',
                         'INFO:root:4: forth',
                         'INFO:root:tags: cat, mouse',
                         'INFO:root:links: 1, 3'
                         ])

    def test_read_with_tag(self):
        self._createFourThoughts()

        args = ['read','--by=name','--tags','cat', '--database',self.db_file.name]
        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, [
                         'INFO:root:1: first',
                         'INFO:root:4: forth'
                         ])

        args = ['read','--by=name','--tags','cat', 'mouse','--database',self.db_file.name]
        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, [
                         'INFO:root:1: first',
                         'INFO:root:3: third',
                         'INFO:root:4: forth'
                         ])

    def test_read_with_link(self):
        self._createFourThoughts()

        args = ['read','--by=name','--links','4', '--database',self.db_file.name]
        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, [
                         'INFO:root:2: second',
                         'INFO:root:3: third'
                         ])

        args = ['read','--by=name','--links','4', '1','--database',self.db_file.name]
        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, [
                         'INFO:root:2: second',
                         'INFO:root:3: third',
                         'INFO:root:4: forth'
                         ])

    def test_read_with_link_and_tag(self):
        self._createFourThoughts()

        args = ['read','--by=name','--tags', 'mouse','--links','4', '--database',self.db_file.name]
        with self.assertLogs(level='INFO') as logs:
            parse(args)
        self.assertEqual(logs.output, [
                         'INFO:root:3: third'
                         ])

