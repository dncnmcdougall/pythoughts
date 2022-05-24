from os import PathLike

from .ThoughtBox import ThoughtBox
from .Thought import Thought
from .Name import Name


class ThoughtBoxDir:
    """Represents a directory containing thoughts.
    This class is used to do the file io on thought files.
    """

    def __init__(self, thought_dir: PathLike):
        raise NotImplementedError()

    def getName(self, path: PathLike) -> Name:
        raise NotImplementedError()

    def getPath(self, name: Name) -> PathLike:
        raise NotImplementedError()

    def createNew(self, name: Name) -> None:
        raise NotImplementedError()

    def read(self, name: Name) -> Thought:
        raise NotImplementedError()

    def writeDotGraph(self, box: ThoughtBox, file: PathLike) -> None:
        raise NotImplementedError()

    def rename(self, src: Name, to: Name) -> None:
        raise NotImplementedError()

    def delete(self, name: Name) -> None:
        raise NotImplementedError()
