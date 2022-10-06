from typing import List


from .expr import (
    Expr,
    Binary,
    Grouping,
    Literal,
    Unary,
)

from .lox_runtime_error import LoxRuntimeError
from .token_type import TokenType
from .token import Token


class Parser:
    class ParseError(LoxRuntimeError):
        pass

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def _expression(self) -> Expr:
        self._equality()

    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._term()

        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._previous()
            right = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self):
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)

        return self._primary()

    def _primary(self):
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            return Grouping(expr)

        raise self._error(self._peek(), "Expected expression")

    def _consume(self, tok_type: TokenType, message: str) -> Token:
        if self._check(tok_type):
            return self._advance()

        raise self._error(self._peek(), message)

    def _error(token: Token, message: str):
        from .lox import error
        error(token, message)
        return Parser.ParseError()

    def _synchronize(self):
        self._advance()

        while not self._is_at_end():
            if self._previous().token_type == TokenType.SEMICOLON:
                return

            if self._peek().token_type in (
                TokenType.CLASS,
                TokenType.FUNC,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ):
                return
            self._advance()

    def _match(self, *types: List[TokenType]) -> bool:
        for tok_type in types:
            if self._check(tok_type):
                self._advance()
                return True

        return False

    def _check(self, tok_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().token_type == tok_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().token_type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def parse(self) -> Expr:
        try:
            self._expression()
        except Parser.ParseError as error:
            return None