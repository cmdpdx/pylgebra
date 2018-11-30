from operations import *
from term import Term
from tokenlist import TokenList, OPERATORS


# Grammar rules
# expression        -> addition ;
# addition          -> multiplication ( ("-" | "+") multiplication )* ;
# multiplication    -> unary ( ("/" | "*") unary )* ;
# unary             -> ("-") unary | power ;
# power             -> primary "^" unary | primary ;
# primary           -> ( NUMBER )*  ( STRING )* | "(" expression ")" ;
# term              -> 
class Parser(object):
    def __init__(self, equation):
        self.tokens = TokenList(equation).tokenize()
        self.current = 0

    def expression(self):
        return self.addition()

    def addition(self):
        expr = self.multiplication()
        while self.match(PLUS, MINUS):
            operator = self.previous()
            right = self.multiplication()
            if operator == PLUS: expr = ADD(expr, right)
            else: expr = SUB(expr, right)
        return expr  
    
    def multiplication(self):
        expr = self.unary()
        while self.match(STAR, SLASH):
            operator = self.previous()
            right = self.unary()
            if operator == STAR: expr = MULT(expr, right)
            else: expr = DIV(expr, right)
        return expr

    def unary(self):
        if self.match(MINUS):
            right = self.unary()
            return MULT(-1, right)
        return power()

    def power(self):
        expr = self.primary()
        if self.match(POWER):
            exponent = self.advance()
            expr = POW(expr, exponent)
        return expr

    def primary(self):
        if self.match(NUMBER):
    
    def match(self, *symbols):
        for symbol in symbols:
            if self.check(symbol):
                self.advance()
                return True
        return False
    
    def check(self, symbol):
        if self.is_at_end(): return False
        return self.peek()  == symbol

    def advance(self):
        if not self.is_at_end():
            current += 1
        return self.previous()
    
    def is_at_end(self):
        return self.current == self.tokens.length

    def peek(self):
        return self.tokens.get(self.current)

    def previous(self):
        return self.tokens.get(self.current - 1)
    


    