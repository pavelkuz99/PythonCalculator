from re import compile
from io import StringIO
from tokenize import generate_tokens
import math
from argparse import ArgumentParser
from numbers import Number
from collections import namedtuple


class UnbalancedParenthesesError(Exception):
    def __init__(self, message):
        super(UnbalancedParenthesesError, self).__init__(message)


class UnknownFunctionError(Exception):
    def __init__(self, message):
        super(UnknownFunctionError, self).__init__(message)


class RedundantParameterError(Exception):
    def __init__(self, message):
        super(RedundantParameterError, self).__init__(message)


class MissingParameterError(Exception):
    def __init__(self, message):
        super(MissingParameterError, self).__init__(message)


class UnknownSymbolError(Exception):
    def __init__(self, message):
        super(UnknownSymbolError, self).__init__(message)


class UnexpectedSpaceError(Exception):
    def __init__(self, message):
        super(UnexpectedSpaceError, self).__init__(message)


class MathOperationsHandler:
    """
    Customized operations from math module with error handling
    """

    @staticmethod
    def add_unary_minus(digit):
        return (-1) * digit

    @staticmethod
    def add_unary_plus(digit):
        return digit

    @staticmethod
    def factorial(digit):
        if digit < 0:
            raise ValueError('can\'t count factorial of negative number')
        elif not str(digit).isdigit():
            raise ValueError('can\'t count factorial of fractional number')
        else:
            return math.factorial(digit)

    @staticmethod
    def logarithm(digit, base):
        if base == 1:
            raise ZeroDivisionError('cant\'t count logarithm by base 1')
        elif digit <= 0:
            raise ValueError('can\'t count logarithm of non-positive digit')
        else:
            return math.log(digit, base)

    @staticmethod
    def logarithm_by_e(digit):
        if digit > 0:
            return math.log(digit)
        else:
            raise ValueError('can\'t count non-positive logarithm')

    @staticmethod
    def logarithm_by_two(digit):
        if digit > 0:
            return math.log2(digit)
        else:
            raise ValueError('can\'t count logarithm of non-positive digit by base 2')

    @staticmethod
    def logarithm_by_ten(digit):
        if digit > 0:
            return math.log10(digit)
        else:
            raise ValueError('can\'t count logarithm of non-positive number by base 10')

    @staticmethod
    def power(digit, base):
        if digit < 0 and not float(base).is_integer():
            raise ValueError('can\'t raise negative number to fractional power')
        else:
            return pow(digit, base)

    @staticmethod
    def square_root(digit):
        if digit >= 0:
            return math.sqrt(digit)
        else:
            raise ValueError('can\'t count square root of negative number')

    @staticmethod
    def divide(digit, base):
        if base == 0:
            raise ZeroDivisionError('can\'t divide by zero')
        else:
            return digit / base

    @staticmethod
    def int_divide(digit, base):
        if base == 0:
            raise ZeroDivisionError('can\'t divide by zero')
        else:
            return digit // base

    @staticmethod
    def get_rest_of_division(digit, base):
        if base == 0:
            raise ZeroDivisionError('can\'t divide by zero')
        else:
            return digit % base

    @staticmethod
    def is_number(item):
        try:
            float(item)
            return True
        except (ValueError, TypeError):
            pass
        return False


class MathModuleData(MathOperationsHandler):
    def __init__(self):
        self.__postfix_operations = {'!': super().factorial}
        self.__prefix_operations = {a: getattr(math, a) for a in dir(math) if callable(getattr(math, a))}
        custom_prefix_operations = {
            'log': super().logarithm,
            'log2': super().logarithm_by_two,
            'log10': super().logarithm_by_ten,
            'pow': super().power,
            'sqrt': super().square_root,
            'ln': super().logarithm_by_e,
            'abs': abs,
            'round': round,
            'minus': super().add_unary_minus,
            'plus': super().add_unary_plus,
        }
        self.__prefix_operations.update(custom_prefix_operations)
        operation = namedtuple('operation', 'priority action')
        self.__one_sign_operations = {
            '^': operation(4, super().power),
            '**': operation(4, super().power),
            '/': operation(3, super().divide),
            '//': operation(3, super().int_divide),
            '%': operation(3, super().get_rest_of_division),
            '*': operation(3, lambda digit, base: digit * base),
            '+': operation(2, lambda digit, base: digit + base),
            '-': operation(2, lambda digit, base: digit - base),
            '(': operation(1, None),
            ')': operation(1, None),
            '<': operation(0, lambda digit, base: digit < base),
            '<=': operation(0, lambda digit, base: digit <= base),
            '=': operation(0, lambda digit, base: digit == base),
            '==': operation(0, lambda digit, base: digit == base),
            '!=': operation(0, lambda digit, base: digit != base),
            '>=': operation(0, lambda digit, base: digit >= base),
            '>': operation(0, lambda digit, base: digit > base)
        }
        self.__CONSTANTS = {attr: getattr(math, attr) for attr in dir(math)
                            if isinstance(getattr(math, attr), Number)}
        self.__all_operations = {**self.__postfix_operations, **self.__prefix_operations, **self.__one_sign_operations}

    def get_postfix_operations(self):
        return self.__postfix_operations

    def get_prefix_operations(self):
        return self.__prefix_operations

    def get_one_sign_operations(self):
        return self.__one_sign_operations

    def get_constants(self):
        return self.__CONSTANTS

    def get_all_operations(self):
        return self.__all_operations


class ExpressionResolver(MathModuleData):
    """
    Resolves implicit multiplication, unary signs and double constants standing together
    """

    # maybe it is better to use regular expression for this case

    def __init__(self):
        super().__init__()

    def resolve_implicit_multiplication(self, tokens_list):
        """
        Resolves implicit multiplication to the new tokens list
        Returns resolved list
        """

        result = []

        def add_multiplication_sign():
            result.append('*')
            result.append(token)

        for index, token in enumerate(tokens_list):
            previous = tokens_list[index - 1]
            if index == 0:
                result.append(token)
            elif (token in super().get_prefix_operations() and super().is_number(previous)
                  or token in super().get_constants() and super().is_number(previous)
                  or token in super().get_constants() and previous in super().get_constants()
                  or token in super().get_prefix_operations() and previous == ')'
                  or super().is_number(token) and previous == ')'
                  or token == '(' and super().is_number(previous)):
                add_multiplication_sign()
            else:
                result.append(token)
        return result

    def resolve_log(self, tokens_list):
        """
        If log() takes two parameter leaves it the same
        If log() takes one parameter changes log() to ln() in place
        """
        open_parentheses_count = 0
        close_parentheses_count = 0
        for index, token in enumerate(tokens_list):
            if token == 'log':
                number_of_arguments = 1
                for character in tokens_list[index + 1:]:
                    if character == '(':
                        open_parentheses_count += 1
                    elif character == ',':
                        number_of_arguments = 2
                    elif character == ')':
                        close_parentheses_count += 1
                    if open_parentheses_count == close_parentheses_count:
                        break
                if number_of_arguments == 1:
                    tokens_list[index] = 'ln'
        return tokens_list

    def resolve_unary(self, tokens_list):
        """
        Resolves all unary '-' and '+' operations changing them to 'minus' and 'plus' functions
        Returns resolved list
        """
        result = []
        for index, token in enumerate(tokens_list):
            previous = tokens_list[index - 1]
            if token == '-' or token == '+':
                if index == 0:
                    result.append('minus') if token == '-' else result.append('plus')
                elif previous == ')' or previous in super().get_constants() or super().is_number(previous):
                    result.append(token)
                else:
                    result.append('minus') if token == '-' else result.append('plus')
            else:
                result.append(token)
        return result

    def resolve_double_const(self, expression):
        """
        Resolves constant values standing together
        """
        for first_const in list(super().get_constants().keys()):
            for second_const in list(super().get_constants().keys()):
                expression = expression.replace(f'{first_const}{second_const}', f'{first_const} {second_const}')
        return expression


class ReversePolishNotationConverter(MathModuleData):
    """
    Converter of math expression to ReversePolishNotation (RPN) expression
    """

    def __init__(self):
        super().__init__()
        self.stack, self.output, self.tokens = [], [], []
        self.resolver = ExpressionResolver()

    def clear_stack(self):
        self.stack = []

    def check_for_numbers(self, list_of_tokens):
        """
        Checks whether expression has no operands
        """
        numbers_count = 0
        for token in list_of_tokens:
            if super().is_number(token) or token in super().get_constants():
                numbers_count += 1
        if numbers_count == 0:
            raise MissingParameterError('no numbers or constants in expression')

    @staticmethod
    def create_tokens_list(expression):
        """
        Creates tokens list from math expressions string
        """
        line = generate_tokens(StringIO(expression).readline)
        return [token[1] for token in line if token[1]]

    def resolve_math_expression(self, expression):
        expression = self.resolver.resolve_double_const(expression)
        tokens = self.create_tokens_list(expression)
        tokens = self.resolver.resolve_log(tokens)
        tokens = self.resolver.resolve_unary(tokens)
        self.check_for_numbers(tokens)
        self.tokens = self.resolver.resolve_implicit_multiplication(tokens)

    def convert_to_rpn(self, expression):
        """
        Converts initial math expression to Reverse Polish Notation
        Returns tokens list in Reverse Polish Notation
        """

        self.resolve_math_expression(expression)

        for item in self.tokens:
            if super().is_number(item) or item in super().get_postfix_operations() \
                    or item in super().get_constants():
                self.output.append(item)
            elif item == '(' or item in super().get_prefix_operations():
                self.stack.append(item)
            elif item == ')':
                for element in reversed(self.stack):
                    if element != '(':
                        self.output.append(self.stack.pop())
                    else:
                        self.stack.pop()
                        break
            elif item in super().get_one_sign_operations():
                for element in reversed(self.stack):
                    if self.stack[-1] in super().get_prefix_operations() \
                            or super().get_one_sign_operations()[self.stack[-1]].priority \
                            > self.get_one_sign_operations()[item].priority \
                            or super().get_one_sign_operations()[self.stack[-1]].priority \
                            == super().get_one_sign_operations()[item].priority and item != '^':
                        self.output.append(self.stack.pop())
                self.stack.append(item)
            elif item == ',':
                for element in reversed(self.stack):
                    if element != '(':
                        self.output.append(self.stack.pop())
                    else:
                        break
            else:
                raise UnknownFunctionError(f'wrong operation "{item}"')
        for element in reversed(self.stack):
            self.output.append(self.stack.pop())
        self.clear_stack()
        return list(self.output)


class ReversePolishNotationHandler(MathModuleData):
    """
    Handles PRN expression
    """

    def __init__(self):
        super().__init__()
        self.stack = []

    def pop_one(self):
        return float(self.stack.pop())

    def pop_two(self):
        y = float(self.stack.pop())
        x = float(self.stack.pop())
        return x, y

    def handle_operations(self, rpn_tokens):
        """
        Handles all operations in Reverse Polish Notation tokens list
        Return result of calculation
        """
        for token in rpn_tokens:
            if token in super().get_constants():
                self.stack.append(super().get_constants()[token])
            elif token not in super().get_all_operations():
                self.stack.append(token)
            elif token in super().get_one_sign_operations():
                try:
                    function = super().get_one_sign_operations()[token].action
                    x, y = self.pop_two()
                    self.stack.append(function(x, y))
                except IndexError:
                    raise MissingParameterError(f'not enough operands for "{token}" operation')
            elif token in super().get_prefix_operations() or super().get_postfix_operations():
                try:
                    if token in ('fmod', 'gcd', 'isclose', 'ldexp', 'remainder', 'log', 'pow', 'atan2'):
                        function = super().get_all_operations()[token]
                        x, y = self.pop_two()
                        self.stack.append(function(x, y))
                    else:
                        function = super().get_all_operations()[token]
                        self.stack.append(function(self.pop_one()))
                except IndexError:
                    raise MissingParameterError(f'not enough operands for "{token}" operation')
        if len(self.stack) > 1:
            raise RedundantParameterError('function takes more parameters that it should')
        return self.stack[0]


class ErrorChecker:
    """
    Class has methods for initial error check of math expression
    """

    @staticmethod
    def check_parentheses(expression):
        """
        Checks whether parentheses are balanced
        """
        n = abs(expression.count('(') - expression.count(')'))
        if expression.count('(') > expression.count(')'):
            raise UnbalancedParenthesesError(f'expression has {n} unclosed parentheses')
        elif expression.count('(') < expression.count(')'):
            raise UnbalancedParenthesesError(f'expression has {n} redundant closing parentheses')
        if n == 0:
            pass

    @staticmethod
    def check_for_symbols(expression):
        """
        Checks whether unsupported symbols are in the string
        """
        regex = compile('[;@_#$&?|}{~":]')
        if regex.search(expression):
            raise UnknownSymbolError(f'unknown symbols "{regex.search(expression).group()}"')
        else:
            pass

    @staticmethod
    def check_spaces(expression):
        """
        Checks whether unexpected spaces are in the string
        """
        for index, character in enumerate(expression):
            try:
                nxt = expression[index + 1]
                previous = expression[index - 1]
                if character == ' ':
                    if nxt.isdigit() and previous.isdigit():
                        raise UnexpectedSpaceError('unexpected space between numbers')
                    elif nxt == ' ' or previous == ' ':
                        raise UnexpectedSpaceError('unexpected double space')
                    elif nxt == '.' and previous.isdigit() or nxt.isdigit() and previous == '.':
                        raise UnexpectedSpaceError('unexpected space between/or in fractional numbers')
                    elif nxt in '<>=!' and previous in '<>=!':
                        raise UnexpectedSpaceError(f'unexpected space in comparison operation {previous + nxt}')
                    elif nxt in '*/^' and previous in '*/^':
                        raise UnexpectedSpaceError(f'unexpected space in operation {previous + nxt}')
                    elif previous == '(' and nxt == ')':
                        raise UnexpectedSpaceError('unexpected empty parentheses')
                    elif previous == ')' and nxt == '.':
                        raise UnexpectedSpaceError('unexpected fractional number after ")"')
            except IndexError:
                pass


class Calculator(ReversePolishNotationConverter, ReversePolishNotationHandler):
    """
    Main calculator class
    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def parse_expression():
        """
        Creates command-line arguments parser
        Returns parsed argument
        """
        parser = ArgumentParser(description='Pure Python command-line calculator')
        parser.add_argument('EXPRESSION', help='expression string to evaluate', action='store_true')
        parsed, args = parser.parse_known_args()
        return args[0]

    def calculate(self):
        math_expression = self.parse_expression()
        ErrorChecker.check_for_symbols(math_expression)
        ErrorChecker.check_parentheses(math_expression)
        ErrorChecker.check_spaces(math_expression)
        rpn_expression = super().convert_to_rpn(math_expression)
        return super().handle_operations(rpn_expression)


def main():
    try:
        calculator = Calculator()
        print(calculator.calculate())
    except Exception as e:
        print(f'ERROR: {e}')


if __name__ == "__main__":
    main()
