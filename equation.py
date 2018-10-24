from operations import *
from term import Variable, Term, _is_a


class EquationError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

class Equation(object):
    def __init__(self, variables, left=None, right=None, eqn_str=None):
        if (left is None and right is not None) or (right is None and left is not None):
            raise EquationError("both left and right sides of equation must be provided")
        # initialize using the given left and right sides
        if left is not None and right is not None:
            if not _is_a(left, Term, OPERATION) or not _is_a(right, Term, OPERATION):
                raise TypeError("left and right must be a Term or operation")
            self.left = left
            self.right = right
        elif eqn_str is not None:
            # TODO: parse string
            print("parse string \"{}\" here...".format(eqn_str))
            self.left = None
            self.right = None
        else:
            raise EquationError("must provide either left and right, or eqn_str")
        
        if _is_a(variables, Variable):
            self.variables = [variables]
        elif _is_a(variables, list):
            self.variables = []
            for var in variables:
                if not _is_a(var, Variable): raise TypeError("variables must be of type Variable")
                self.variables.append(var)
        else:
            raise TypeError("variables must be of type Variable")

    def simplify(self):
        if not _is_a(self.left, Term): 
            self.left.simplify()
            self.left = self.left.value

        if not _is_a(self.right, Term): 
            self.right.simplify()
            self.right = self.right.value

    def __str__(self):
        return "{} = {} | for {}".format(self.left, self.right, ", ".join(map(str, self.variables)))
