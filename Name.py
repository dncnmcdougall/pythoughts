import string

from typing import List


class Name:
    """Represents the name of a Thought."""

    def __init__(self, parts: List[str]):
        self.parts = parts

    @staticmethod
    def fromStr(name: str) -> "Name":
        if not name:
            return Name([])
        parts = [name[0]]
        letter = name[0].isalpha()
        for i in range(1, len(name)):
            if letter == name[i].isalpha():
                parts[-1] += name[i]
            else:
                letter = name[i].isalpha()
                parts.append(name[i])
        return Name(parts)

    @staticmethod
    def findNext(names: List["Name"], name: "Name") -> "Name":
        """Finds the next available subname for name, given the sorted list of used names.

        name: the base name to start with.
        names: the sorted list of used names.
        """
        name_parts = name.parts.copy()
        length = len(name_parts)
        if len(name_parts) == 0 or name_parts[-1].isalpha():
            name_parts.append("1")
        else:
            name_parts.append("a")

        for i in range(len(names)):
            if len(names[i].parts) <= length:
                continue
            elif name_parts[0:-1] != names[i].parts[0:length]:
                continue
            elif name_parts[-1] == names[i].parts[length]:
                name_parts[-1] = Name._incPart(name_parts[-1])
        return Name(name_parts)

    @staticmethod
    def _incPart(part: str) -> str:
        if part.isalpha():
            list_part = list(part)
            j = 1
            i = string.ascii_lowercase.index(list_part[-j]) + 1

            while j < len(list_part) and i == 26:
                list_part[-j] = "a"
                j += 1
                i = string.ascii_lowercase.index(list_part[-j]) + 1
            if j == len(list_part) and i == 26:
                list_part[-j] = "a"
                return "".join(["a"] + list_part)
            else:
                list_part[-j] = string.ascii_lowercase[i]
            return "".join(list_part)
        else:
            return "%d" % (int(part) + 1)

    def next(self) -> "Name":
        new_parts = self.parts.copy()
        if len(new_parts) == 0:
            new_parts.append("1")
        else:
            new_parts[-1] = Name._incPart(new_parts[-1])
        return Name(new_parts)

    def __repr__(self) -> str:
        return "".join(self.parts)

    def _strComp(self, str1, str2):
        len1 = len(str1)
        len2 = len(str2)
        if len1 < len2:
            return -1
        elif len1 > len2:
            return 1
        else:
            for i, c in enumerate(str1):
                if c < str2[i]:
                    return -1
                if c > str2[i]:
                    return 1
            return 0

    def _comp(self, other: "Name") -> int:
        other_len = len(other.parts)
        for i, item in enumerate(self.parts):
            if i >= other_len:
                return 1
            str_comp = self._strComp(item, other.parts[i])
            if str_comp != 0:
                return str_comp
        if len(self.parts) < other_len:
            return -1
        return 0

    def __lt__(self, other):
        return self._comp(other) < 0

    def __gt__(self, other):
        return self._comp(other) > 0

    def __eq__(self, other):
        return self._comp(other) == 0

    def __le__(self, other):
        return self._comp(other) <= 0

    def __ge__(self, other):
        return self._comp(other) >= 0

    def __ne__(self, other):
        return self._comp(other) != 0
