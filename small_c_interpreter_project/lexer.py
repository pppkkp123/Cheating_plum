from dataclasses import dataclass
from typing import List
from errors import LexError


@dataclass
class Token:
    type: str
    value: object
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r}, line={self.line}, col={self.col})"


KEYWORDS = {
    "int", "char", "void",
    "if", "else", "while", "for",
    "break", "continue", "return",
}

TWO_CHAR_OPS = {
    "==", "!=", "<=", ">=", "&&", "||",
    "++", "--", "+=", "-=", "*=", "/=", "%=",
}

ONE_CHAR = set("+-*/%<>=!&|^~(){}[];,.")


class Lexer:
    """Turn Small-C source text into tokens."""

    def __init__(self, source: str):
        self.source = source
        self.i = 0
        self.line = 1
        self.col = 1
        self.n = len(source)

    def peek(self, offset=0) -> str:
        idx = self.i + offset
        if idx >= self.n:
            return "\0"
        return self.source[idx]

    def advance(self) -> str:
        ch = self.peek()
        self.i += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def skip_whitespace_and_comments(self):
        while True:
            while self.peek().isspace():
                self.advance()

            # // line comment
            if self.peek() == "/" and self.peek(1) == "/":
                while self.peek() not in ("\n", "\0"):
                    self.advance()
                continue

            # /* block comment */
            if self.peek() == "/" and self.peek(1) == "*":
                self.advance()
                self.advance()
                while True:
                    if self.peek() == "\0":
                        raise LexError(f"Unterminated block comment at line {self.line}")
                    if self.peek() == "*" and self.peek(1) == "/":
                        self.advance()
                        self.advance()
                        break
                    self.advance()
                continue

            break

    def read_number(self):
        line, col = self.line, self.col
        text = ""

        if self.peek() == "0" and self.peek(1).lower() == "x":
            text += self.advance()
            text += self.advance()
            while self.peek().isdigit() or self.peek().lower() in "abcdef":
                text += self.advance()
            return Token("NUMBER", int(text, 16), line, col)

        while self.peek().isdigit():
            text += self.advance()
        return Token("NUMBER", int(text), line, col)

    def read_identifier(self):
        line, col = self.line, self.col
        text = ""
        while self.peek().isalnum() or self.peek() == "_":
            text += self.advance()
        if text in KEYWORDS:
            return Token("KEYWORD", text, line, col)
        return Token("IDENT", text, line, col)

    def read_string(self):
        line, col = self.line, self.col
        self.advance()  # opening "
        chars = []
        while self.peek() not in ('"', "\0"):
            ch = self.advance()
            if ch == "\\":
                esc = self.advance()
                mapping = {"n": "\n", "t": "\t", "r": "\r", "0": "\0", '"': '"', "\\": "\\"}
                chars.append(mapping.get(esc, esc))
            else:
                chars.append(ch)
        if self.peek() != '"':
            raise LexError(f"Unterminated string at line {line}, col {col}")
        self.advance()
        return Token("STRING", "".join(chars), line, col)

    def read_char(self):
        line, col = self.line, self.col
        self.advance()  # opening '
        if self.peek() == "\\":
            self.advance()
            esc = self.advance()
            mapping = {"n": "\n", "t": "\t", "r": "\r", "0": "\0", "'": "'", "\\": "\\"}
            ch = mapping.get(esc, esc)
        else:
            ch = self.advance()
        if self.peek() != "'":
            raise LexError(f"Invalid char literal at line {line}, col {col}")
        self.advance()
        return Token("NUMBER", ord(ch), line, col)

    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            self.skip_whitespace_and_comments()
            ch = self.peek()
            line, col = self.line, self.col

            if ch == "\0":
                tokens.append(Token("EOF", "", line, col))
                return tokens

            if ch.isdigit():
                tokens.append(self.read_number())
                continue

            if ch.isalpha() or ch == "_":
                tokens.append(self.read_identifier())
                continue

            if ch == '"':
                tokens.append(self.read_string())
                continue

            if ch == "'":
                tokens.append(self.read_char())
                continue

            two = ch + self.peek(1)
            if two in TWO_CHAR_OPS:
                self.advance()
                self.advance()
                tokens.append(Token("SYMBOL", two, line, col))
                continue

            if ch in ONE_CHAR:
                self.advance()
                tokens.append(Token("SYMBOL", ch, line, col))
                continue

            raise LexError(f"Unknown character {ch!r} at line {line}, col {col}")
