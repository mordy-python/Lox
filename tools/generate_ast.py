"""
Creates the python files that contain the code with the nodes for the trees
"""
import re
import sys
from pathlib import Path
from typing import Dict, List

import black
import isort


class GenerateAst:
    def __init__(self, outputdir: str):
        self.outputdir = Path(outputdir)

    def generate_ast(self):
        self._create_output_directory()
        self._define_ast(
            base_name="Expr",
            types=[
                "Assign   : Token name, Expr value",
                "Binary   : Expr left, Token operator, Expr right",
                "Call     : Expr callee, Token paren, List<Expr> arguments",
                "Get      : Expr obj, Token name",
                "Grouping : Expr expression",
                "Literal  : Any value",
                "Logical  : Expr left, Token operator, Expr right",
                "Set      : Expr obj, Token name, Expr value",
                "Super    : Token keyword, Token method",
                "This     : Token keyword",
                "Unary    : Token operator, Expr right",
                "Variable : Token name",
            ],
            imports={"typing": ["Any", "List"], ".token": ["Token"]},
        )
        self._define_ast(
            base_name="Stmt",
            types=[
                "Block      : List<Stmt> statements",
                "Class      :  Token name, Optional[Variable] superclass, "
                "List<Function> methods",
                "Expression : Expr expression",
                "Function   : Token name, List<Token> params, List<Stmt> body",
                "If      : Expr condition, Stmt thenBranch, Optional[Stmt] elseBranch",
                "Print      : Expr expression",
                "Return     : Token keyword, Optional[Expr] value",
                "Var        : Token name, Optional[Expr] initializer",
                "While      : Expr condition, Stmt body",
            ],
            imports={
                "typing": ["List", "Optional"],
                ".expr": ["Expr", "Variable"],
                ".token": ["Token"],
            },
        )

    def _create_output_directory(self):
        """Make sure the output directory exists"""
        if self.outputdir.exists() and self.outputdir.is_dir():
            return
        Path.mkdir(self.outputdir, parents=True)

    def _define_ast(self, base_name: str, types: List, imports: Dict[str, List] = None):
        """
        Create a new ast class
        :param base_name: This will be the base class, for example Expr or Stmt
        :param types: A list of types that will be implemented
        :param imports: A list of imports that will be created in the top of the file.
            This is a list of dicts, where the key of the dict is the module
            (eg: from x), and the values the imports themself, eg (import foo, bar)
        """
        lines = [
            "# This file has been auto-generated from tools/generate_ast.py",
            "# Any changes made to this file will be overwritten.",
            "",
            "from abc import ABC, abstractmethod",
            "from __future__ import annotations",
        ]

        if imports:
            lines.extend(self._define_imports(imports))

        lines.extend(self._define_visitor(base_name, types))

        lines.extend(
            [
                f"class {base_name}(ABC):",
                f"    @abstractmethod",
                f"    def accept(self, visitor: {base_name}Visitor):",
                "         raise NotImplementedError",
            ]
        )

        for class_type in types:
            class_type: str
            class_name = class_type.split(":")[0].strip()
            # Replace <> with []
            fields = (
                class_type.split(":")[1].strip().replace("<", "[").replace(">", "]")
            )
            lines.extend(self._define_type(base_name, class_name, fields))

        self._write_files(base_name, lines)

    def _define_imports(self, imports: Dict[str, str]) -> List[str]:
        lines = []
        for module, identifiers in imports.items():
            lines.append(f"from {module} import {', '.join(identifiers)}")

        return lines

    def _define_visitor(self, base_name: str, types: List) -> List:
        """Create the {base_name}Visitor"""
        visitor_lines = [
            f"class {base_name}Visitor(ABC):",
            f'    """This class is used as a visitor for the {base_name} class"""',
        ]

        for class_type in types:
            class_type: str
            class_name = class_type.split(":")[0].strip()
            lines = [
                "    @abstractmethod",
                f"    def visit_{class_name.lower()}_{base_name.lower()}(self, {base_name.lower()}: {class_name}):",
                "        raise NotImplementedError",
            ]
            visitor_lines.extend(lines)
        return visitor_lines

    def _define_type(self, base_name: str, class_name: str, fields_list: str) -> List:
        # __init__ method
        fields = [field.strip().split() for field in fields_list.split(",")]

        # Convert snakeCase to camel_case
        for field in fields:
            field[1] = re.sub(r"(?<!^)(?=[A-Z])", "_", field[1]).lower()

        init_fields = ", ".join(f"{field[1]}: {field[0]}" for field in fields)

        lines = [
            f"class {class_name}({base_name}):",
            f"    def __init__(self, {init_fields}):",
        ]

        for field in fields:
            lines.append(f"      self.{field[1]} = {field[1]}")

        # Add the visit method
        visitor_method = [
            "",
            f"    def accept(self, visitor: {base_name}Visitor):",
            f'        """Create an accept method that calls the visitor"""',
            f"        return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)",
        ]

        lines.extend(visitor_method)
        return lines

    def _write_files(self, base_name: str, lines: List):
        """Write lines to a file"""
        output_file = self.outputdir / f"{base_name.lower()}.py"

        # Reformat with black
        file_contents = black.format_str("\n".join(lines), mode=black.FileMode())
        # file_contents = "\n".join(lines)
        # Reformat it with isort
        file_contents = isort.code(file_contents)

        with open(output_file, "w") as f:
            # Add newlines
            f.writelines(line for line in file_contents)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <output_dir>")
        sys.exit(64)

    ast_gen = GenerateAst(sys.argv[1])
    ast_gen.generate_ast()