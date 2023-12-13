import re
from dataclasses import dataclass
from enum import Enum
from functools import cache


@dataclass
class Node:
    kind: str
    value: str


class LayerSpec(Enum):
    """Спецификация формата файла для списка карт"""

    LAYER = r"^[A-Za-z0-9_]+"
    COMMENT = r"^\ */.*$"
    EMPTY = r"\ +"
    NEWLINE = r"\r\n|\r|\n"
    MISMATCH_SPELLING = r"[A-Za-z0-9_]+"
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
    def parse(cls, text) -> list[Node]:
        spec = cls.get_compiled_regex()

        return [Node(_m.lastgroup, _m.group()) for _m in spec.finditer(text)]

    @classmethod
    def check_errors(cls, nodes) -> list:
        current_line = 1
        errors = []

        for node in nodes:
            match node.kind:
                case LayerSpec.NEWLINE.name:
                    current_line += 1
                case LayerSpec.MISMATCH.name | LayerSpec.MISMATCH_SPELLING.name:
                    errors.append(
                        error_description(node.kind, current_line, node.value)
                    )

        return errors


def error_description(kind, line, value):
    """Генерация человекочитаемого описания ошибок"""
    match kind:
        case LayerSpec.MISMATCH.name:
            return f"Неизвестный символ '{value}' в строке #{line}"
        case LayerSpec.MISMATCH_SPELLING.name:
            return (
                f"Название леера '{value}' должно находится в начале"
                f" строки, строка с ошибкой #{line}"
            )
