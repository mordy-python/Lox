from typing import Any, Callable, Dict, List

from lox.token import Token
from lox.token_type import TokenType


class Scanner:
    tokens: List
    start: int = 0
    current: int = 0
    line: int = 1
    keywords = {
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "class": TokenType.CLASS,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "nil": TokenType.NIL,
        "func": TokenType.FUNC,
        "for": TokenType.FOR,
        "while": TokenType.WHILE,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "var": TokenType.VAR,
    }

    def __init__(self, source: str, on_error=None) -> None:
        """
        Create a new Scanner that will scan `source`.
        `on_error` will be called when an error is encountered.
        """
        self.source = source
        self.on_error = on_error
        self.tokens = []

    def scan_tokens(self) -> List[Token]:
        while not self._is_at_end():
            # We're at the start of the next lexeme
            self.start = self.current
            self._scan_token()
        # Add an EOF as the last token
        self.tokens.append(
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=self.line)
        )
        return self.tokens

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]
