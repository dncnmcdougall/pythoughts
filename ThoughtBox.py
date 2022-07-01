import sqlite3
import os

from typing import List, Dict

from .Name import Name
from .Link import Link
from .Tag import Tag
from .Thought import Thought


def sql_escape(s: str):
    return s.replace("'", "''")


class ThoughtBox:
    def __init__(self, database_path: str, explicitly_create_tables: bool = False):
        create_tables = False
        if not os.path.exists(database_path) or explicitly_create_tables:
            create_tables = True
        self.conn = sqlite3.connect(database_path)

        if create_tables:
            cur = self.conn.cursor()
            cur.execute("CREATE TABLE thoughts (number TEXT PRIMARY KEY, title TEXT)")
            cur.execute(
                "CREATE TABLE tags (number INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE)"
            )
            cur.execute("CREATE TABLE links (source TEXT, target TEXT)")
            cur.execute("CREATE TABLE tag_links (thought TEXT, tag INTEGER)")
            self.conn.commit()

    def listTags(self) -> List[Tag]:
        """Returns a list of all the tags in the database."""
        cur = self.conn.cursor()
        tags = []
        for row in cur.execute(
            "SELECT group_concat(DISTINCT tags.title) as title FROM tags"
        ):
            tags.extend(
                [Tag.fromStr(t.strip()) for t in row[0].split(",") if t.strip()]
            )
        return tags

    def listThoughts(
        self,
        names: List[Name] = [],
        tags: List[Tag] = [],
        linked_to: List[str] = [],
        print_query=False,
    ) -> List[Thought]:
        """
        Lists the specified thoughts.
        Listed thougts have names in names, tags in tags AND link to the specified thoughts.
        If any of these lists is empty, it is taken to mean all thoughts, tags or links, respectively.

        """

        inner_tables = ["thoughts"]
        queries = []
        if len(tags) > 0:
            tagQuery = " OR ".join(
                [f"tags.title='{sql_escape(str(t.title))}'" for t in tags]
            )
            tagQuery = f"tag_links.thought=thoughts.number AND tag_links.tag=tags.number AND ({tagQuery})"

            inner_tables.append("tags")
            inner_tables.append("tag_links")
            queries.append(tagQuery)

        if len(linked_to) > 0:
            linkQuery = " OR ".join(
                [f"links.target={sql_escape(str(l))}" for l in linked_to]
            )
            linkQuery = f"links.source=thoughts.number AND ({linkQuery})"

            inner_tables.append("links")
            queries.append(linkQuery)

        if len(names) > 0:
            namesQuery = " OR ".join([f"thoughts.number='{str(n)}'" for n in names])
            queries.append(f"({namesQuery})")

        if len(queries) > 0:
            where_str = f"WHERE {' AND '.join(queries)} GROUP BY thoughts.number"
        else:
            where_str = ""

        query = (
            f"SELECT tbl.number, tbl.title, group_concat(DISTINCT tags.title), group_concat(DISTINCT links.target) "
            "FROM "
            f" (SELECT thoughts.number as number, thoughts.title as title FROM {', '.join(inner_tables)} {where_str}) as tbl "
            "LEFT OUTER JOIN links ON links.source=tbl.number "
            "LEFT OUTER JOIN tags, tag_links ON tag_links.thought=tbl.number AND tag_links.tag=tags.number "
            "GROUP BY tbl.number "
        )

        if print_query:
            print(query, flush=True)

        cur = self.conn.cursor()
        thoughts: List[Thought] = []

        for row in cur.execute(query):
            if print_query:
                print(row)
            number = Name.fromStr(row[0])
            title = Name.fromStr(row[1])
            tag_bits = [Tag.fromStr(t.strip()) for t in row[2].split(",") if t.strip()]
            link_bits = [
                Link(source=number, target=l.strip())
                for l in row[3].split(",")
                if l.strip()
            ]
            thoughts.append(
                Thought(
                    name=row[0],
                    title=row[1],
                    tags=tag_bits,
                    links=link_bits,
                    content=[],
                    sources=[],
                )
            )

        return sorted(thoughts)

    def listThoughtsByTag(
        self,
        names: List[Name] = [],
        tags: List[Tag] = [],
        linked_to: List[str] = [],
        print_query=False,
    ) -> Dict[Tag, List[Thought]]:
        """
        Lists the specified thoughts, grouped by tag.
        Listed thougts have names in names, tags in tags AND link to the specified thoughts.
        If any of these lists is empty, it is taken to mean all thoughts, tags or links, respectively.

        """

        thoughts = self.listThoughts(
            names=names, tags=tags, linked_to=linked_to, print_query=print_query
        )

        by_tags: Dict[Tag, List[Thought]] = {}
        for thought in thoughts:
            for tag in thought.tags:
                if tag not in by_tags:
                    by_tags[tag] = []
                by_tags[tag].append(thought)
        return by_tags

    def addOrUpdate(self, thought: Thought):
        """Adds a new thought to the database or overrides a previous one."""
        str_name = str(thought.name)

        cur = self.conn.cursor()
        cur.execute("DELETE FROM thoughts WHERE number IS '" + str_name + "'")
        cur.execute("DELETE FROM links WHERE source IS '" + str_name + "'")
        cur.execute("DELETE FROM tag_links WHERE thought IS '" + str_name + "'")
        # delete all unused tags
        cur.execute(
            "WITH tbl as "
            "(SELECT tags.number as number, tag_links.tag as tag_col FROM tags "
            "LEFT OUTER JOIN tag_links ON tags.number = tag_links.tag "
            "GROUP BY tags.number) "
            "DELETE FROM tags WHERE tags.number IN (SELECT tbl.number FROM tbl where tag_col IS NULL )"
        )
        self.conn.commit()

        cur = self.conn.cursor()
        cur.execute(
            f"INSERT INTO thoughts (number, title) VALUES ('{str_name}', '{sql_escape(thought.title)}')"
        )

        if len(thought.links) > 0:
            linkValues = ", ".join(
                [
                    f"('{sql_escape(str(l.source))}', '{sql_escape(str(l.target))}')"
                    for l in thought.links
                ]
            )
            cur.execute("INSERT INTO links (source, target) VALUES " + linkValues)

        if len(thought.tags) > 0:
            tagValues = ", ".join(
                [f"('{sql_escape(str(t.title))}')" for t in thought.tags]
            )
            cur.execute(
                f"INSERT INTO tags (title) VALUES {tagValues} ON CONFLICT DO NOTHING"
            )
            self.conn.commit()

            cur = self.conn.cursor()
            tagQuery = " OR ".join(
                [f"(title='{sql_escape(str(t.title))}')" for t in thought.tags]
            )
            rows = cur.execute(f"SELECT number FROM tags WHERE {tagQuery}").fetchall()

            if len(rows) > 0:
                tagValues = ", ".join([f"('{str_name}', {row[0]})" for row in rows])
                cur.execute(f"INSERT INTO tag_links (thought, tag) VALUES {tagValues}")
        self.conn.commit()

    def delete(self, name: Name):
        """
        Deletes the named thought.
        Additionally this deletes any tags that are only used by this thought.
        This also deletes all links from this thought to others.
        However it does not delete any links into this thought from others, they remain even though broken.
        """
        str_name = str(name)

        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM thoughts WHERE number IS '{str_name}'")
        cur.execute(f"DELETE FROM links WHERE source IS '{str_name}'")
        cur.execute(f"DELETE FROM tag_links WHERE thought IS '{str_name}'")
        # delete all unused tags
        cur.execute(
            "WITH tbl as "
            "(SELECT tags.number as number, tag_links.tag as tag_col FROM tags "
            "LEFT OUTER JOIN tag_links ON tags.number = tag_links.tag "
            "GROUP BY tags.number) "
            "DELETE FROM tags WHERE tags.number IN (SELECT tbl.number FROM tbl where tag_col IS NULL )"
        )

        self.conn.commit()

    def rename(self, name: Name, new_name: Name) -> List[Name]:
        """Changes the name of a thought.
        This updates the links out of the thought (the link src is updated).
        Links into the thought are kept as is. This results in broken links (the links to points to the old files).
        (Links need to be updated by updating each thought that links to this thought.)
        The thought should have the same title and tags.

        Returns a list of all the thoughts that pointed to this thought. These all need to be updated.
        """

        str_name = str(name)
        str_new_name = str(new_name)

        cur = self.conn.cursor()
        cur.execute(
            f"UPDATE thoughts SET number='{str_new_name}' WHERE number='{str_name}'"
        )
        cur.execute(
            f"UPDATE tag_links SET thought='{str_new_name}' WHERE thought='{str_name}'"
        )
        cur.execute(
            f"UPDATE links SET source='{str_new_name}' WHERE source='{str_name}'"
        )
        self.conn.commit()

        return [t.name for t in self.listThoughts(linked_to=[str_name])]
