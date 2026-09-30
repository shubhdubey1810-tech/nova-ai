"""
NØVA AI
Universal Local Solver

Local capabilities:
- Arithmetic
- Algebra
- Equations
- Simplification
- Factorization
- Derivatives
- Integrals
- Limits
"""

from __future__ import annotations

import ast
import operator
import re
from typing import Optional

import sympy as sp


class UniversalSolver:

    def __init__(self) -> None:
        self.x = sp.Symbol("x")
        self.y = sp.Symbol("y")
        self.z = sp.Symbol("z")

    # --------------------------------------------------
    # Detection
    # --------------------------------------------------

    def looks_like_math(
        self,
        text: str
    ) -> bool:

        value = text.lower().strip()

        math_words = [
            "calculate",
            "solve",
            "equation",
            "simplify",
            "factor",
            "derivative",
            "differentiate",
            "integrate",
            "integral",
            "limit",
            "algebra",
            "math",
            "find x",
            "find y",
            "square root",
            "sqrt",
        ]

        if any(
            word in value
            for word in math_words
        ):
            return True

        # Strong signal for mathematical expressions.
        if re.search(
            r"\d+\s*[\+\-\*/\^]\s*\d+",
            value
        ):
            return True

        if "=" in value:
            return True

        return False

    # --------------------------------------------------
    # Clean expression
    # --------------------------------------------------

    def _clean_expression(
        self,
        expression: str
    ) -> str:

        expression = expression.strip()

        expression = expression.replace(
            "^",
            "**"
        )

        expression = expression.replace(
            "×",
            "*"
        )

        expression = expression.replace(
            "÷",
            "/"
        )

        expression = expression.replace(
            "π",
            "pi"
        )

        expression = expression.replace(
            "√",
            "sqrt"
        )

        return expression

    def _parse_expression(
        self,
        expression: str
    ):

        expression = expression.strip()

        if len(expression) > 500:
            raise ValueError("Expression is too long.")

        tree = ast.parse(
            expression,
            mode="eval"
        )

        names = {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "pi": sp.pi,
            "E": sp.E,
        }

        functions = {
            "sqrt": sp.sqrt,
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "log": sp.log,
            "exp": sp.exp,
            "Abs": sp.Abs,
            "abs": sp.Abs,
        }

        binary_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: sp.Mod,
        }

        def convert(node):

            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, (int, float))
                and not isinstance(node.value, bool)
            ):
                return sp.Integer(node.value) if isinstance(node.value, int) else sp.Float(node.value)

            if isinstance(node, ast.Name):

                if node.id in names:
                    return names[node.id]

                if node.id.isidentifier() and not node.id.startswith("_"):
                    return sp.Symbol(node.id)

                raise ValueError("Unsupported symbol.")

            if isinstance(node, ast.UnaryOp):

                if isinstance(node.op, ast.UAdd):
                    return convert(node.operand)

                if isinstance(node.op, ast.USub):
                    return -convert(node.operand)

                raise ValueError("Unsupported unary operator.")

            if isinstance(node, ast.BinOp):

                operation = binary_operators.get(
                    type(node.op)
                )

                if operation is None:
                    raise ValueError("Unsupported binary operator.")

                return operation(
                    convert(node.left),
                    convert(node.right)
                )

            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and not node.keywords
                and len(node.args) <= 4
            ):

                function = functions.get(
                    node.func.id
                )

                if function is not None:
                    return function(
                        *[
                            convert(argument)
                            for argument in node.args
                        ]
                    )

            raise ValueError("Unsupported expression.")

        return convert(tree.body)

    # --------------------------------------------------
    # Number extraction
    # --------------------------------------------------

    def _extract_expression(
        self,
        text: str
    ) -> Optional[str]:

        value = text.strip()

        # "calculate 25 * 45"
        match = re.search(
            r"(?:calculate|solve|evaluate)\s+(.+)",
            value,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

        # Pure expression.
        if re.fullmatch(
            r"[0-9a-zA-Z_+\-*/().,^= ]+",
            value
        ):
            return value

        return None

    # --------------------------------------------------
    # Basic expression
    # --------------------------------------------------

    def evaluate(
        self,
        expression: str
    ) -> str:

        expression = self._clean_expression(
            expression
        )

        try:

            parsed = self._parse_expression(
                expression
            )

            result = sp.simplify(
                parsed
            )

            return str(result)

        except Exception:

            return ""

    # --------------------------------------------------
    # Equation solver
    # --------------------------------------------------

    def solve_equation(
        self,
        expression: str
    ) -> str:

        expression = self._clean_expression(
            expression
        )

        if "=" not in expression:
            return ""

        left, right = expression.split(
            "=",
            1
        )

        try:

            equation = sp.Eq(
                self._parse_expression(left),
                self._parse_expression(right)
            )

            result = sp.solve(
                equation,
                self.x
            )

            if not result:

                # Try all free symbols.
                symbols = sorted(
                    equation.free_symbols,
                    key=lambda item:
                        str(item)
                )

                if symbols:

                    result = sp.solve(
                        equation,
                        symbols[0]
                    )

            return str(result)

        except Exception:

            return ""

    # --------------------------------------------------
    # Derivative
    # --------------------------------------------------

    def derivative(
        self,
        expression: str
    ) -> str:

        try:

            expression = (
                self._clean_expression(
                    expression
                )
            )

            result = sp.diff(
                self._parse_expression(expression),
                self.x
            )

            return str(
                sp.simplify(result)
            )

        except Exception:

            return ""

    # --------------------------------------------------
    # Integral
    # --------------------------------------------------

    def integral(
        self,
        expression: str
    ) -> str:

        try:

            expression = (
                self._clean_expression(
                    expression
                )
            )

            result = sp.integrate(
                self._parse_expression(expression),
                self.x
            )

            return str(result)

        except Exception:

            return ""

    # --------------------------------------------------
    # Limit
    # --------------------------------------------------

    def limit(
        self,
        expression: str
    ) -> str:

        try:

            expression = (
                self._clean_expression(
                    expression
                )
            )

            result = sp.limit(
                self._parse_expression(expression),
                self.x,
                0
            )

            return str(result)

        except Exception:

            return ""

    # --------------------------------------------------
    # Main solver
    # --------------------------------------------------

    def solve(
        self,
        question: str
    ) -> Optional[str]:

        text = question.strip()

        if not self.looks_like_math(
            text
        ):
            return None

        lowered = text.lower()

        # -------------------------------
        # Derivative
        # -------------------------------

        if (
            "derivative" in lowered
            or "differentiate" in lowered
        ):

            match = re.search(
                r"(?:of|differentiate)\s+(.+)",
                text,
                flags=re.IGNORECASE
            )

            expression = (
                match.group(1)
                if match
                else text
            )

            result = self.derivative(
                expression
            )

            if result:
                return (
                    f"Derivative:\n{result}"
                )

        # -------------------------------
        # Integral
        # -------------------------------

        if (
            "integral" in lowered
            or "integrate" in lowered
        ):

            match = re.search(
                r"(?:of|integrate)\s+(.+)",
                text,
                flags=re.IGNORECASE
            )

            expression = (
                match.group(1)
                if match
                else text
            )

            result = self.integral(
                expression
            )

            if result:
                return (
                    f"Integral:\n{result} + C"
                )

        # -------------------------------
        # Limit
        # -------------------------------

        if "limit" in lowered:

            match = re.search(
                r"limit\s+(.+)",
                text,
                flags=re.IGNORECASE
            )

            expression = (
                match.group(1)
                if match
                else text
            )

            result = self.limit(
                expression
            )

            if result:
                return (
                    f"Limit:\n{result}"
                )

        # -------------------------------
        # Equation
        # -------------------------------

        equation_text = re.sub(
            r"^solve\s+",
            "",
            text,
            flags=re.IGNORECASE
        )

        if "=" in equation_text:

            result = self.solve_equation(
                equation_text
            )

            if result:
                return (
                    f"Solution:\n{result}"
                )

        # -------------------------------
        # Expression
        # -------------------------------

        expression = (
            self._extract_expression(
                text
            )
        )

        if expression:

            result = self.evaluate(
                expression
            )

            if result:
                return (
                    f"Answer:\n{result}"
                )

        return None


universal_solver = UniversalSolver()