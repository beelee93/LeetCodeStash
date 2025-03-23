"""
Although the question only needs us to implement for plus and minus,
I went ahead to implement for plus, minus, times, divide and exponentiation
to demonstrate the concept of operator precedence
"""

from collections import namedtuple

Token = namedtuple('Token', ['token_type','value'])
Operator = namedtuple('Operator', ['symbol', 'left_assoc', 'precedence', 'calc'])


class Tokenizer(object):
    """
    Consumes a math expression as a string and generates a list of tokens
    """

    OP_PLUS = Operator('+', True, 1, lambda a,b: a+b)
    OP_MINUS = Operator('-', True, 1, lambda a,b: a-b)
    OP_TIMES = Operator('*', True, 2, lambda a,b: a*b)
    OP_DIVIDE = Operator('/', True, 2, lambda a,b: a/b)
    OP_EXPONENTIATION = Operator('^', False, 3, lambda a,b: a**b)
    OP_UNARY_MINUS = Operator('-', True, 4, lambda _,b: 0-b)
    OP_LPAREN = Operator('(', False, 0, None)
    OP_RPAREN = Operator(')', False, 0, None)
    NUMBER = Operator("1", False, 0, None)

    ARITHMETIC_OPERATORS = [OP_PLUS, OP_MINUS, OP_TIMES, OP_DIVIDE, OP_EXPONENTIATION]

    def __init__(self, expr):
        self.__expr = expr

    @property
    def expr_len(self):
        return len(self.__expr)
    
    def char_at(self, i):
        return self.__expr[i]
        
    def __iter__(self):
        self.__iter_index = 0
        self.__number_str = ""
        self.__prev_token = None
        return self
    
    @property
    def iter_index(self):
        return self.__iter_index
    
    def __next__(self):
        # We're gonna go through character by character, "yielding" whenever we find a valid token
        while self.__iter_index < self.expr_len:
            c = self.char_at(self.__iter_index)

            # When we encounter a non-numeric character and that we have a running number string,
            # it is time to yield our number string
            if not c.isnumeric() and self.__number_str != "":
                num = self.__number_str
                self.__number_str = ""
                self.__prev_token = Token(Tokenizer.NUMBER, num)
                return self.__prev_token
            
            # When we encounter a numeric character, we begin/resume building up the running number string
            if c.isnumeric():
                self.__number_str += c
                self.__iter_index += 1
                continue

            # Skip whitespaces
            if c == " ":
                self.__iter_index += 1
                continue

            # Unary minus has to be specially handled. We treat the `-` symbol as a unary operator if it is not following
            # a number or a right paranthesis.
            if c == Tokenizer.OP_UNARY_MINUS.symbol and (self.__prev_token is None or self.__prev_token.token_type not in [
                Tokenizer.NUMBER,
                Tokenizer.OP_RPAREN,
            ]):
                self.__iter_index += 1
                self.__prev_token = Token(Tokenizer.OP_UNARY_MINUS, c)
                return self.__prev_token

            # For all the arithmetic operators, we just yield the corresponding token once we match the symbol
            for op in Tokenizer.ARITHMETIC_OPERATORS:
                if c == op.symbol:
                    self.__iter_index += 1
                    self.__prev_token = Token(op, c)
                    return self.__prev_token

            if c == Tokenizer.OP_LPAREN.symbol:
                self.__iter_index += 1
                self.__prev_token = Token(Tokenizer.OP_LPAREN, c)
                return self.__prev_token

            if c == Tokenizer.OP_RPAREN.symbol:
                self.__iter_index += 1
                self.__prev_token = Token(Tokenizer.OP_RPAREN, c)
                return self.__prev_token

            raise ValueError(c)
        
        if self.__number_str != "":
            num = self.__number_str
            self.__number_str = ""
            self.__prev_token = Token(Tokenizer.NUMBER, num)
            return self.__prev_token

        raise StopIteration()


class OutputStack(object):
    """
    A simple stack that auto-evaluates when you push an operator.
    Once all operation are done, the top-most value should be the
    result of the calculation. If the expression is valid, there can
    only be exactly one value in the stack.
    """
    def __init__(self):
        self.__stack = []

    def append(self, v):
        if type(v) == int:
            self.__stack.append(v)
            return
        
        if type(v) != Operator:
            raise ValueError("Expected an operator")

        # By pushing an operator into the stack, we will
        # evaluate the operator using the existing operands in
        # the stack
        if v == Tokenizer.OP_UNARY_MINUS:
            right = self.__stack.pop()
            result = v.calc(0, right)
            self.__stack.append(result)
            return
        
        right = self.__stack.pop()
        left = self.__stack.pop()
        result = v.calc(left, right)
        self.__stack.append(result)
    
    @property
    def result(self):
        return self.__stack[-1]


class Solution(object):
    def calculate(self, s):
        """
        :type s: str
        :rtype: int
        """
        output_stack = OutputStack()
        operator_stack = []
        tokenizer = Tokenizer(s)

        for token in tokenizer:
            if token.token_type == Tokenizer.NUMBER:
                output_stack.append(int(token.value, 10))
                continue
            
            if token.token_type in (Tokenizer.ARITHMETIC_OPERATORS + [Tokenizer.OP_UNARY_MINUS]):
                # first, we check the operator stack. we should pop off all operators
                # that are of higher precedence or same precedence but left-associative; 
                # and put them into the output stack so that they are evaluated before
                # the current operator `token`.
                while len(operator_stack) > 0 and operator_stack[-1] != Tokenizer.OP_LPAREN and (
                    # prioritize greater precedence operator
                    operator_stack[-1].precedence > token.token_type.precedence or
                    # for same precedence, prioritize left-assoc operators
                    (operator_stack[-1].precedence == token.token_type.precedence and 
                    operator_stack[-1].left_assoc and token.token_type.left_assoc)
                ):
                    output_stack.append(operator_stack.pop())

                operator_stack.append(token.token_type)
                continue

            if token.token_type == Tokenizer.OP_LPAREN:
                operator_stack.append(Tokenizer.OP_LPAREN)
                continue

            if token.token_type == Tokenizer.OP_RPAREN:
                if len(operator_stack) == 0:
                    raise ValueError("mismatched parentheses")
                
                # all operators within a matching pair of parentheses need to be
                # evaluated with higher precedence, so we pop them off the operator
                # stack and into the output stack
                while operator_stack[-1] != Tokenizer.OP_LPAREN:
                    output_stack.append(operator_stack.pop())
                
                if operator_stack[-1] != Tokenizer.OP_LPAREN:
                    raise ValueError("mismatched parentheses")

                operator_stack.pop() # pop off the matching opening parenthesis "("
                continue

        # Once we finished consuming all tokens, we need to ensure we account for the
        # operators that are still in the operator stack
        while len(operator_stack) > 0:
            op = operator_stack.pop()
            if op == Tokenizer.OP_LPAREN:
                raise ValueError("mismatched parentheses")
            output_stack.append(op)

        return output_stack.result


if __name__ == "__main__":
    assert Solution().calculate("1 + 1") == 2
    assert Solution().calculate(" 2-1 + 2 ") == 3
    assert Solution().calculate("(1+(4+5+2)-3)+(6+8)") == 23
    assert Solution().calculate("1-(-2)") == 3
