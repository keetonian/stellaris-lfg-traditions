"""Minimal parser for Paradox (Clausewitz) script files, stdlib only.

parse(text) -> list of Entry. Each entry is `key op value` (value is a str or a list of entries) or a bare value
inside a block (key and op are None), e.g. `traditions = { "a" "b" }`. Comments (#...) are dropped and quotes
are stripped from strings. Good enough for checking this mod's files; not a full game-accurate parser.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator, List, Optional, Union

OPERATORS = ("<=", ">=", "!=", "==", "=", "<", ">")
_TOKEN = re.compile(r'"(?:[^"\\\n]|\\.)*"|[{}]|<=|>=|!=|==|[=<>]|[^\s{}=<>"#]+|#[^\n]*')


class ParseError(ValueError):
    pass


@dataclass
class Entry:
    key: Optional[str]
    op: Optional[str]
    value: Union[str, List["Entry"]]
    line: int

    @property
    def is_block(self) -> bool:
        return isinstance(self.value, list)


def _tokens(text: str) -> Iterator[tuple[str, int]]:
    text = text.lstrip("﻿")
    line = 1
    pos = 0
    for m in _TOKEN.finditer(text):
        line += text.count("\n", pos, m.start())
        pos = m.start()
        tok = m.group(0)
        if tok.startswith("#"):
            continue
        yield tok, line


def _unquote(tok: str) -> str:
    return tok[1:-1] if len(tok) >= 2 and tok[0] == '"' and tok[-1] == '"' else tok


def parse(text: str) -> List[Entry]:
    toks = list(_tokens(text))
    pos = 0

    def block(depth: int) -> List[Entry]:
        nonlocal pos
        out: List[Entry] = []
        while pos < len(toks):
            tok, line = toks[pos]
            if tok == "}":
                if depth == 0:
                    raise ParseError(f"line {line}: unexpected '}}'")
                pos += 1
                return out
            if tok == "{":
                pos += 1
                out.append(Entry(None, None, block(depth + 1), line))
                continue
            if tok in OPERATORS:
                raise ParseError(f"line {line}: unexpected operator {tok!r}")
            pos += 1
            if pos < len(toks) and toks[pos][0] in OPERATORS:
                op = toks[pos][0]
                pos += 1
                if pos >= len(toks):
                    raise ParseError(f"line {line}: missing value after {tok} {op}")
                vtok, vline = toks[pos]
                if vtok == "{":
                    pos += 1
                    out.append(Entry(_unquote(tok), op, block(depth + 1), line))
                elif vtok == "}" or vtok in OPERATORS:
                    raise ParseError(f"line {vline}: missing value after {tok} {op}")
                else:
                    pos += 1
                    out.append(Entry(_unquote(tok), op, _unquote(vtok), line))
            else:
                out.append(Entry(None, None, _unquote(tok), line))
        if depth != 0:
            raise ParseError("unexpected end of file: unclosed '{'")
        return out

    return block(0)


def parse_file(path) -> List[Entry]:
    with open(path, encoding="utf-8-sig") as f:
        return parse(f.read())


def get(entries: List[Entry], key: str) -> List[Entry]:
    """All direct children with this key."""
    return [e for e in entries if e.key == key]


def first(entries: List[Entry], key: str) -> Optional[Entry]:
    found = get(entries, key)
    return found[0] if found else None


def walk(entries: List[Entry]) -> Iterator[Entry]:
    """All entries, depth-first."""
    for e in entries:
        yield e
        if e.is_block:
            yield from walk(e.value)


def bare_values(entries: List[Entry]) -> List[str]:
    return [e.value for e in entries if e.key is None and not e.is_block]
