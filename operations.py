from term import Term, _is_a
from math import factorial

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
        if _is_a(a, Term, OPERATION):
            self.a = a.clone()
        elif _is_a(a, int, float):
            self.a = Term(a)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(a, b))

        if _is_a(b, Term, OPERATION):
            self.b = b.clone()
        elif _is_a(b, int, float):
            self.b = Term(b)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(a, b))
    
    # TODO: is this just a redundant version of .terms?
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

    def _pack_add(self, terms):
        """Pack a list of terms into nested ADDs."""
        a = None
        b = None
        # One term: save it to a, make b = 0
        if len(terms) == 1:
            a = terms[0]
            b = Term(0)
        # More than one: nest ADDs as needed for > 2 terms
        else:
            a = terms.pop()
            b = terms.pop()
            while len(terms):
                a = ADD(a, b)
                b = terms.pop()
        
        return (a, b)

    def _combine_term(self, term, dest):
        # don't search for like terms of operations
        if not _is_a(term, Term):
            dest.append(term)
            return

        found = False
        for dest_term in dest:
            if _is_a(dest_term, Term) and dest_term.like_term(term):
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
            self._combine_term(term, terms)

        self.a, self.b = self._pack_add(terms)

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
        # of the sum over the ADD factor: (a+b)(c+d) = a*(c+d) + b*(c+d)
        # Those new products become the terms of this ADD
        elif _is_a(factor, ADD):
            factor_a = factor.clone()
            factor_b = factor.clone()
            factor_a.distribute(self.a)
            factor_b.distribute(self.b)
            # resolve any new MULTs as a result of the distribute
            factor_a.simplify()
            factor_b.simplify()
            # collect any like terms
            terms = []
            all_terms = factor_a.terms + factor_b.terms
            for term in all_terms:
                self._combine_term(term.value, terms)
            # pack resulting terms into ADDS as needed
            self.a, self.b = self._pack_add(terms)

    def clone(self):
        """Create a new ADD object identical to this one."""
        a = self.a.clone()
        b = self.b.clone()
        return ADD(a, b)
            
    @property
    def terms(self):
        """Get a flat list of all terms in both addends of the ADD, unpacking ADDs."""
        t = []
        for addend in (self.a, self.b):
            if _is_a(addend, ADD):
                t += addend.terms
            # only include non-trivial terms
            elif _is_a(addend, Term) and not addend.is_zero:
                t.append(addend)
            elif not _is_a(addend, Term):
                t.append(addend)
        return t

    @property
    def addends(self):
        return (self.a.value, self.b.value)

    @property
    def value(self):
        """Get the "true" value of the ADD; return a copy.
        
        If the b term is 0, then only return the value of the a term. Otherwise, clone
        this ADD.
        
        A value of 0 in the b term is an indication that this ADD has been simplified.
        By returning only the a term, ADDs can be reduced, when possible, by using
        ADD.value.
        """
        if _is_a(self.b, Term) and self.b.is_zero:
            return self.a.value
        else:
            return self.clone()

    def __eq__(self, other):
        if not _is_a(other, ADD): return False
        # Shallow equality, doesn't take commutivity/associativity into consideration
        # return (self.a == other.a) and (self.b == other.b)
        # Deeper equality: would they evaluate to the same value? Check term by term.
        self_terms = self.terms
        other_terms = other.terms
        if len(self_terms) != len(other_terms): return False
        for self_term in self_terms:
            found = False
            for i, other_term in enumerate(other_terms):
                if other_term is not None and self_term == other_term:
                    found = True
                    other_terms[i] = None
                    break
            if not found: return False
        return True

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
        if _is_a(a, Term, OPERATION):
            self.a = a.clone()
        elif _is_a(a, int, float):
            self.a = Term(a)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(a, b))

        if _is_a(b, Term, OPERATION):
            self.b = b.clone()
        elif _is_a(b, int, float):
            self.b = Term(b)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(a, b))
    
    def _unpack_mult(self):
        factors = []
        for factor in (self.a.value, self.b.value):
            if _is_a(factor, MULT):
                factors += factor._unpack_mult()
            # only include non-trivial factors
            elif _is_a(factor, Term) and not factor.is_one:
                factors.append(factor)
            # include any other operation encountered
            elif not _is_a(factor, Term):
                factors.append(factor)
        return factors

    def simplify(self):
        """Perform the multiplication, simplify results as much as possible.

        Multiplication can always be performed, and so the result should never
        be a MULT. For consistency, the result
        is stored in self.a, with the multiplicative identity in self.b.
        """
        # simplfiy inner groups first (PEMDAS)
        # Save the results in local a and b variables
        if _is_a(self.a, OPERATION):
            self.a.simplify()
            a = self.a.value    # a is either a Term or ADD
        else:
            a = self.a
        if _is_a(self.b, OPERATION):
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
            print("term and add")
            b.distribute(a)
            print(b)
            # TODO: determine if the ADD is really just a Term
            self.a, self.b = b, Term(1)
        elif _is_a(a, ADD) and _is_a(b, Term):
            a.distribute(b)
            self.a, self.b = a, Term(1)
        elif _is_a(a, ADD) and _is_a(b, ADD):
            a.distribute(b.value)
            self.a, self.b = a, Term(1)
    
    @property
    def value(self):
        """Get the "true" value of the MULT; return a copy.
        
        If the b factor is 1, then only return the value of the a factor; otherwise
        clone this MULT. 
        
        A value of 1 in the b factor is an indication that this MULT has been simplified.
        By returning only the a factor, MULTs can be reduced, when possible, by using
        MULT.value.
        """
        if self.b.is_one:
            return self.a.value
        else:
            return self.clone()

    @property
    def factors(self):
        return (self.a.value, self.b.value)

    def clone(self):
        return MULT(self.a.clone(), self.b.clone())

    def __eq__(self, other):
        if not _is_a(other, MULT): return False
        self_facts = self._unpack_mult()
        other_facts = other._unpack_mult()
        if len(self_facts) != len(other_facts): return False
        for self_fact in self_facts:
            found = False
            for i, other_fact in enumerate(other_facts):
                if other_fact is not None and self_fact == other_fact:
                    other_facts[i] = None
                    found = True
                    break
            if not found: return False
        return True

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


class DIV(object):
    def __init__(self, dividend, divisor):
        if _is_a(dividend, int, float):
            self.dividend = Term(dividend)
        elif _is_a(dividend, Term, OPERATION):
            self.dividend = dividend
        else:
            raise TypeError("dividend and divisor must be of type int, float, Term, or any operation object.")
        if _is_a(divisor, int, float):
            self.divisor = Term(divisor)
        elif _is_a(divisor, Term, OPERATION):
            self.divisor = divisor
        else:
            raise TypeError("dividend and divisor must be of type int, float, Term, or any operation object.")
    
    def simplify(self):
        """Summary statement.

        Division can always be performed (except if divisor = 0). The following rules are used:
        - Simplify dividend and divisor first, save .values
        - Term / Term => use Term.divide() to simplify to a single Term
        - Term / OPERATION => can't be simplified further at the moment
        - ADD / x => wrap a DIV around each addend, dividing by x. Recursively call 
            simplify on new DIVS?
        - MULT / x => POW.simplify can still return a MULT...
        - POW / x => POW.simplify can still return a POW... 
        """
        self.dividend.simplify()
        self.divisor.simplify()
        nume = self.dividend.value
        denom = self.divisor.value
        if _is_a(nume, Term) and _is_a(denom, Term):
            nume.divide(denom)
            self.dividend = nume
            self.divisor = Term(1)
        else:
            print("not yet implemented")


class POW(object):
    def __init__(self, base, exponent):
        if not _is_a(exponent, int, float):
            raise TypeError("exponent must be of type int or float.")
        self._exponent = exponent
        if _is_a(base, int, float):
            self._base = Term(base)
        elif _is_a(base, Term, OPERATION):
            self._base = base
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
        if self._exponent == 0:
            self._base = Term(1)
            self._exponent = 1
            return

        if _is_a(self._base, Term):
            self._base.power(self._exponent)
            self._exponent = 1
        elif _is_a(self._base, ADD):
            # Error on negative exponents on ADDs for now. TODO: add binomial expansion for neg exp.
            if self._exponent < 0:
                raise NotImplementedError

            # Binomial expansion: from 0 to the exponent
            # Since 0 exponents are dealt with as a special case, we can assume exponent != 0
            # Thus we will always have at least two terms (from the ADD)
            a, b = self._base.addends
            terms = []
            for i in range(0, self._exponent + 1):
                coeff = choose(self._exponent, i)
                fact_a = POW(a.value, self._exponent - i)
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
            
            self._base = ADD(term_a, term_b)
            self._exponent = 1
            
        elif _is_a(self._base, MULT):
            fact_a, fact_b = self._base.factors
            a = POW(fact_a, self._exponent)
            b = POW(fact_b, self._exponent)
            a.simplify()
            b.simplify()
            self._base = MULT(a.value, b.value)
            self._exponent = 1
        elif _is_a(self._base, POW):
            self._exponent *= self._base.exponent
            self._base = self._base.base
            
    def clone(self):
        """Return a new POW identical to this one."""
        return POW(self._base.clone(), self._exponent)

    @property
    def base(self):
        return self._base.value

    @property
    def exponent(self):
        return self._exponent

    @property
    def value(self):
        """Get the value of the POW: the value of the base if exp is 1, else a clone of this POW."""
        if self._exponent == 1:
            return self._base.value
        else:
            return self.clone()

    def __eq__(self, other):
        if not _is_a(other, POW): return False
        return (self.exponent == other.exponent) and (self.base == other.base)

    def __str__(self):
        return "({})^{}".format(self._base.value, self._exponent)
        
        
OPERATION = (ADD, MULT, DIV, POW)
