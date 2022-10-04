from typing import Any
from .token_type import TokenType


class Token:
    """
    Store Parsed Tokens
    """

    def __init__(
        self, token_type: TokenType, lexeme: str, literal: Any, line: int
    ) -> None:
        """Create a new token"""
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self) -> str:
        return f"<{self.token_type} {self.lexeme!r} {self.literal}>"
