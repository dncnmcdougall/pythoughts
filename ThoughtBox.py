from typing import List, Dict

from .Name import Name
from .Link import Link
from .Tag import Tag
from .Thought import Thought


class ThoughtBox:
    def __init__(self, database_path: str):
        raise NotImplementedError()

    def listTags(self) -> List[Tag]:
        raise NotImplementedError()

    def listThoughts(
        self,
        names: List[Name] = None,
        tags: List[Tag] = None,
        linked_to: List[Name] = None,
    ) -> List[Thought]:
        raise NotImplementedError()

    def listThoughtsByTag(
        self,
        names: List[Name] = None,
        tags: List[Tag] = None,
        linked_to: List[Name] = None,
    ) -> Dict[Name, List[Thought]]:
        raise NotImplementedError()

    def addOrUpdate(self, thought: Thought) -> None:
        raise NotImplementedError()

    def delete(self, name: Name) -> Thought:
        raise NotImplementedError()

    def rename(self, name: Name, new_name: Name) -> None:
        raise NotImplementedError()
