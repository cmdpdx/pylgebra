def _is_a(obj, *types):
    """Returns True if obj is any of the given types; False otherwise."""
    types = list(types)
    while types:
        t = types.pop()
        # allow lists or tuples of types to be passed
        if isinstance(t, list) or isinstance(t, tuple):
            types += t
        elif isinstance(obj, t): return True
    return False


class Variable(object):
    """Base object to represent an unknown value."""
    def __init__(self, label, value=None):
        self.label = label
        self.value = value

    def __eq__(self, other):
        return (self.label == other.label)

    def __str__(self):
        return self.label


class VariablePower(object):
    """Represents a variable raised to any power; used to build Terms.
    
    Properties:
    base -- the base of the power; returns a Variable (read-only)
    power -- the exponent the base is raised to (read/write)

    Public methods:
    clone -- returns a new VariablePower instance with the same Variable and power. Note
        that the Variable is not a clone (since all variables with the same label 
        represent the same unknown value). 
    """
    def __init__(self, variable, power=1):
        self.power = power
        if _is_a(variable, Variable):
            self.variable = variable
        elif _is_a(variable, str):
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
    """A term in an algebraic expression.

    A term contains a real-number coefficient and 0 or more variables multiplying the
    coefficient, each variable raised to any integer power (TODO: allow rational exp).

    Pubic methods:
    like_term --  returns True if the given Term's variables match this Term; else False
    add -- add a given Term, if possible, to this Term by adding coefficients.
    multiply -- multiply this term by an int, float, or Term. 
    power -- raise this Term to the given power.
    clone -- create a new Term exactly like the current one

    Properties:
    is_constant, is_one, is_zero -- tests for special Terms
    value -- returns a clone of this Term
    """ 

    def __init__(self, *factors):
        """Creates a new Term by multiplying the given list of factors.

        Factors is assumed to not be in any particular order. As each factor
        is encountered, it is handled differently depending on its type:
        
        int, float -- multiply the coefficient
        str, Variable -- assumes var^1, creates a VariablePower; multiply current variables
        VariablePower -- multiply current variables
        tuple -- assume it is formatted as (var, power); creates a VariablePower; multiply current variables   
        list -- add to the list of factors

        Raises:
        TypeError -- if anything other than the above is passed in 

        Instance variables:
        coefficient -- the real number multiplying the term
        variables -- list of all variables raised to their respective powers
        """
        # in case there are lists or tuples in factors we'll need to be able to
        # extend factors.
        factors = list(factors)
        self.coefficient = 1
        self.variables = []
        for factor in factors:
            if _is_a(factor, int, float):
                self.coefficient *= factor
            elif _is_a(factor, str, Variable):
                self._merge_variable(VariablePower(factor))
            elif _is_a(factor, VariablePower):
                self._merge_variable(factor)
            elif _is_a(factor, tuple):
                var, power = factor
                self._merge_variable(VariablePower(var, power))
            elif _is_a(factor, list):
                factors += factor
            elif _is_a(factor, Term):
                self.coefficient *= factor.coefficient
                self._merge_variables(factor.variables)
            else:
                raise TypeError("parameters must be of type int, float, str, Variable, VariablePower, or Term.")
        # just in case there are var^0, clear them now to prevent like-term mistakes
        self._simplify()
    
    def _merge_variable(self, other):
        self._merge_variables([other])

    def _merge_variables(self, other_vars, division=False):
        """Multiply the given list of variables with this term's variables.
        
        If division == True, multiply other_var.power by -1 before adding, since
        (x^a)/(x^b) = x^(a-b).
        """
        # if no variables are multiplying this term, multiply 
        # all of the incoming variables as is
        if not self.variables:
            self.variables = other_vars.copy()
            if division:
                for var in self.variables:
                    var.power *= -1
            return

        to_add = []
        sign = 1 if not division else -1
        for other_var in other_vars:
            matched = False
            for var in self.variables:
                if var.base == other_var.base:
                    var.power += other_var.power * sign
                    matched = True
                    break
            if not matched: 
                var = other_var.clone()
                var.power *= sign
                to_add.append(var)
        self.variables += to_add

    def _simplify(self):
        """Converts 0 exponent variables to 1; removes variables if coefficient is 0"""
        if self.coefficient == 0 and self.variables:
            self.variables = []
        else:
            variables = [var for var in self.variables if var.power != 0]
            self.variables = variables

    def like_term(self, other):
        if len(self.variables) != len(other.variables):
            return False
        for var in self.variables:
            if var not in other.variables:
                return False
        return True

    def add(self, other):
        """Adds a Term (if possible) to the current Term.

        Combines two terms if they are like terms. Also allows ints and floats
        to be added if the Term is a constant. 

        Raises:
        TypeError -- when attempting to add an incorrect type to a Term
        ValueError -- if the terms to be added are not like terms
        """
        # allow ints, floats to be added to constants
        if _is_a(other, int, float) and self.is_constant:
            self.coefficient += other
            return
        if not _is_a(other, Term):
            raise TypeError("{} must be of type Term to add to {}".format(other, self))
        if not self.like_term(other):
            raise ValueError("{} and {} are not like terms".format(self, other))
        self.coefficient += other.coefficient
        self._simplify()

    def multiply(self, other):
        """Multiply this Term by an int, float, or Term.
        
        Raises:
        TypeError -- if other is a type other than int, float, or Term
        """
        if _is_a(other, int, float):
            self.coefficient *= other
        elif _is_a(other, Term) and other.is_constant:
            self.coefficient *= other.coefficient
        elif _is_a(other, Term):
            self.coefficient *= other.coefficient
            self._merge_variables(other.variables)
        else:
            raise TypeError("must multiply a Term by an int, float, or Term.")
        self._simplify()
    
    def divide(self, other):
        """Multiply this Term by an int, float, or Term.
        
        Raises:
        TypeError -- if other is a type other than int, float, or Term
        """
        if _is_a(other, int, float):
            self.coefficient /= other
        elif _is_a(other, Term) and other.is_constant:
            self.coefficient /= other.coefficient
        elif _is_a(other, Term):
            self.coefficient /= other.coefficient
            self._merge_variables(other.variables, division=True)
        else:
            raise TypeError("must divide a Term by an int, float, or Term.")
        self._simplify()

    def power(self, exp):
        """Raise this Term to the exp power."""
        if not _is_a(exp, int):
            raise ValueError("Terms can only be raised to integer powers")
        self.coefficient = self.coefficient ** exp
        for var in self.variables:
            var.power *= exp
        self._simplify()

    def clone(self):
        """Return a new Term instance, cloning all variables."""
        variables = []
        for var in self.variables:
            variables.append(var.clone())
        return Term(self.coefficient, variables)

    @property
    def is_constant(self):
        return self.is_zero or not self.variables

    @property
    def is_one(self):
        return self.is_constant and self.coefficient == 1

    @property
    def is_zero(self):
        return self.coefficient == 0

    @property
    def value(self):
        """Get a clone of this term."""
        return self.clone()

    def __eq__(self, other):
        if not _is_a(other, Term): return False
        return self.like_term(other) and (self.coefficient == other.coefficient)

    def __str__(self):
        s = []
        if self.coefficient != 1 or self.is_constant:
            s.append(str(self.coefficient))
        for var in self.variables:
            s.append("[{}]".format(str(var)))
        return "".join(s)
    
"""
# Deprecated (temporarily?)
def sum(a, b):
    if not (_is_a(a, Term) and _is_a(b, Term)):
        raise TypeError("{} and {} must both be of type Term to sum.".format(a, b))
    if not a.like_term(b):
        raise ValueError("{} and {} are not like terms".format(a, b))
    coeff = a.coefficient + b.coefficient
    return Term(coeff, a.variables)

def product(a, b):
    if _is_a(a, Term):
        term = a.clone()
        term.multiply(b)
        return term
    elif _inst(b, Term):
        term = b.clone()
        term.multiply(a)
        return term
    else:
        raise TypeError("one factor must be a Term to multiply.")
"""
