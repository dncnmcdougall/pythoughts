from dataclasses import dataclass


@dataclass
class Tag:
    """Represents a tag in a Thought."""

    id: int
    title: str

    @staticmethod
    def fromStr(tag: str) -> "Tag":
        return Tag(id=-1, title=tag)

    def __hash__(self):
        return self.title.__hash__()
