from __future__ import annotations

from dataclasses import dataclass
import re
from typing import NamedTuple

from lxml import etree


NS = {"t": "http://calphad.org/thermml/0.1"}


@dataclass(frozen=True)
class SemanticValidationError:
    path: str
    message: str


class ExpressionSyntaxError(ValueError):
    pass


class Token(NamedTuple):
    kind: str
    value: str
    position: int


NUMBER_RE = re.compile(r"(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?")
IDENT_RE = re.compile(r"[#A-Za-z_][#A-Za-z0-9_\[\]\.:/<>]*")


def tokenize_expression(text: str) -> list[Token]:
    tokens: list[Token] = []
    position = 0

    while position < len(text):
        char = text[position]

        if char.isspace():
            position += 1
            continue

        if text.startswith("**", position):
            tokens.append(Token("POW", "**", position))
            position += 2
            continue

        if char == "^":
            tokens.append(Token("POW", "^", position))
            position += 1
            continue

        if char in "+-*/(),":
            kind = {
                "+": "PLUS",
                "-": "MINUS",
                "*": "STAR",
                "/": "SLASH",
                "(": "LPAREN",
                ")": "RPAREN",
                ",": "COMMA",
            }[char]
            tokens.append(Token(kind, char, position))
            position += 1
            continue

        number_match = NUMBER_RE.match(text, position)
        if number_match is not None:
            value = number_match.group(0)
            tokens.append(Token("NUMBER", value, position))
            position = number_match.end()
            continue

        ident_match = IDENT_RE.match(text, position)
        if ident_match is not None:
            value = ident_match.group(0)
            tokens.append(Token("IDENT", value, position))
            position = ident_match.end()
            continue

        raise ExpressionSyntaxError(
            f"Unexpected character {char!r} at position {position}"
        )

    tokens.append(Token("EOF", "", position))
    return tokens


class ExpressionParser:
    def __init__(self, text: str):
        self.text = text
        self.tokens = tokenize_expression(text)
        self.index = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def advance(self) -> Token:
        token = self.current
        self.index += 1
        return token

    def expect(self, kind: str) -> Token:
        token = self.current
        if token.kind != kind:
            raise ExpressionSyntaxError(
                f"Expected {kind} at position {token.position}, found {token.value!r}"
            )
        return self.advance()

    def parse(self) -> None:
        self.parse_expression()
        if self.current.kind != "EOF":
            token = self.current
            raise ExpressionSyntaxError(
                f"Unexpected token {token.value!r} at position {token.position}"
            )

    def parse_expression(self) -> None:
        self.parse_term()
        while self.current.kind in {"PLUS", "MINUS"}:
            self.advance()
            self.parse_term()

    def parse_term(self) -> None:
        self.parse_power()
        while self.current.kind in {"STAR", "SLASH"}:
            self.advance()
            self.parse_power()

    def parse_power(self) -> None:
        self.parse_unary()
        if self.current.kind == "POW":
            self.advance()
            self.parse_power()

    def parse_unary(self) -> None:
        if self.current.kind in {"PLUS", "MINUS"}:
            self.advance()
            self.parse_unary()
            return
        self.parse_primary()

    def parse_primary(self) -> None:
        token = self.current

        if token.kind == "NUMBER":
            self.advance()
            return

        if token.kind == "IDENT":
            self.advance()
            if self.current.kind == "LPAREN":
                self.advance()
                self.parse_expression()
                while self.current.kind == "COMMA":
                    self.advance()
                    self.parse_expression()
                self.expect("RPAREN")
            return

        if token.kind == "LPAREN":
            self.advance()
            self.parse_expression()
            self.expect("RPAREN")
            return

        raise ExpressionSyntaxError(
            f"Expected expression term at position {token.position}, found {token.value!r}"
        )


def validate_expression_text(text: str) -> None:
    stripped = text.strip()
    if not stripped:
        raise ExpressionSyntaxError("Expression is empty")
    ExpressionParser(stripped).parse()


def iter_expression_nodes(doc: etree._ElementTree):
    for node in doc.xpath("//t:expr", namespaces=NS):
        yield node, "expr"
    for node in doc.xpath("//t:range[not(*)]", namespaces=NS):
        if node.text and node.text.strip():
            yield node, "range"


def validate_document_semantics(
    doc: etree._ElementTree,
) -> list[SemanticValidationError]:
    errors: list[SemanticValidationError] = []

    for node, label in iter_expression_nodes(doc):
        text = node.text or ""
        try:
            validate_expression_text(text)
        except ExpressionSyntaxError as error:
            errors.append(
                SemanticValidationError(
                    path=doc.getpath(node),
                    message=f"Invalid {label} expression syntax: {error}",
                )
            )

    return errors