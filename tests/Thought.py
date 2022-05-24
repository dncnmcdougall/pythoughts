import unittest

from typing import List, Dict

from ..Thought import Thought


class ThoughtTests(unittest.TestCase):
    def equalDict(self, thought: Thought, dict: Dict[str, List[str]]):
        self.assertEqual(str(thought.title), dict["title"])
        self.assertEqual([t.title for t in thought.tags], dict["tags"])
        self.assertEqual([str(l.dest) for l in thought.links], dict["links"])

    def test_parse(self):
        """ This method takes in the lines of a file and returns a thought.
        The format of the content is irrelevant, with a few small boundaries:

        The first heading is the title of the thought.

        Inline links are specified with /[[\(.\{-}\)]]/ which links to /\1/.
        Inline tags are /#\(.\{-}\)\s/ with the tag being /\1/.

        There is also the special heading # tags. The content of this section is split on ","
        and each non-empty group is treated as a tag. This allows tags with spaces.

        Three is also the special heading #sources. The content of this is also
        parsed for tags and links, but is not included in content.

        Other toplevel headings are ignored. The content of those sections is
        not parsed for tags and links, and the content is not stored. """

        heading_content = ["# heading", "content 1", "content 2", ""]

        inline_tags = ["The #cat jumped", "#dog jumped too", "as did the #kangaroo", ""]

        inline_links = [
            "The cat [[1]] jumped",
            "[[2]] dog jumped too",
            "as did the kangaroo [[3]]",
            "",
        ]

        tags_content = ["# tags", "tag1, tag1b", "tag 2, tag 2b,", "tag 3, tag 3b", ""]

        sources_content = ["# sources", "sources 1", "sources 2", ""]

        content = []
        content.extend(heading_content)
        content.extend(inline_tags)
        content.extend(inline_links)
        content.extend(tags_content)
        content.extend(sources_content)

        expected_content = []
        expected_content.extend(heading_content[1:])
        expected_content.extend(inline_tags)
        expected_content.extend(inline_links)
        result = Thought.parse(content, "test")
        self.equalDict(
            result,
            {
                "title": "heading",
                "content": expected_content,
                "tags": [
                    "cat",
                    "dog",
                    "kangaroo",
                    "tag1",
                    "tag1b",
                    "tag 2",
                    "tag 2b",
                    "tag 3",
                    "tag 3b",
                ],
                "sources": ["sources 1", "sources 2", ""],
                "links": ["1", "2", "3"],
            },
        )

    def test_parse_heading(self):
        """ The first heading in the file is used as the title.
        A heading line is: /#\s\(.*\)$/
        And the heading is: /\1/

        Note that this means that you can have a thought entitles "tags".
        It will then have two "tags" headings in it.
        """
            
        heading_content = ["# heading", "content 1", "content 2", ""]

        heading_content_2 = ["# heading 2", "content 1", "content 2", ""]

        heading_content_3 = ["# tags", "content 1", "content 2", ""]

        result = Thought.parse([], "test")
        self.equalDict(
            result,
            {"title": '', "content": [], "tags": [], "sources": [], "links": []},
        )

        result = Thought.parse([heading_content[0]], "test")
        self.equalDict(
            result,
            {"title": "heading", "content": [], "tags": [], "sources": [], "links": []},
        )

        result = Thought.parse(heading_content, "test")
        self.equalDict(
            result,
            {
                "title": "heading",
                "content": ["content 1", "content 2", ""],
                "tags": [],
                "sources": [],
                "links": [],
            },
        )

        result = Thought.parse(heading_content_2, "test")
        self.equalDict(
            result,
            {
                "title": "heading 2",
                "content": ["content 1", "content 2", ""],
                "tags": [],
                "sources": [],
                "links": [],
            },
        )

        result = Thought.parse(heading_content_3, "test")
        self.equalDict(
            result,
            {
                "title": "tags",
                "content": ["content 1", "content 2", ""],
                "tags": [],
                "sources": [],
                "links": [],
            },
        )

    def test_parse_tags(self):
        """ There are two ways to specify tags.
        Eaither inline on in the tags section of the file.

        Inline links are specified with /[[\(.\{-}\)]]/ which links to /\1/.

        The tags section of the file starts tith the "tags" heading. Every line
        in that section is split on ",". Every non-empty item in the resulting
        lists is considered a tag. Thus there can be tags with spaces. 
        """

        heading_content = ["# heading", "content 1", "content 2", ""]

        inline_tags = ["The #cat jumped", "#dog jumped too", "as did the #kangaroo", ""]

        tags_content = ["# tags", "tag1, tag1b", "tag 2, tag 2b,", "tag 3, tag 3b", ""]

        result = Thought.parse(tags_content, "test")
        self.equalDict(
            result,
            {
                "title": "tags",
                "content": ["tag1, tag1b", "tag 2, tag 2b,", "tag 3, tag 3b", ""],
                "tags": [],
                "sources": [],
                "links": [],
            },
        )

        content = []
        content.extend([heading_content[0]])
        content.extend(tags_content)
        result = Thought.parse(content, "test")
        self.equalDict(
            result,
            {
                "title": "heading",
                "content": [],
                "tags": ["tag1", "tag1b", "tag 2", "tag 2b", "tag 3", "tag 3b"],
                "sources": [],
                "links": [],
            },
        )

        content = []
        content.extend([heading_content[0]])
        content.extend(inline_tags)
        result = Thought.parse(content, "test")
        self.equalDict(
            result,
            {
                "title": "heading",
                "content": [
                    "The #cat jumped",
                    "#dog jumped too",
                    "as did the #kangaroo",
                    "",
                ],
                "tags": ["cat", "dog", "kangaroo"],
                "sources": [],
                "links": [],
            },
        )

        content = []
        content.extend([heading_content[0]])
        content.extend(inline_tags)
        content.extend(tags_content)
        result = Thought.parse(content, "test")
        self.equalDict(
            result,
            {
                "title": "heading",
                "content": [
                    "The #cat jumped",
                    "#dog jumped too",
                    "as did the #kangaroo",
                    "",
                ],
                "tags": [
                    "cat",
                    "dog",
                    "kangaroo",
                    "tag1",
                    "tag1b",
                    "tag 2",
                    "tag 2b",
                    "tag 3",
                    "tag 3b",
                ],
                "sources": [],
                "links": [],
            },
        )

    def test_parse_links(self):
        """ 
        Links are specified inline with /[[\(.\{-}\)]]/ which links to /\1/.
        """

        heading_content = ["# heading", "content 1", "content 2", ""]

        inline_links = [
            "The cat [[1]] jumped",
            "[[2]] dog jumped too",
            "as did the kangaroo [[3]]",
            "all [[4]] jumping together [[5]]",
            "",
        ]

        content = []
        content.extend([heading_content[0]])
        content.extend(inline_links)
        result = Thought.parse(content, "test")
        self.equalDict(
            result,
            {
                "title": "heading",
                "content": [
                    "The cat [[1]] jumped",
                    "[[2]] dog jumped too",
                    "as did the kangaroo [[3]]",
                    "all [[4]] jumping together [[5]]",
                    "",
                ],
                "tags": [],
                "sources": [],
                "links": ["1", "2", "3", "4", "5"],
            },
        )

    def test_parse_sources(self):
        """ Sources is a special section that is parsed and included.
        It is not very special in that it is treated the same as the main contnet.
        It is special in that it is not ignored.
        """

        heading_content = ["# heading", "content 1", "content 2", ""]

        sources_content = ["# sources", "sources 1", "sources 2", ""]

        sources_content_tags = ["# sources", "#first source", "sources #second", ""]

        sources_content_links = ["# sources", "sources [[1]]", "sources [[cats]]]", ""]

        result = Thought.parse(sources_content, "test")
        self.equalDict(
            result,
            {
                "title": "sources",
                "content": ["sources 1", "sources 2", ""],
                "tags": [],
                "sources": [],
                "links": [],
            },
        )

        content = []
        content.extend([heading_content[0]])
        content.extend(sources_content)
        result = Thought.parse(content, "test")
        self.equalDict(
            result,
            {
                "title": "heading",
                "content": [],
                "tags": [],
                "sources": ["sources 1", "sources 2", ""],
                "links": [],
            },
        )

        content = []
        content.extend([heading_content[0]])
        content.extend(sources_content_tags)
        result = Thought.parse(content, "test")
        self.equalDict(
            result,
            {
                "title": "heading",
                "content": [],
                "tags": ["first", "second"],
                "sources": ["#first source", "sources #second", ""],
                "links": [],
            },
        )

        content = []
        content.extend([heading_content[0]])
        content.extend(sources_content_links)
        result = Thought.parse(content, "test")
        self.equalDict(
            result,
            {
                "title": "heading",
                "content": [],
                "tags": [],
                "sources": ["sources [[1]]", "sources [[cats]]", ""],
                "links": ["1", "cats"],
            },
        )

    def test_parse_other_headings(self):
        """ Apart from the first heading, tags and sources, all other headings and their content are ignored.
        It is not very special in that it is treated the same as the main contnet.
        It is special in that it is not ignored.
        """

        heading_content = ["# heading", "content #1", "content [[2]]", ""]

        sources_content = ["# sources", "sources #2", "sources [[cats]]]", ""]

        other_content = ["# other", "other #3", "other [[dogs]]", ""]

        content = []
        content.extend(heading_content)
        content.extend(sources_content)
        content.extend(other_content)
        result = Thought.parse(content, "test")
        self.equalDict(
            result,
            {
                "title": "heading",
                "content": ["content #1", "content [[2]]"],
                "tags": ["1","2"],
                "sources": ["sources #2", "sources [[cats]]", ""],
                "links": ["2","cats"],
            },
        )

