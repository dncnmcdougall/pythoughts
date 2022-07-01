import unittest
import tempfile

from typing import List, Dict

from ..ThoughtBox import ThoughtBox
from ..Thought import Thought
from ..Name import Name
from ..Tag import Tag
from ..Link import Link


class ThoughtBoxTests(unittest.TestCase):
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

        self.db_file = tempfile.NamedTemporaryFile()
        self.tb = ThoughtBox(self.db_file.name, explicitly_create_tables=True)

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

    def tearDown(self):
        self.db_file.close()

    def test_listTags(self):
        tags = self.tb.listTags()
        tag_strs = [t.title for t in tags]

        self.assertIn("first", tag_strs)
        self.assertIn("second", tag_strs)
        self.assertIn("cat", tag_strs)
        self.assertIn("dog", tag_strs)
        self.assertIn("mouse", tag_strs)

        self.assertNotIn("house", tag_strs)

    def test_listThoughts(self):
        thoughts = self.tb.listThoughts()
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(
            thought_strs,
            [("1", "first"), ("2", "second"), ("3", "third"), ("4", "forth")],
        )

    def test_listThoughts_with_name(self):
        thoughts = self.tb.listThoughts(names=[Name.fromStr(n) for n in ["1", "3"]])
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(thought_strs, [("1", "first"), ("3", "third")])

    def test_listThoughts_with_tags(self):
        thoughts = self.tb.listThoughts(tags=[Tag.fromStr(t) for t in ["cat", "mouse"]])
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(thought_strs, [("1", "first"), ("3", "third"), ("4", "forth")])

    def test_listThoughts_with_links(self):
        thoughts = self.tb.listThoughts(linked_to=[Name.fromStr(n) for n in ["1"]])
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(thought_strs, [("4", "forth")])

        thoughts = self.tb.listThoughts(linked_to=[Name.fromStr(n) for n in ["4"]])
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(thought_strs, [("2", "second"), ("3", "third")])

        thoughts = self.tb.listThoughts(linked_to=[Name.fromStr(n) for n in ["1", "4"]])
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(
            thought_strs, [("2", "second"), ("3", "third"), ("4", "forth")]
        )

    def test_listThoughtsByTags(self):
        d = self.tb.listThoughtsByTag()
        d_comp = {tag.title: [(str(t.name), t.title) for t in d[tag]] for tag in d}

        self.assertEqual(d_comp["first"], [("1", "first")])

        self.assertEqual(d_comp["second"], [("2", "second")])

        self.assertEqual(d_comp["cat"], [("1", "first"), ("4", "forth")])

        self.assertEqual(d_comp["dog"], [("2", "second"), ("3", "third")])

        self.assertEqual(d_comp["mouse"], [("3", "third"), ("4", "forth")])

    def test_listThoughtsByTags_with_name(self):
        d = self.tb.listThoughtsByTag(names=[Name.fromStr(n) for n in ["1", "3"]])
        d_comp = {tag.title: [(str(t.name), t.title) for t in d[tag]] for tag in d}

        self.assertEqual(d_comp["first"], [("1", "first")])

        self.assertEqual(d_comp["cat"], [("1", "first")])

        self.assertEqual(d_comp["dog"], [("3", "third")])

        self.assertEqual(d_comp["mouse"], [("3", "third")])

    def test_listThoughtsByTags_with_tags(self):
        d = self.tb.listThoughtsByTag(tags=[Tag.fromStr(t) for t in ["cat", "mouse"]])
        d_comp = {tag.title: [(str(t.name), t.title) for t in d[tag]] for tag in d}

        self.assertEqual(d_comp["cat"], [("1", "first"), ("4", "forth")])

        self.assertEqual(d_comp["mouse"], [("3", "third"), ("4", "forth")])

    def test_listThoughtsByTags_with_links(self):
        d = self.tb.listThoughtsByTag(linked_to=[Name.fromStr(n) for n in ["1"]])
        d_comp = {tag.title: [(str(t.name), t.title) for t in d[tag]] for tag in d}

        self.assertEqual(d_comp["cat"], [("4", "forth")])

        self.assertEqual(d_comp["mouse"], [("4", "forth")])

        d = self.tb.listThoughtsByTag(linked_to=[Name.fromStr(n) for n in ["2", "4"]])
        d_comp = {tag.title: [(str(t.name), t.title) for t in d[tag]] for tag in d}

        self.assertEqual(d_comp["second"], [("2", "second")])

        self.assertEqual(d_comp["cat"], [("1", "first")])

        self.assertEqual(d_comp["dog"], [("2", "second"), ("3", "third")])

        self.assertEqual(d_comp["mouse"], [("3", "third")])

    def test_addOrUpdate_update(self):
        thoughts = self.tb.listThoughts()
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(
            thought_strs,
            [("1", "first"), ("2", "second"), ("3", "third"), ("4", "forth")],
        )

        new_third = self._addThought(
            name="3", title="new title", tags=["dog", "mouse", "new_tag"], links=["2"]
        )

        thoughts = self.tb.listThoughts(names=[Name.fromStr("3")])
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(thought_strs, [("3", "new title")])

        tags = self.tb.listTags()
        tag_strs = [t.title for t in tags]

        self.assertIn("new_tag", tag_strs)

        thoughts = self.tb.listThoughts(linked_to=[Name.fromStr("2")])
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(thought_strs, [("1", "first"), ("3", "new title")])

    def test_delete(self):
        thoughts = self.tb.listThoughts()
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(
            thought_strs,
            [("1", "first"), ("2", "second"), ("3", "third"), ("4", "forth")],
        )

        # Delete thought 2
        self.tb.delete(Name.fromStr("2"))

        thoughts = self.tb.listThoughts()
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        # The thought is deleted
        self.assertEqual(thought_strs, [("1", "first"), ("3", "third"), ("4", "forth")])

        # Links out are deleted
        thoughts = self.tb.listThoughts(linked_to=[Name.fromStr(n) for n in ["4"]])
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(thought_strs, [("3", "third")])

        # Does not delete links in
        thoughts = self.tb.listThoughts(names=[Name.fromStr("1")])
        links = [str(l.target) for l in thoughts[0].links]
        self.assertIn("2", links)
        self.assertIn("3", links)

        # Unused tags are deleted
        tags = self.tb.listTags()
        tag_strs = [t.title for t in tags]

        self.assertIn("first", tag_strs)
        self.assertNotIn("second", tag_strs)
        self.assertIn("cat", tag_strs)
        self.assertIn("dog", tag_strs)
        self.assertIn("mouse", tag_strs)

    def test_rename(self):
        thoughts = self.tb.listThoughts()
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(
            thought_strs,
            [("1", "first"), ("2", "second"), ("3", "third"), ("4", "forth")],
        )

        # Rename thought 2 to 5
        needs_updating = self.tb.rename(Name.fromStr("2"), Name.fromStr("5"))

        # list all the thoughts that linked to this thought.
        self.assertEqual(needs_updating, ["1"])
        thoughts = self.tb.listThoughts(linked_to=[Name.fromStr(n) for n in ["2"]])
        thought_strs = [(str(t.name), t.title) for t in thoughts]
        self.assertEqual(thought_strs, [("1", "first")])

        thoughts = self.tb.listThoughts()
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        # The thought is renamed
        self.assertEqual(
            thought_strs,
            [("1", "first"), ("3", "third"), ("4", "forth"), ("5", "second")],
        )

        thoughts = self.tb.listThoughts(linked_to=[Name.fromStr(n) for n in ["4"]])
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        # Links out are preserved
        self.assertEqual(thought_strs, [("3", "third"), ("5", "second")])

        # Links in are manintaned
        thoughts = self.tb.listThoughts(names=[Name.fromStr("1")])
        links = [str(l.target) for l in thoughts[0].links]
        self.assertIn("3", links)
        self.assertIn("2", links)

        # Unused tags are deleted
        tags = self.tb.listTags()
        tag_strs = [t.title for t in tags]

        self.assertIn("first", tag_strs)
        self.assertIn("second", tag_strs)
        self.assertIn("cat", tag_strs)
        self.assertIn("dog", tag_strs)
        self.assertIn("mouse", tag_strs)


class ThoughtBox_PersistenceTests(unittest.TestCase):
    def _addThought(
        self, tb, name: str, title: str, tags: List[str], links: List[str]
    ) -> Thought:

        t = Thought(
            name=Name.fromStr(name),
            title=title,
            tags=[Tag.fromStr(t) for t in tags],
            links=[Link.fromStr(name, l) for l in links],
            content=[],
            sources=[],
        )
        tb.addOrUpdate(t)
        return t

    def setUp(self):
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

        self.db_file = tempfile.NamedTemporaryFile()
        tb = ThoughtBox(self.db_file.name, explicitly_create_tables=True)

        self.first = self._addThought(
            tb, name="1", title="first", tags=["first", "cat"], links=["2", "3"]
        )

        self.second = self._addThought(
            tb, name="2", title="second", tags=["second", "dog"], links=["4"]
        )

        self.third = self._addThought(
            tb, name="3", title="third", tags=["dog", "mouse"], links=["4"]
        )

        self.forth = self._addThought(
            tb, name="4", title="forth", tags=["cat", "mouse"], links=["1", "3"]
        )

    def tearDown(self):
        self.db_file.close()

    def test_listThoughts(self):
        tb = ThoughtBox(self.db_file.name)
        thoughts = tb.listThoughts()
        thought_strs = [(str(t.name), t.title) for t in thoughts]

        self.assertEqual(
            thought_strs,
            [("1", "first"), ("2", "second"), ("3", "third"), ("4", "forth")],
        )
