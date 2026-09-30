import unittest

from backend.universal_solver import UniversalSolver


class UniversalSolverTests(unittest.TestCase):
    def setUp(self):
        self.solver = UniversalSolver()

    def test_calculates_arithmetic(self):
        self.assertEqual(
            self.solver.solve("calculate 2 + 3 * 4"),
            "Answer:\n14"
        )

    def test_solves_equation(self):
        self.assertEqual(
            self.solver.solve("solve x + 2 = 5"),
            "Solution:\n[3]"
        )

    def test_differentiates_expression(self):
        self.assertEqual(
            self.solver.solve("differentiate x^2"),
            "Derivative:\n2*x"
        )

    def test_rejects_python_execution(self):
        self.assertIsNone(
            self.solver.solve(
                "calculate __import__('os').getcwd()"
            )
        )


if __name__ == "__main__":
    unittest.main()