_inst = isinstance

class Variable(object):
    def __init__(self, label, value=None):
        self.label = label
        self.value = value

    def __eq__(self, other):
        return (self.label == other.label)

    def __str__(self):
        return self.label


class VariablePower(object):
    def __init__(self, variable, power=1):
        self.power = power
        if _inst(variable, Variable):
            self.variable = variable
        elif _inst(variable, str):
            self.variable = Variable(variable)
        else:
            raise TypeError("parameter 'variable' must be of type Variable or str.")
        
    def __eq__(self, other):
        return (self.variable == other.variable) and (self.power == other.power)

    def __str__(self):
        p = "^" + str(self.power) if self.power != 1 else ""
        return str(self.variable) + p  
        
    @property
    def base(self):
        return self.variable
    
    def clone(self):
        return VariablePower(self.variable, self.power)


class Term(object):
    def __init__(self, *factors):
        # in case there are lists or tuples in factors we'll need to be able to
        # extend factors.
        factors = list(factors)
        err = False
        self.coefficient = 1
        self.variables = []
        for factor in factors:
            if _inst(factor, int) or _inst(factor, float):
                self.coefficient *= factor
            elif _inst(factor, str) or _inst(factor, Variable):
                self._merge_variable(VariablePower(factor))
            elif _inst(factor, VariablePower):
                self._merge_variable(factor)
            elif _inst(factor, list) or _inst(factor, tuple):
                factors += factor
            else:
                err = True
                break
        if err:
            raise TypeError("parameters must be of type int, float, str, Variable, or VariablePower.")
    
    def _merge_variable(self, new_var):
        for var in self.variables:
            if var.base == new_var.base:
                var.power += new_var.power
                return
        self.variables.append(new_var.clone())

    def like_term(self, other):
        if len(self.variables) != len(other.variables):
            return False
        for var in self.variables:
            if var not in other.variables:
                return False
        return True
    
    def is_constant(self):
        return not self.variables

    # Adds to (modifies) the current Term instance
    def add(self, other):
        if not _inst(other, Term):
            raise TypeError("{} must be of type Term to add to {}".format(other, self))
        if not self.like_term(other):
            raise ValueError("{} and {} are not like terms".format(self, other))
        self.coefficient += other.coefficient

    # Does not alter either Term in the addition; returns a new Term instance
    @staticmethod
    def sum(a, b):
        if not (_inst(a, Term) and _inst(b, Term)):
            raise TypeError("{} and {} must both be of type Term to sum.".format(a, b))
        if not a.like_term(b):
            raise ValueError("{} and {} are not like terms".format(a, b))
        coeff = a.coefficient + b.coefficient
        return Term(coeff, a.variables)

    def multiply(self, other):
        if _inst(other, int) or _inst(other, float):
            self.coefficient *= other
        elif _inst(other, Term) and other.is_constant():
            self.coefficient *= other.coefficient
        elif _inst(other, Term):
            self.coefficient *= other.coefficient
            for var in other.variables:
                self._merge_variable(var)
        else:
            raise TypeError("must multiply a Term by an int, float, or Term.")

    @staticmethod
    def product(a, b):
        if _inst(a, Term):
            term = a.clone()
            term.multiply(b)
            return term
        elif _inst(b, Term):
            term = b.clone()
            term.multiply(a)
            return term
        else:
            raise TypeError("one factor must be a Term to multiply.")

    def clone(self):
        return Term(self.coefficient, self.variables)

    def __str__(self):
        s = []
        if self.coefficient != 1 or self.is_constant():
            s.append(str(self.coefficient))
        for var in self.variables:
            s.append("[{}]".format(str(var)))
        return "".join(s)
