from dataclasses import dataclass

from .Name import Name


@dataclass
class Link:
    """Represents a link between Thoughts."""

    source: Name
    dest: Name
