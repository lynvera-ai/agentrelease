"""Read bounded UTF-8 documents without executing configuration code."""

import json
from pathlib import Path

import yaml
from yaml.nodes import MappingNode, Node

from .validation import InputError

MAX_INPUT_BYTES = 5 * 1024 * 1024


class StrictSafeLoader(yaml.SafeLoader):
    def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict:
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if type(key) is not str:
                raise InputError("INVALID_INPUT", "YAML mapping keys must be strings.")
            if key in result:
                raise InputError("DUPLICATE_KEY", f"YAML contains duplicate key '{key}'.")
            result[key] = self.construct_object(value_node, deep=deep)
        return result

    def compose_node(self, parent: Node | None, index: object) -> Node:
        if self.check_event(yaml.AliasEvent):
            raise InputError("INVALID_INPUT", "YAML aliases are not supported.")
        return super().compose_node(parent, index)


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("DUPLICATE_KEY", f"JSON contains duplicate key '{key}'.")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise InputError("INVALID_INPUT", "JSON numbers must be finite.")


def load_document(path: str | Path, kind: str) -> object:
    try:
        with Path(path).open("rb") as stream:
            content = stream.read(MAX_INPUT_BYTES + 1)
        if len(content) > MAX_INPUT_BYTES:
            raise InputError("INPUT_TOO_LARGE", f"{kind} exceeds the 5 MiB input limit.")
        text = content.decode("utf-8")
    except OSError as exc:
        raise InputError("INPUT_IO", f"Cannot read {kind} file.") from exc
    except UnicodeError as exc:
        raise InputError("INVALID_ENCODING", f"{kind} must be UTF-8.") from exc
    try:
        if kind == "policy":
            return yaml.load(text, Loader=StrictSafeLoader)
        return json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    except (yaml.YAMLError, ValueError, RecursionError) as exc:
        if isinstance(exc, InputError):
            raise
        raise InputError(
            "MALFORMED_INPUT", f"{kind} is not a valid {kind_format(kind)} document."
        ) from exc


def kind_format(kind: str) -> str:
    return "YAML" if kind == "policy" else "JSON"
