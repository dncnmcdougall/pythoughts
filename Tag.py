from dataclasses import dataclass


@dataclass
class Tag:
    """Represents a tag in a Thought."""

    id: int
    title: str

    @staticmethod
    def fromStr(tag: str) -> "Tag":
        """Creates a tag from the given string.
        This has a default id of id=-1.
        """
        return Tag(id=-1, title=tag)

    def __hash__(self):
        return self.title.__hash__()
