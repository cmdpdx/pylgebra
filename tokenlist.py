PLUS = "+"
MINUS = "-"
STAR = "*"
SLASH = "/"
LEFT_PAREN = "("
RIGHT_PAREN = ")"
POWER = "^"
OPERATORS = (PLUS, MINUS, STAR, SLASH, LEFT_PAREN, RIGHT_PAREN, POWER) 
NUMBER = "number"
VARIABLE = "variable"

class TokenList(object):
    def __init__(self, equation):
        self.tokens = []
        self.equation = equation

    def _err(self, equation, msg):
        self.tokens.clear()
        raise ValueError(" ".join((equation, "not formatted correctly >>", msg)))

    def tokenize(self):
        self.equation = self.equation.replace(" ", "")
        self.tokens.clear()
        index = 0
        while index < len(self.equation):
            char = self.equation[index]
            if char in OPERATORS or char.isalpha():
                self.tokens.append(char)
                index += 1
            elif char.isdigit():
                index = self._consume_real(index)
            else:
                self._err(self.equation, "unrecognized character: " + char)

    def _consume_real(self, index):
        decimal = False
        digits = []
        while index < len(self.equation): 
            char = self.equation[index]
            if not char.isdecimal() and char != ".": break
            if char == "." and decimal: 
                self._err(self.equation, "too many decimal points in number")
            elif char == ".": 
                decimal = True
            digits.append(char)
            index += 1

        self.tokens.append("".join(digits))
        return index

    def get(self, index):
        return self.tokens[index]

    @property
    def length(self):
        return len(self.tokens)

