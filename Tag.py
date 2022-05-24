from dataclasses import dataclass


@dataclass
class Tag:
    """Represents a tag in a Thought."""

    id: int
    title: str
