import argparse

from .ThoughtBoxDir import ThoughtBoxDir
from .Name import Name
from .Link import Link
from .Thought import Thought
from .ThoughtBox import ThoughtBox


def parse():
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

    args = main_parser.parse_args()

    if args.command == "help":
        for p in parsers:
            if p.prog.split()[1] == args.help:
                p.print_help()
                exit(0)
        main_parser.print_help()
        exit(0)

    for cmd in cmds:
        if cmd.__name__.lower() == args.command:
            cmd(args).run()


class Create:
    """Create new thought files on disk."""

    @staticmethod
    def parser(subparsers):
        parser = subparsers.add_parser(
            "create", help=Create.__doc__, description=Create.__doc__
        )
        parser.add_argument(
            "name", nargs=1, action="store", help="The name of the thought to update."
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
        tbd.createNew(name)


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
            choices=["name", "tag"],
            help=(
                "Display the toughts either as a list (--by=name) or grouped by tags"
                " (--by=tag)."
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
                "Display the thoughts which link to the given links. If no link is"
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
        tb = ThoughtBox(self.args.database)
        names = [Name.fromStr(n[0]) for n in self.args.names]
        links = [Name.fromStr(l[0]) for l in self.args.links]
        tags = [Name.fromStr(t[0]) for t in self.args.tags]
        if self.args.by == "tag":
            tb.listThoughtsByTag(names=names, tags=tags, linked_to=links)
            # TODO: print
            raise NotImplementedError()
        else:
            tb.listThoughts(names=names, tags=tags, linked_to=links)
            # TODO: print
            raise NotImplementedError()


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
            help="Adds a tag to the thought. Ignored if --create is presnet.",
        )
        parser.add_argument(
            "-l",
            "--link",
            nargs=1,
            action="append",
            help=(
                "Adds an outward link to this thought. Ignored is --create is presnet."
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
        print(self.args)
        name = Name.fromStr(self.args.name)
        links = [Link(name, Name.fromStr(l[0])) for l in self.args.links]
        tags = [Name.fromStr(t[0]) for t in self.args.tags]
        title = " ".join(self.args.title)

        t = Thought(name=name, title=title, tags=tags, links=links)
        tb = ThoughtBox(self.args.database)
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
        tbd = ThoughtBoxDir(self.args.box)
        name = Name.fromStr(self.args.name)
        thought = tbd.read(name)

        tb = ThoughtBox(self.args.database)
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

        tb = ThoughtBox(self.args.database)
        tb.rename(src, to)
        tbd.rename(src, to)


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

        tb = ThoughtBox(self.args.database)
        tb.delete(name)
        tbd.delete(name)


if __name__ == "__main__":
    parse()
