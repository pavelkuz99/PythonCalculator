import unittest
from parameterized import parameterized, parameterized_class
import sys
from final_task.calculator import pycalc
import math


class TestMathOperationsHandler(unittest.TestCase):
    def setUp(self):
        self.math_operations = pycalc.MathOperationsHandler()

    def test_add_unary_minus(self):
        self.assertEqual(self.math_operations.add_unary_minus(5), -5)
        self.assertEqual(self.math_operations.add_unary_minus(-5.6), 5.6)
        self.assertEqual(self.math_operations.add_unary_minus(-.8), 0.8)

    def test_add_unary_plus(self):
        self.assertEqual(self.math_operations.add_unary_plus(6), 6)
        self.assertEqual(self.math_operations.add_unary_plus(-5.5), -5.5)

    def test_factorial(self):
        with self.assertRaises(ValueError):
            self.math_operations.factorial(6.66)
        with self.assertRaises(ValueError):
            self.math_operations.factorial(-13)
        self.assertEqual(self.math_operations.factorial(5), 120)
        self.assertEqual(self.math_operations.factorial(0), 1)

    def test_logarithm(self):
        self.assertEqual(self.math_operations.logarithm(8, 2), math.log(8, 2))
        with self.assertRaises(ZeroDivisionError):
            self.math_operations.logarithm(8, 1)
        with self.assertRaises(ValueError):
            self.math_operations.logarithm(-8, -2)

    def test_logarithm_by_e(self):
        self.assertEqual(self.math_operations.logarithm_by_e(13), math.log(13))
        with self.assertRaises(ValueError):
            self.math_operations.logarithm_by_e(-20)

    def test_logarithm_by_two(self):
        self.assertEqual(self.math_operations.logarithm_by_two(8), math.log2(8))
        with self.assertRaises(ValueError):
            self.math_operations.logarithm_by_two(-666)

    def test_logarithm_by_ten(self):
        self.assertEqual(self.math_operations.logarithm_by_ten(8), math.log10(8))
        with self.assertRaises(ValueError):
            self.math_operations.logarithm_by_ten(-666)

    def test_power(self):
        for i in range(-5, 5):
            with self.subTest(i=i):
                self.assertEqual(self.math_operations.power(i, 2), math.pow(i, 2))
        with self.assertRaises(ValueError):
            self.math_operations.power(-6.66, .28)

    def test_square_root(self):
        self.assertEqual(self.math_operations.square_root(16), math.sqrt(16))
        self.assertEqual(self.math_operations.square_root(101.1), math.sqrt(101.1))
        with self.assertRaises(ValueError):
            self.math_operations.square_root(-2)

    def test_divide(self):
        self.assertEqual(self.math_operations.divide(18, -2.5), 18 / -2.5)
        with self.assertRaises(ZeroDivisionError):
            self.math_operations.divide(-2, 0)

    def test_int_divide(self):
        self.assertEqual(self.math_operations.int_divide(1813, 22), 1813 // 22)
        with self.assertRaises(ZeroDivisionError):
            self.math_operations.int_divide(-2, 0)

    def test_division_rest(self):
        self.assertEqual(self.math_operations.get_rest_of_division(131, 0.8), 131 % 0.8)
        with self.assertRaises(ZeroDivisionError):
            self.math_operations.get_rest_of_division(13, 0)

    @unittest.expectedFailure
    def test_fail_is_number(self):
        self.assertTrue(self.math_operations.is_number('hello'))

    def test_is_number(self):
        self.assertEqual(self.math_operations.is_number('.3'), True)
        self.assertEqual(self.math_operations.is_number('11.8'), True)
        self.assertEqual(self.math_operations.is_number('a'), False)
        self.assertEqual(self.math_operations.is_number('sin'), False)


class TestExpressionResolver(unittest.TestCase):
    def setUp(self):
        self.resolver = pycalc.ExpressionResolver()

    # some issue with (3)(10+1) kind of expression
    @parameterized.expand([
        ('2 ( 10 + 1 )'.split(), '2 * ( 10 + 1 )'.split()),
        ('8 sin ( 10 + 1 )'.split(), '8 * sin ( 10 + 1 )'.split()),
        ('e pi'.split(), 'e * pi'.split()),
        ('( 3 ) 10'.split(), '( 3 ) * 10'.split()),
        ('6 pi'.split(), '6 * pi'.split()),
    ])
    def test_resolve_implicit_multiplication(self, expression, expected):
        self.assertEqual(self.resolver.resolve_implicit_multiplication(expression), expected)

    @parameterized.expand([
        ('log ( 8 , 2 )'.split(), 'log ( 8 , 2 )'.split()),
        ('log ( 8 )'.split(), 'ln ( 8 )'.split()),
    ])
    def test_resolve_log(self, expression, expected):
        self.assertEqual(self.resolver.resolve_log(expression), expected)

    @parameterized.expand([
        ('+ 13'.split(), 'plus 13'.split()),
        ('- sin ( pi )'.split(), 'minus sin ( pi )'.split()),
    ])
    def test_resolve_unary(self, expression, expected):
        self.assertEqual(self.resolver.resolve_unary(expression), expected)

    def test_resolve_double_const(self):
        self.assertEqual(self.resolver.resolve_double_const('epi + pitau'), 'e pi + pi tau')


class TestRPNConverter(unittest.TestCase):
    def setUp(self):
        self.converter = pycalc.ReversePolishNotationConverter()

    @parameterized.expand([
        ('3+2-log(8,2)', ['3', '+', '2', '-', 'log', '(', '8', ',', '2', ')']),
        ('sin(pi/2)', ['sin', '(', 'pi', '/', '2', ')']),
    ])
    def test_create_tokens_list(self, expression, expected):
        self.assertEqual(self.converter.create_tokens_list(expression), expected)

    def test_convert_to_rpn(self):
        self.assertEqual(self.converter.convert_to_rpn('-sin(pi/2)'), ['pi', '2', '/', 'sin', 'minus'])
        with self.assertRaises(pycalc.UnknownFunctionError):
            self.converter.convert_to_rpn('sen(pi/2)')

    def test_clear_stack(self):
        self.converter.stack = ['1', '3', '+']
        self.converter.clear_stack()
        self.assertEqual(self.converter.stack, [])


# class TestRPN(TestCase):

#
#
#
#     def test_pop_one(self):
#         self.rpn.stack = [1, 2, 3, 4]
#         self.assertEqual(self.rpn.pop_one(), 4)
#
#     def test_pop_two(self):
#         self.rpn.stack = [1, 2, 3, 4]
#         self.assertEqual(self.rpn.pop_one(), 4, 3)
#
#     def test_handle_operations(self):
#         expression1 = '3 + 2 1'
#         rpn_expression1 = self.rpn.convert_to_rpn(expression1)
#         with self.assertRaises(pycalc.RedundantParameterError):
#             self.rpn.handle_operations(rpn_expression1)
#
#
# class TestCheck(TestCase):
#     def setUp(self):
#         self.rpn = pycalc.RPN()
#         self.check = pycalc.Check()
#
#     def test_check_for_numbers(self):
#         expression1 = 'sin+cos'
#         expression2 = '3+2'
#         with self.assertRaises(pycalc.MissingParameterError):
#             self.check.check_for_numbers(expression1)
#         self.check.check_for_numbers(expression2)
#
#     def test_check_parentheses(self):
#         expression1 = '8*(3+2))'
#         expression2 = '(8*(3+2))'
#         expression3 = '(8*(3+2)'
#         with self.assertRaises(pycalc.UnbalancedParenthesesError):
#             self.check.check_parentheses(expression1)
#         self.check.check_parentheses(expression2)
#         with self.assertRaises(pycalc.UnbalancedParenthesesError):
#             self.check.check_parentheses(expression3)
#
#     def test_check_for_symbols(self):
#         expression1 = '8#(3+2))'
#         expression2 = '8+(3~2))'
#         expression3 = '3 + 2'
#         with self.assertRaises(pycalc.UnknownSymbolError):
#             self.check.check_for_symbols(expression1)
#         with self.assertRaises(pycalc.UnknownSymbolError):
#             self.check.check_for_symbols(expression2)
#         self.check.check_for_symbols(expression3)
#
#     def test_check_spaces(self):
#         expression1 = '1 2'
#         expression2 = '8 > =  7'
#         expression3 = '11 + sin(13)'
#         expression4 = '5 / / 88'
#         expression5 = '(88) .3'
#         with self.assertRaises(pycalc.UnexpectedSpaceError):
#             self.check.check_spaces(expression1)
#         with self.assertRaises(pycalc.UnexpectedSpaceError):
#             self.check.check_spaces(expression2)
#         self.check.check_spaces(expression3)
#         with self.assertRaises(pycalc.UnexpectedSpaceError):
#             self.check.check_spaces(expression4)
#         with self.assertRaises(pycalc.UnexpectedSpaceError):
#             self.check.check_spaces(expression5)


if __name__ == '__main__':
    unittest.main()
