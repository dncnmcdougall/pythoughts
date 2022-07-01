import os
import shutil
import pathlib

from os import PathLike

from .ThoughtBox import ThoughtBox
from .Thought import Thought
from .Name import Name


class ThoughtBoxDir:
    """Represents a directory containing thoughts.
    This class is used to do the file io on thought files.
    """

    def __init__(self, thought_dir: PathLike):
        self.dir = thought_dir

    def getName(self, path: PathLike) -> Name:
        """Converts a path into a thought name."""
        return Name.fromStr(os.path.splitext(os.path.basename(path))[0])

    def getPath(self, name: Name) -> PathLike:
        """Converts a thought name into a path pointing into this directory."""
        return pathlib.Path(os.path.join(self.dir, str(name) + ".tb"))

    def createNew(self, name: Name, force_override=False) -> Name:
        """
        Creates a new empty thought.

        If force_override==True:
            then the thought has the name given.
            A name of "" is invalid, as it would point to a non-existing file.
            WARNING: This will override exisitng thoughts if they are specified.
        If force_override==False:
            then the thought has the next available subname of name.
            A name of "" means find the next available top level name.

        Arguments:
        name:           The name or parent name of the thought.
        force_override: Force the name of the new thought to be name, even if it already exisits.

        Returns:
        the name of the created thought.

        """
        current_name = name
        if not force_override:
            while os.path.exists(self.getPath(current_name)):
                current_name = current_name.next()

        with open(self.getPath(current_name), "w") as tf:
            tf.write("# <+title+>\n")
            tf.write("\n")
            tf.write("# sources\n")
            tf.write("\n")
            tf.write("# tags\n")
        return current_name

    def read(self, name: Name) -> Thought:
        """Read and parse the thought file in this directory."""
        lines = []
        with open(self.getPath(name), "r") as thought_file:
            lines = [l.strip() for l in thought_file.readlines()]

        return Thought.parse(lines, name)

    def writeDotGraph(
        self,
        box: ThoughtBox,
        file: PathLike,
        use_links=True,
        link_tags=False,
        show_tags=True,
    ) -> None:
        """Write out a graph of the links between thoughts.

        Arguments:
        box:        The database to read information out of.
        file:       The file to write into.
        use_links:  If true the graph links thoughts with links. If false links are ignored .
        link_tags:  If true the graph links thoughts with tags. If false tags are duplicated.
        show_tags:  If true tags are shown on thoughts. If false tags are not shown (unless link_tags is true).
        """
        raise NotImplementedError()

    def rename(self, src: Name, to: Name) -> None:
        """Rename the specified thought on disk."""
        src_path = self.getPath(src)
        to_path = self.getPath(to)
        if os.path.exists(src_path) and os.path.exists(to_path):
            raise FileExistsError()
        shutil.move(src_path, to_path)

    def delete(self, name: Name) -> None:
        """Delete the specified thought off disk."""
        os.remove(self.getPath(name))
