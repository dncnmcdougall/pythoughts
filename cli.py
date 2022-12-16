import argparse
import logging
import sys

from .ThoughtBoxDir import ThoughtBoxDir
from .Name import Name
from .Link import Link
from .Tag import Tag
from .Thought import Thought
from .ThoughtBox import ThoughtBox


def parse(sys_args=None):
    main_parser = argparse.ArgumentParser(
        prog="pythoughts",
        description="Tools for managing a thoughtbox database and files.",
    )
    subparsers = main_parser.add_subparsers(dest="command", required=True)

    cmds = [Create, Read, Write, Parse, Rename, Delete]
    parsers = []

    for cmd in cmds:
        parsers.append(cmd.parser(subparsers))

    parser = subparsers.add_parser("help", help="show help for the commands.")
    parser.add_argument("help", nargs="?", choices=[p.prog.split()[1] for p in parsers])

    args = main_parser.parse_args(args=sys_args)

    if args.command == "help":
        for p in parsers:
            if p.prog.split()[1] == args.help:
                p.print_help()
                sys.exit(0)
        main_parser.print_help()
        sys.exit(0)

    for cmd in cmds:
        if cmd.__name__.lower() == args.command:
            cmd(args).run()


class Create:
    """Create new thought files on disk.

    Onsuccess the file will constain the new thought and this will print out the resulting name as:
    "Created: name"

    If --override is used then this will always use the provided name, even if it already exists (overwriting the content.)
    Normally (without --override) the next avalable sub-name will be used.
    For example if thought 1,2,4 exist and:
    name is "" then 3 will be created,
    name is "1" then 1a will be created,
    name is "1" and --override, then "1" will be overwritten,
    name is "" and  --override then "1" will be overwritten.
    """

    @staticmethod
    def parser(subparsers):
        parser = subparsers.add_parser(
            "create", help=Create.__doc__, description=Create.__doc__
        )
        parser.add_argument(
            "name", 
            nargs='?', 
            action="store", 
            default="1", 
            help="The name of the thought to create."
        )
        parser.add_argument(
            "-b",
            "--box",
            "--directory",
            nargs=1,
            action="store",
            required=True,
            help="The name of the ThoughtBox directory to use.",
        )
        parser.add_argument(
            "--overwrite",
            "--override",
            action="store_true",
            help="If true this command will overwrite the named thought (if it exists). Normally the next available sub-name will be used.",
        )
        return parser

    def __init__(self, args):
        self.args = args

    def run(self):
        tbd = ThoughtBoxDir(self.args.box[0])
        arg_name = self.args.name[0].strip()
        if len(arg_name) == 0:
            arg_name = "1"
        name = Name.fromStr(arg_name)
        new_name = tbd.createNew(name, force_override=self.args.overwrite)
        logging.info(f"Created: {new_name}")


class Read:
    """Read thoughts form the database."""

    @staticmethod
    def parser(subparsers):
        parser = subparsers.add_parser(
            "read", help=Read.__doc__, description=Read.__doc__
        )
        parser.add_argument(
            "--by",
            nargs=1,
            required=True,
            action="store",
            choices=["name", "tag", "detail"],
            help=(
                "Display the toughts as: "
                " a list (--by=name),"
                " grouped by tags (--by=tag), "
                " with details (--by=detail)."
                ""
                "--by=name uses:"
                " name1: title1"
                " name2: title2"
                ""
                "--by=tag uses:"
                " tag1: name1, name2"
                " tag2: name1, name3"
                ""
                "--by=detail uses:"
                " name1: title1"
                " tags: tag1, tag2"
                " links: link1, link2"
                " name2: title2"
                " tags: tag1, tag3"
                " links: link2, link3"
            ),
        )
        parser.add_argument(
            "-t",
            "--tags",
            nargs="+",
            action="store",
            help=(
                "Display the thoughts with the given tags. If no tag is given, display"
                " all the thoughts."
            ),
        )
        parser.add_argument(
            "-n",
            "--names",
            nargs="+",
            action="store",
            help=(
                "Display thoughts with the given names. If no name is given, display"
                " all the thoughts."
            ),
        )
        parser.add_argument(
            "-l",
            "--links",
            nargs="+",
            action="store",
            help=(
                "Display the thoughts which link to the given thought. If no link is"
                " given, display all the thoughts."
            ),
        )
        parser.add_argument(
            "-d",
            "--database",
            nargs=1,
            action="store",
            required=True,
            help="The name of the database to use.",
        )
        return parser

    def __init__(self, args):
        self.args = args

    def run(self):
        tb = ThoughtBox(self.args.database[0])
        names = [Name.fromStr(n) for n in self.args.names or []]
        links = [Name.fromStr(l) for l in self.args.links or []]
        tags = [Tag.fromStr(t) for t in self.args.tags or []]
        if self.args.by[0] == "tag":
            result = tb.listThoughtsByTag(names=names, tags=tags, linked_to=links)
            res_tags = sorted(result.keys(),  key=lambda t: t.title)
            for tag in res_tags:
                names = [t.name for t in result[tag]]
                logging.info(f"{tag.title}: {', '.join(names)}")
        else:
            result = tb.listThoughts(names=names, tags=tags, linked_to=links)
            detail = self.args.by[0] == "detail"
            for thought in result:
                logging.info(f"{thought.name}: {thought.title}")
                if detail:
                    str_tags = sorted([t.title for t in thought.tags])
                    str_links = sorted([l.target for l in thought.links])
                    logging.info(f"tags: {', '.join(str_tags)}")
                    logging.info(f"links: {', '.join(str_links)}")


class Write:
    """Write and update thoughts in the database."""

    @staticmethod
    def parser(subparsers):
        parser = subparsers.add_parser(
            "write", help=Write.__doc__, description=Write.__doc__
        )
        parser.add_argument(
            "name", nargs=1, action="store", help="The name of the thought to update."
        )
        parser.add_argument(
            "title", nargs="+", action="store", help="The title of the thought."
        )
        parser.add_argument(
            "-t",
            "--tag",
            nargs=1,
            action="append",
            help="Adds a tag to the thought.",
        )
        parser.add_argument(
            "-l",
            "--link",
            nargs=1,
            action="append",
            help=("Adds an outward link to this thought."),
        )
        parser.add_argument(
            "-d",
            "--database",
            nargs=1,
            action="store",
            required=True,
            help="The name of the database to use.",
        )
        return parser

    def __init__(self, args):
        self.args = args

    def run(self):
        name = Name.fromStr(self.args.name)
        links = [Link(name, Name.fromStr(l[0])) for l in self.args.link or []]
        tags = [Tag.fromStr(t[0]) for t in self.args.tag or []]
        title = " ".join(self.args.title)

        t = Thought(
            name=name, title=title, tags=tags, links=links, content=[], sources=[]
        )
        tb = ThoughtBox(self.args.database[0])
        tb.addOrUpdate(t)


class Parse:
    """Write and update thoughts to the database from disk."""

    @staticmethod
    def parser(subparsers):
        parser = subparsers.add_parser(
            "parse", help=Parse.__doc__, description=Parse.__doc__
        )
        parser.add_argument(
            "name", nargs=1, action="store", help="The name of the thought to update."
        )
        parser.add_argument(
            "-d",
            "--database",
            nargs=1,
            action="store",
            required=True,
            help="The name of the database to use.",
        )
        parser.add_argument(
            "-b",
            "--box",
            "--directory",
            nargs=1,
            action="store",
            required=True,
            help="The name of the ThoughtBox directory to use.",
        )
        return parser

    def __init__(self, args):
        self.args = args

    def run(self):
        tbd = ThoughtBoxDir(self.args.box[0])
        name = Name.fromStr(self.args.name)
        thought = tbd.read(name)

        tb = ThoughtBox(self.args.database[0])
        tb.addOrUpdate(thought)


class Rename:
    """Rename thoughts in the database and on disk."""

    @staticmethod
    def parser(subparsers):
        parser = subparsers.add_parser(
            "rename", help=Rename.__doc__, description=Rename.__doc__
        )
        parser.add_argument(
            "-f",
            "--from",
            nargs=1,
            action="store",
            required=True,
            help="The name of the thought to rename.",
        )
        parser.add_argument(
            "-t",
            "--to",
            nargs=1,
            action="store",
            required=True,
            help="The new name of the thought.",
        )
        parser.add_argument(
            "-b",
            "--box",
            "--directory",
            nargs=1,
            action="store",
            required=True,
            help="The name of the ThoughtBox directory to use.",
        )
        parser.add_argument(
            "-d",
            "--database",
            nargs=1,
            action="store",
            required=True,
            help="The name of the database to use.",
        )
        return parser

    def __init__(self, args):
        self.args = args

    def run(self):
        tbd = ThoughtBoxDir(self.args.box)
        src = Name.fromStr(self.args["from"])
        to = Name.fromStr(self.args.to)

        tbd.rename(src, to)
        tb = ThoughtBox(self.args.database)
        needs_updating = tb.rename(src, to)
        logging.info(f"Successfully renamed {src} to {to}.")
        logging.info(f"The following thoughts need updating:")
        logging.info(f"{', '.join(needs_updating)}")


class Delete:
    """Delete thoughts from the database and disk."""

    @staticmethod
    def parser(subparsers):
        parser = subparsers.add_parser(
            "delete", help=Delete.__doc__, description=Delete.__doc__
        )
        parser.add_argument(
            "name", nargs=1, action="store", help="The name of the thought to delete."
        )
        parser.add_argument(
            "-d",
            "--database",
            nargs=1,
            action="store",
            required=True,
            help="The name of the database to use.",
        )
        parser.add_argument(
            "-b",
            "--box",
            "--directory",
            nargs=1,
            action="store",
            required=True,
            help="The name of the ThoughtBox directory to use.",
        )
        return parser

    def __init__(self, args):
        self.args = args

    def run(self):
        tbd = ThoughtBoxDir(self.args.box)
        name = Name.fromStr(self.args.name)

        tbd.delete(name)
        tb = ThoughtBox(self.args.database)
        tb.delete(name)
        logging.info(f"Successfully deleted {name}.")


if __name__ == "__main__":
    parse()
