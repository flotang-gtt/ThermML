from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import re
from typing import NamedTuple

from lxml import etree


NS = {
    "t": "http://calphad.org/thermml/0.1",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


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

        if char == "{":
            end = text.find("}", position + 1)
            if end == -1:
                raise ExpressionSyntaxError(
                    f"Unterminated braced reference starting at position {position}"
                )

            value = text[position + 1 : end]
            if not value:
                raise ExpressionSyntaxError(
                    f"Empty braced reference at position {position}"
                )

            tokens.append(Token("IDENT", value, position))
            position = end + 1
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


def collect_symbolic_references(text: str) -> set[str]:
    tokens = tokenize_expression(text.strip())
    references: set[str] = set()

    for index, token in enumerate(tokens):
        if token.kind != "IDENT":
            continue

        next_kind = tokens[index + 1].kind if index + 1 < len(tokens) else "EOF"
        if next_kind == "LPAREN":
            continue

        if token.value in {"T", "P", "i", "j", "k"}:
            continue

        references.add(token.value)

    return references


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
    declared_global_expressions = {
        expression.attrib["name"]
        for expression in doc.xpath('./t:globalExpressions/t:expression', namespaces=NS)
        if "name" in expression.attrib
    }

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

    for range_node in doc.xpath('./t:globalExpressions/t:expression/t:range[not(*)]', namespaces=NS):
        text = (range_node.text or '').strip()
        if not text:
            continue

        for reference in sorted(collect_symbolic_references(text)):
            if reference not in declared_global_expressions:
                errors.append(
                    SemanticValidationError(
                        path=doc.getpath(range_node),
                        message=(
                            f"Unknown symbolic reference {reference!r} in range expression; "
                            "expected a declared global expression name"
                        ),
                    )
                )

    phase_by_name = {
        phase.attrib['name']: phase
        for phase in doc.xpath('.//t:phase[@name]', namespaces=NS)
    }

    for component in doc.xpath('./t:systemComponents/t:systemComponent[@refstate]', namespaces=NS):
        refstate = component.attrib.get('refstate', '')
        if not refstate:
            continue

        if refstate not in phase_by_name:
            errors.append(
                SemanticValidationError(
                    path=doc.getpath(component),
                    message=(
                        f"System component {component.attrib.get('symbol', '<unknown>')!r} "
                        f"uses refstate {refstate!r}, which must be empty or match a "
                        "declared phase name"
                    ),
                )
            )

    for parent in doc.xpath("//*[t:range[@low and @high]]", namespaces=NS):
        ranges = [
            child
            for child in parent
            if child.tag == "{http://calphad.org/thermml/0.1}range"
            and "low" in child.attrib
            and "high" in child.attrib
        ]
        previous_high: Decimal | None = None
        previous_path: str | None = None

        for range_node in ranges:
            low = Decimal(range_node.attrib["low"])
            high = Decimal(range_node.attrib["high"])
            path = doc.getpath(range_node)

            if low > high:
                errors.append(
                    SemanticValidationError(
                        path=path,
                        message=(
                            f"Invalid range bounds: low={range_node.attrib['low']} must be "
                            f"less than or equal to high={range_node.attrib['high']}"
                        ),
                    )
                )

            if previous_high is not None and low < previous_high:
                errors.append(
                    SemanticValidationError(
                        path=path,
                        message=(
                            "Overlapping or out-of-order ranges: "
                            f"{path} starts at {range_node.attrib['low']} before the previous "
                            f"range ended at {previous_high}"
                            + (f" ({previous_path})" if previous_path else "")
                        ),
                    )
                )

            previous_high = high
            previous_path = path

    for phase in doc.xpath('.//t:phase[t:structure/t:sublattices]', namespaces=NS):
        phase_name = phase.attrib.get('name', '<unknown>')
        sublattices = phase.xpath('./t:structure/t:sublattices', namespaces=NS)[0]
        multiplicity_count = len(sublattices.attrib.get('multiplicities', '').split())
        site_count = len(sublattices.xpath('./t:site', namespaces=NS))

        if multiplicity_count != site_count:
            errors.append(
                SemanticValidationError(
                    path=doc.getpath(sublattices),
                    message=(
                        f"Phase {phase_name!r} declares {multiplicity_count} multiplicities "
                        f"for {site_count} sublattice sites"
                    ),
                )
            )

        for endmember in phase.xpath('./t:endmembers/t:endmember', namespaces=NS):
            constituent_sites = len(
                endmember.xpath('./t:constituents/t:site', namespaces=NS)
            )
            if constituent_sites != site_count:
                errors.append(
                    SemanticValidationError(
                        path=doc.getpath(endmember),
                        message=(
                            f"Endmember {endmember.attrib.get('name', '<unknown>')!r} in phase "
                            f"{phase_name!r} uses {constituent_sites} constituent sites but the "
                            f"phase structure declares {site_count}"
                        ),
                    )
                )

        for interaction in phase.xpath('./t:interactions/t:interaction', namespaces=NS):
            constituent_sites = len(
                interaction.xpath('./t:constituents/t:site', namespaces=NS)
            )
            if constituent_sites != site_count:
                errors.append(
                    SemanticValidationError(
                        path=doc.getpath(interaction),
                        message=(
                            f"Interaction {interaction.attrib.get('name', '<unknown>')!r} in "
                            f"phase {phase_name!r} uses {constituent_sites} constituent sites "
                            f"but the phase structure declares {site_count}"
                        ),
                    )
                )

    for interpolation in doc.xpath('.//t:ternaryInterpolations/t:interpolation', namespaces=NS):
        labels: list[str] = []

        for const in interpolation.xpath('.//t:const', namespaces=NS):
            site = const.attrib.get('site')
            site_index = const.attrib.get('siteIndex')

            if site and site_index and site != site_index:
                errors.append(
                    SemanticValidationError(
                        path=doc.getpath(const),
                        message=(
                            f"Interpolation locator aliases disagree: site={site!r} and "
                            f"siteIndex={site_index!r}"
                        ),
                    )
                )

            label = site or site_index
            if label:
                labels.append(label)

        if labels and sorted(labels) != ['i', 'j', 'k']:
            errors.append(
                SemanticValidationError(
                    path=doc.getpath(interpolation),
                    message=(
                        "Interpolation locators must contain each of i, j, and k exactly once; "
                        f"found {labels}"
                    ),
                )
            )

    return errors