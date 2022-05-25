from dataclasses import dataclass

from .Name import Name


@dataclass
class Link:
    """Represents a link between Thoughts."""

    source: Name
    target: str

    @staticmethod
    def fromStr(source: str, target: str) -> "Link":
        return Link(source=Name.fromStr(source), target=target)
