from term import Term, _is_a
from math import factorial

_OPERATION = (ADD, MULT, POW)

def _prod(first, last):
    """Multiply the numbers from first to last, inclusive."""
    prod = 1
    for i in range(first, last+1):
        prod *= i
    return prod

def choose(n, k):
    """Return the number of ways to choose k items from n items."""
    if not _is_a(n, int) or not _is_a(k, int):
        raise TypeError("n and k must be of type int to calculate combination.")
    
    # for known results skip the arithmetic
    if k > n: return 0
    if k == 0 or k == n: return 1
    if k == 1: return n
    # nCk = n! / (k! * (n-k)!)
    # don't need the entire n! in the numerator, reduce by the (n-k)! in the denominator
    # so numerator = n * (n-1) * (n-2) * ... * (n-k+1)!
    numer = _prod((n-k) + 1, n)
    # we already reduced the (n-k)! factor, just need k!
    denom = factorial(k)
    return numer // denom

class ADD(object):
    def __init__(self, a, b):
        err = False
        if _is_a(a, Term, _OPERATION):
            self.a = a.clone()
        elif _is_a(a, int, float):
            self.a = Term(a)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(a, b))

        if _is_a(b, Term, _OPERATION):
            self.b = b.clone()
        elif _is_a(b, int, float):
            self.b = Term(b)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(a, b))
    
    def _unpack_add(self, add):
        """Recursively separates ADDs into their two terms, unpack ADDs along the way.

        Note that no other operators are simplified here; they are just returned with
        the rest of the terms.
        """
        terms = []
        for addend in (add.a, add.b):
            if _is_a(addend, ADD):
                terms += self._unpack_add(addend)
            else:
                terms.append(addend)
        return terms

    def _combine_term(self, term, dest):
        found = False
        for dest_term in dest:
            if dest_term.like_term(term):
                dest_term.add(term)
                found = True
                break
        if not found: dest.append(term)

    def simplify(self):
        """Combines all like terms within both terms of the add.

        Unpacks nested ADD objects and flattens all terms to a single list.
        All posible like terms are combined. Simplifies the ADD object in place.
        Does not simplify any other operation encountered. 
        """
        # Collect all the terms (will recursively flatten all sub-ADDs)
        all_terms = self.terms
        terms = []
        # It's all addition; combine like terms, unless it's another operation
        for term in all_terms:
            if _is_a(term, Term):
                self._combine_term(term, terms)
            else:
                terms.append(term)

        # One term left: save it to a, make b = 0
        if len(terms) == 1:
            self.a = terms[0]
            self.b = Term(0)
        # Two terms left: save them both
        elif len(terms) == 2:
            self.a = terms[0]
            self.b = terms[1]
        # More than two, group pairs into ADD objects
        else:
            a = terms.pop()
            b = terms.pop()
            while len(terms):
                a = ADD(a, b)
                b = terms.pop()
            self.a = a
            self.b = b

    def distribute(self, factor):
        """Multiply factor to both terms of the sum."""
        # If factor is a Term, int, or float, multiply both terms by factor
        # If a term is a Term or ADD, the factor is multiplied/distributed through
        # If a term is a MULT or POW, wrap the term in a MULT (simplified later)
        if _is_a(factor, Term, int, float):
            if _is_a(self.a, ADD):
                self.a.distribute(factor)
            elif _is_a(self.a, Term):
                self.a.multiply(factor)
            elif _is_a(self.a, MULT, POW):
                self.a = MULT(factor, self.a)
                
            if _is_a(self.b, ADD):
                self.b.distribute(factor)
            elif _is_a(self.b, Term):
                self.b.multiply(factor)
            elif _is_a(self.b, MULT, POW):
                self.b = MULT(factor, self.b)
        # If the factor is an ADD, then we'll have to distribute each term
        # of the sum over the ADD factor: (a+b)(c+d) = (a+b)*c + (a+b)*d
        # Those new products become the terms of this ADD
        elif _is_a(factor, ADD):
            factor_a = factor.clone()
            factor_b = factor.clone()
            factor_a.distribute(self.a)
            factor_b.distribute(self.b)
            factor_a.simplify()
            factor_b.simplify()
            self.a = factor_a.value
            self.b = factor_b.value
        self.simplify()
            
    def clone(self):
        """Create a new ADD object identical to this one."""
        a = self.a.clone()
        b = self.b.clone()
        return ADD(a, b)
            
    @property
    def terms(self):
        """Get a flat list of all terms in both addends of the ADD, unpacking ADDs."""
        t = []
        if _is_a(self.a, ADD):
            t += self.a.terms
        else:
            t.append(self.a)
        
        if _is_a(self.b, ADD):
            t += self.b.terms
        else:
            t.append(self.b)
        return t

    @property
    def value(self):
        if _is_a(self.b, Term) and self.b.is_zero():
            return self.a.value
        else:
            return self.clone()

    def __eq__(self, other):
        return (self.a == other.a) and (self.b == other.b)

    def __str__(self):
        s = []
        if _is_a(self.a, ADD):
            s.append("({})".format(str(self.a)))
        else:
            s.append(str(self.a))
        s.append(" + ")
        if _is_a(self.b, ADD):
            s.append("({})".format(str(self.b)))
        else:
            s.append(str(self.b))
        
        return "".join(s)


class MULT(object):
    def __init__(self, a, b):
        if _is_a(a, Term, ADD, MULT):
            self.a = a.clone()
        elif _is_a(a, int, float):
            self.a = Term(a)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(a, b))

        if _is_a(b, Term, ADD, MULT):
            self.b = b.clone()
        elif _is_a(b, int, float):
            self.b = Term(b)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(a, b))
    
    def simplify(self):
        """Perform the multiplication, simplify results as much as possible.

        Multiplication can always be performed, and so the result should never
        be a MULT; possible results are Term and ADD. For consistency, the result
        is stored in self.a, with the multiplicative identity in self.b.
        """
        # simplfiy inner groups first (PEMDAS)
        # Save the results in local a and b variables
        if _is_a(self.a, ADD, MULT):
            self.a.simplify()
            a = self.a.value    # a is either a Term or ADD
        else:
            a = self.a
        if _is_a(self.b, ADD, MULT):
            self.b.simplify()
            b = self.b.value    # b is either a Term or ADD
        else:
            b = self.b

        # There should only be four possibilities at this point:
        # Term x Term, Term x ADD, ADD x Term, ADD x ADD
        if _is_a(a, Term) and _is_a(b, Term):
            a.multiply(b)
            self.a, self.b = a, Term(1)
        elif _is_a(a, Term) and _is_a(b, ADD):
            b.simplify()
            b.distribute(a)
            # TODO: determine if the ADD is really just a Term
            self.a, self.b = b, Term(1)
        elif _is_a(a, ADD) and _is_a(b, Term):
            a.simplify()
            a.distribute(b)
            self.a, self.b = a, Term(1)
        # (a+b) * (c+d) = a(c+d) + b(c+d)
        elif _is_a(a, ADD) and _is_a(b, ADD):
            a.simplify()
            b.simplify()
            first = b.distribute(a.a)
            second = b.distribute(a.b)
            self.a, self.b = ADD(first, second), Term(1)
    
    @property
    def value(self):
        if self.b.is_one():
            return self.a.value
        else:
            return self.clone()

    def clone(self):
        a = self.a.clone()
        b = self.b.clone()
        return MULT(a, b)

    def __str__(self):
        s = []
        if _is_a(self.a, ADD, MULT):
            s.append("({})".format(str(self.a)))
        else:
            s.append(str(self.a))
        s.append(" * ")
        if _is_a(self.b, ADD, MULT):
            s.append("({})".format(str(self.b)))
        else:
            s.append(str(self.b))
        
        return "".join(s)


class POW(object):
    def __init__(self, base, exponent):
        if not _is_a(exponent, int, float):
            raise TypeError("exponent must be of type int or float.")
        self.exponent = exponent
        if _is_a(base, int, float):
            self.base = Term(base)
        elif _is_a(base, Term, ADD, MULT, POW):
            self.base = base
        else:
            raise TypeError("base must be a Term or operation")
    
    def simplify(self):
        """Apply the exponent to the base according to the rules of exponents.

        Powers can always be simplified, since Terms keep track of the exponent on their
        variables. Therefore, the simplfied result is stored in base with exponent set 
        to 1. 

        According to https://en.wikipedia.org/wiki/Zero_to_the_power_of_zero, the general 
        consensus (specifically for algebraic contexts) is that 0^0 = 1. This method is
        making the same assumption, and thus will simplify all POWs with an exponent 0 to 
        Term(1) as base and 1 as the exponent. 

        Will recursively call simplify on any POWs created in this process, but will not
        simplify other operations.

        Rules of exponents:
        Term: apply exponent to the coefficient, add power to exponents of variables
        ADD: binomial expansion of terms (https://en.wikipedia.org/wiki/Binomial_theorem)
        MULT: wrap POW around both factors with same power
        POW: make base = POW's base; multiply powers
        """
        if self.exponent == 0:
            self.base = Term(1)
            self.exponent = 1
            return

        if _is_a(self.base, Term):
            self.base.power(self.exponent)
            self.exponent = 1
        elif _is_a(self.base, ADD):
            # Error on negative exponents on ADDs for now. TODO: add binomial expansion for neg exp.
            if self.exponent < 0:
                raise NotImplementedError

            # Binomial expansion: from 0 to the exponent
            # Since 0 exponents are dealt with as a special case, we can assume exponent != 0
            # Thus we will always have at least two terms (from the ADD)
            a = self.base.a
            b = self.base.b
            terms = []
            for i in range(0, self.exponent+1):
                coeff = choose(self.exponent, i)
                fact_a = POW(a.value, self.exponent-i)
                fact_b = POW(b.value, i)
                # recursively simplify POWs
                fact_a.simplify()
                fact_b.simplify()
                terms.append(Term(coeff, fact_a.value, fact_b.value))
            term_a = terms.pop()
            term_b = terms.pop()
            while terms:
                term_a = ADD(term_a, term_b)
                term_b = terms.pop()
            
            self.base = ADD(term_a, term_b)
            self.exponent = 1
            
        elif _is_a(self.base, MULT):
            a = POW(self.base.a.value, self.exponent)
            b = POW(self.base.b.value, self.exponent)
            a.simplify()
            b.simplify()
            self.base = MULT(a.value, b.value)
            self.exponent = 1
        elif _is_a(self.base, POW):
            self.exponent *= self.base.exponent
            self.base = self.base.base.value
            
    def clone(self):
        """Return a new POW identical to this one."""
        return POW(self.base.clone(), self.exponent)
    
    # TODO: base and exponent properties

    @property
    def value(self):
        """Get the value of the POW: the value of the base if exp is 1, else a clone of this POW."""
        if self.exponent == 1:
            return self.base.value
        else:
            return self.clone()

    def __str__(self):
        return "({})^{}".format(self.base, self.exponent)
        
