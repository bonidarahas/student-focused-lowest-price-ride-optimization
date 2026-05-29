import ast
import operator


class CalculatorTool:
    """
    Safe calculator tool.

    Supports:
    +, -, *, /, **, %, and parentheses.
    """

    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
    }

    def run(self, expression: str) -> str:
        try:
            tree = ast.parse(expression, mode="eval")
            result = self._evaluate(tree.body)
            return str(result)

        except Exception as e:
            return f"Calculator error: {str(e)}"

    def _evaluate(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Only numbers are allowed.")

        if isinstance(node, ast.BinOp):
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)
            operator_type = type(node.op)

            if operator_type not in self.allowed_operators:
                raise ValueError("Operator not allowed.")

            return self.allowed_operators[operator_type](left, right)

        if isinstance(node, ast.UnaryOp):
            operand = self._evaluate(node.operand)
            operator_type = type(node.op)

            if operator_type not in self.allowed_operators:
                raise ValueError("Operator not allowed.")

            return self.allowed_operators[operator_type](operand)

        raise ValueError("Invalid expression.")