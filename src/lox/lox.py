import sys
import os

from .token_type import TokenType
from .token import Token
from .scanner import Scanner
from .parser import Parser
from .ast_printer import AstPrinter


class Lox:
    had_error = False
    
    def __init__(self):
        if len(sys.argv) > 2:
            print("Usage: lox [script]")
            sys.exit(64)
        elif len(sys.argv) == 2:
            self.run_file(sys.argv[1])
        else:
            self.repl()

    def run_file(self, filename):
        if os.path.exists(filename):
            with open(filename, "r") as source:
                source = source.read()
                self.run(source)
                if Lox.had_error:
                    sys.exit(65)
        else:
            raise FileNotFoundError(f"file {filename} not found")

    def repl(self):
        while True:
            line = input("lox> ")
            if not line:
                break
            self.run(line)
            Lox.had_error = False

    def run(self, source):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        expression = parser.parse()
        if Lox.had_error:
            return
        print(AstPrinter().print(expression))

    def error(self, line: int, message: str):
        self._report(line, "", message)

    @staticmethod
    def report(line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        Lox.had_error = True


def error(token: Token, message: str):
    if token.token_type == TokenType.EOF:
        Lox.report(token.line, " at end", message)
    else:
        Lox.report(token.line, f" at {token.lexeme!r}", message)