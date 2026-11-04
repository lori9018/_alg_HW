"""lambda_engine 的單元測試。

執行：
    python test_lambda.py
或
    python -m unittest test_lambda
"""

import sys
import unittest

from lambda_engine import (
    Abs,
    App,
    Var,
    church_numeral,
    evaluate,
    evaluate_program,
    free_vars,
    parse,
    reduce_with_trace,
    substitute,
    to_str,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def normal_form(source, **kwargs):
    """把字串解析、歸約到 normal form，回傳結果字串。"""
    return to_str(evaluate(parse(source), **kwargs)["result"])


class TestParser(unittest.TestCase):
    def test_variable(self):
        self.assertEqual(parse("x"), Var("x"))

    def test_application_is_left_associative(self):
        self.assertEqual(parse("f a b"), App(App(Var("f"), Var("a")), Var("b")))

    def test_abstraction(self):
        self.assertEqual(parse("\\x. x"), Abs("x", Var("x")))

    def test_multi_param_is_curried(self):
        self.assertEqual(parse("\\x y. x"), Abs("x", Abs("y", Var("x"))))

    def test_lambda_symbol(self):
        self.assertEqual(parse("λx. x"), Abs("x", Var("x")))

    def test_body_extends_right(self):
        # \x. x y  要解析成 \x. (x y)
        self.assertEqual(parse("\\x. x y"), Abs("x", App(Var("x"), Var("y"))))

    def test_parentheses(self):
        self.assertEqual(parse("f (a b)"), App(Var("f"), App(Var("a"), Var("b"))))

    def test_roundtrip_pretty(self):
        for src in ["\\x. x", "f a b", "\\f. \\x. f (f x)", "(\\x. x) y"]:
            self.assertEqual(to_str(parse(src)), src)


class TestChurchNumeral(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(to_str(church_numeral(0)), "\\f. \\x. x")

    def test_three(self):
        self.assertEqual(to_str(parse("3")), "\\f. \\x. f (f (f x))")


class TestSubstitution(unittest.TestCase):
    def test_simple(self):
        result = substitute(parse("x y"), "x", Var("a"))
        self.assertEqual(to_str(result), "a y")

    def test_shadowing(self):
        # \x. x 裡面的 x 被綁定，不該被代換
        result = substitute(parse("\\x. x"), "x", Var("a"))
        self.assertEqual(to_str(result), "\\x. x")

    def test_capture_avoidance(self):
        # (\x. \y. x) y  ->  \y'. y   （y 不能被 \y 捕獲）
        result = substitute(parse("\\y. x"), "x", Var("y"))
        self.assertEqual(to_str(result), "\\y'. y")


class TestFreeVars(unittest.TestCase):
    def test_free(self):
        self.assertEqual(free_vars(parse("\\x. x y")), {"y"})

    def test_closed(self):
        self.assertEqual(free_vars(parse("\\x. x")), set())


class TestReduction(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(normal_form("(\\x. x) y"), "y")

    def test_constant(self):
        self.assertEqual(normal_form("(\\x. \\y. x) a b"), "a")

    def test_normal_order_is_outermost_first(self):
        trace = reduce_with_trace(parse("(\\x. x) ((\\y. y) z)"))
        self.assertEqual(trace["steps"][1], "(\\y. y) z")
        self.assertEqual(trace["steps"][2], "z")

    def test_church_plus(self):
        program = """
            plus = \\m. \\n. \\f. \\x. m f (n f x)
            plus 2 3
        """
        self.assertEqual(to_str(evaluate_program(program)[0]["result"]),
                         to_str(church_numeral(5)))

    def test_church_mult(self):
        program = """
            mult = \\m. \\n. \\f. m (n f)
            mult 2 3
        """
        self.assertEqual(to_str(evaluate_program(program)[0]["result"]),
                         to_str(church_numeral(6)))


class TestExamples(unittest.TestCase):
    def test_factorial(self):
        with open("examples/factorial.lam", encoding="utf-8") as handle:
            trace = evaluate_program(handle.read())[0]
        # 3! = 6
        self.assertEqual(to_str(trace["result"]), to_str(church_numeral(6)))
        self.assertFalse(trace["truncated"])

    def test_fibonacci(self):
        with open("examples/fibonacci.lam", encoding="utf-8") as handle:
            trace = evaluate_program(handle.read())[0]
        # fib(4) = 3
        self.assertEqual(to_str(trace["result"]), to_str(church_numeral(3)))
        self.assertFalse(trace["truncated"])


class TestLimits(unittest.TestCase):
    def test_max_steps(self):
        # Omega = (\x. x x) (\x. x x)，永遠不會停；靠 max_steps 截斷
        trace = evaluate(parse("(\\x. x x) (\\x. x x)"), max_steps=20)
        self.assertTrue(trace["truncated"])
        self.assertEqual(trace["count"], 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
