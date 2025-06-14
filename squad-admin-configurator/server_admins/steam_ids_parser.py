import re
from dataclasses import dataclass
from enum import Enum
from functools import cache
from typing import Iterable


@dataclass
class Node:
    kind: str
    value: str


class SteamIDsSpec(Enum):
    """Спецификация формата файла для списка steam id"""

    EMPTY = r"[ \t]+"
    STEAMID = r"76\d{15}"
    COMMENT = r"#.*$"
    NEWLINE = r"\r\n|\r|\n"
    MISMATCH = r".+"

    @classmethod
    @cache
    def get_regex(cls):
        return "|".join(f"(?P<{kind.name}>{kind.value})" for kind in cls)

    @classmethod
    @cache
    def get_compiled_regex(cls):
        return re.compile(cls.get_regex(), re.M)

    @classmethod
    def parse_iter(cls, text):
        spec = cls.get_compiled_regex()

        for _match in spec.finditer(text):
            yield Node(_match.lastgroup, _match.group())

    @classmethod
    def parse(cls, text: str) -> list[Node]:
        spec = cls.get_compiled_regex()

        return [Node(_m.lastgroup, _m.group()) for _m in spec.finditer(text)]

    @classmethod
    def check_errors(cls, nodes: Iterable[Node]) -> list:
        current_line = 1
        errors = []

        for node in nodes:
            match node.kind:
                case SteamIDsSpec.NEWLINE.name:
                    current_line += 1
                case SteamIDsSpec.MISMATCH.name:
                    errors.append(error_description(node.kind, current_line, node.value))

        return errors


def error_description(kind, line, value):
    """Генерация человекочитаемого описания ошибок"""
    match kind:
        case SteamIDsSpec.MISMATCH.name:
            return f"Неизвестный символ '{value}' в строке #{line}"
