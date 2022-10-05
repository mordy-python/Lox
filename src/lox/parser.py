from typing import List

from .expr import *
from .token_type import TokenType
from .token import Token


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
