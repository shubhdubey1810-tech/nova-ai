# NØVA AI 1.0
# Tool System

import ast
import operator
from pathlib import Path
from datetime import datetime


class NovaTools:

    def __init__(self):
        self.name = "NØVA Tools"
        self.version = "1.0.0"

    # --------------------------------------------------
    # Calculator
    # --------------------------------------------------

    def calculate(self, expression):
        """Safely calculate basic mathematical expressions."""

        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
        }

        def evaluate(node):

            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError("Invalid value")

            if isinstance(node, ast.BinOp):
                operation = allowed_operators.get(type(node.op))

                if operation is None:
                    raise ValueError("Operator not allowed")

                return operation(
                    evaluate(node.left),
                    evaluate(node.right)
                )

            if isinstance(node, ast.UnaryOp):
                operation = allowed_operators.get(type(node.op))

                if operation is None:
                    raise ValueError("Operator not allowed")

                return operation(evaluate(node.operand))

            raise ValueError("Invalid expression")

        try:
            tree = ast.parse(expression, mode="eval")
            result = evaluate(tree.body)
            return str(result)

        except Exception:
            return "I couldn't calculate that expression."

    # --------------------------------------------------
    # Current Time
    # --------------------------------------------------

    def get_time(self):
        """Get the current local time."""

        return datetime.now().strftime("%I:%M:%S %p")

    # --------------------------------------------------
    # List Files
    # --------------------------------------------------

    def list_files(self, folder="."):
        """List files and folders."""

        try:
            path = Path(folder)

            if not path.exists():
                return ["Folder does not exist."]

            return [
                item.name
                for item in path.iterdir()
            ]

        except PermissionError:
            return ["Permission denied."]

    # --------------------------------------------------
    # Read Text File
    # --------------------------------------------------

    def read_file(self, filename):
        """Read a text file."""

        try:
            path = Path(filename)

            if not path.exists():
                return "File does not exist."

            if not path.is_file():
                return "This is not a file."

            return path.read_text(encoding="utf-8")

        except PermissionError:
            return "Permission denied."

        except Exception as error:
            return f"Could not read file: {error}"

    # --------------------------------------------------
    # Create Text File
    # --------------------------------------------------

    def create_file(self, filename, content=""):
        """Create a text file."""

        try:
            path = Path(filename)

            path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            path.write_text(
                content,
                encoding="utf-8"
            )

            return f"File created: {path}"

        except PermissionError:
            return "Permission denied."

        except Exception as error:
            return f"Could not create file: {error}"

    # --------------------------------------------------
    # System Information
    # --------------------------------------------------

    def system_info(self):
        """Return basic NØVA information."""

        return {
            "name": "NØVA AI",
            "version": "1.0.0",
            "tool_engine": self.version
        }


# Create global tool manager
nova_tools = NovaTools()


# ------------------------------------------------------
# Simple tool interface
# ------------------------------------------------------

def use_tool(tool_name, *args):

    if tool_name == "calculate":
        return nova_tools.calculate(*args)

    if tool_name == "time":
        return nova_tools.get_time()

    if tool_name == "list_files":
        return nova_tools.list_files(*args)

    if tool_name == "read_file":
        return nova_tools.read_file(*args)

    if tool_name == "create_file":
        return nova_tools.create_file(*args)

    if tool_name == "system_info":
        return nova_tools.system_info()

    return f"Unknown tool: {tool_name}"


# ------------------------------------------------------
# Test
# ------------------------------------------------------

if __name__ == "__main__":

    print("NØVA Tool System 1.0")
    print()

    print("Calculator:")
    print(use_tool("calculate", "25 * 4"))

    print()
    print("Time:")
    print(use_tool("time"))

    print()
    print("System:")
    print(use_tool("system_info"))