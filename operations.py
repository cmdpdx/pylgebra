from term import Term, _is_a
from math import factorial

def _seq_product(first, last):
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
    numer = _seq_product((n-k) + 1, n)
    # we already reduced the (n-k)! factor, just need k!
    denom = factorial(k)
    return numer // denom

class ADD(object):
    def __init__(self, augend, addend, subtract=False):
        """Create an addition between the augend and the addend.

        Parameters:
        augend -- the first part of the addition. Can be an int, float, Term 
            or any other operation 
        addend -- the second part of the addition. Same restrictions as augend
        subtract -- consider this object as subtraction? If so, MULT the addend
            by -1
        """
        if _is_a(augend, Term, OPERATION):
            self._augend = augend.clone()
        elif _is_a(augend, int, float):
            self._augend = Term(augend)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(augend, addend))

        if _is_a(addend, Term, OPERATION):
            self._addend = addend.clone()
        elif _is_a(addend, int, float):
            self._addend = Term(addend)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(a, addend))
    
        # for subtraction, multiply through a -1 and deal with it like addition
        if subtract:
            self._addend = MULT(-1, self._addend)
            self._addend.simplify()
            self._addend = self._addend.value

    def _unpack_add(self):
        """Recursively separate nested ADDs into a flast list of terms.

        No other operators are simplified here; they are just returned with
        the rest of the terms.
        """
        terms = []
        for addend in (self._augend, self._addend):
            if _is_a(addend, ADD):
                terms += addend._unpack_add()
            # only include non-trivial terms and operations other than ADDs
            elif _is_a(addend, Term) and not addend.is_zero:
                terms.append(addend)
            elif not _is_a(addend, Term):
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
            while terms:
                a = ADD(a, b)
                b = terms.pop()
        
        return (a, b)

    def _combine_term(self, term, dest):
        # don't search for like terms of operations
        if not _is_a(term, Term):
            dest.append(term)
            return
        # look for a like term to combine with; if none found, append term to list of terms
        for dest_term in dest:
            if _is_a(dest_term, Term) and dest_term.like_term(term):
                dest_term.add(term)
                return
        dest.append(term)

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

        self._augend, self._addend = self._pack_add(terms)

    def distribute(self, factor):
        """Multiply factor to both terms of the sum."""
        # If the factor is an ADD, then we'll have to distribute each term
        # of the sum over the ADD factor: (a+b)(c+d) = a*(c+d) + b*(c+d)
        # Those new products become the terms of this ADD
        if _is_a(factor, ADD):
            factor_a = factor.clone()
            factor_b = factor.clone()
            factor_a.distribute(self._augend)
            factor_b.distribute(self._addend)
            # resolve any new MULTs as a result of the distribute
            factor_a.simplify()
            factor_b.simplify()
            # collect any like terms
            terms = []
            all_terms = factor_a.terms + factor_b.terms
            for term in all_terms:
                self._combine_term(term.value, terms)
            # pack resulting terms into ADDS as needed
            self._augend, self._addend = self._pack_add(terms)
        # If factor is a Term, int, or float, multiply both terms by factor
        # If a term is a Term or ADD, the factor is multiplied/distributed through
        # If a term is a MULT or POW, wrap the term in a MULT (simplified later)
        elif _is_a(factor, Term, int, float):
            if _is_a(self._augend, ADD):
                self._augend.distribute(factor)
            elif _is_a(self._augend, Term):
                self._augend.multiply(factor)
            elif _is_a(self._augend, OPERATION):
                prod = MULT(factor, self._augend)
                prod.simplify()
                self._augend = prod.value
                
            if _is_a(self._addend, ADD):
                self._addend.distribute(factor)
            elif _is_a(self._addend, Term):
                self._addend.multiply(factor)
            elif _is_a(self._addend, OPERATION:
                prod = MULT(factor, self._addend)
                prod.simplify()
                self._addend = prod.value
        # if factor is some other operation, MULT both terms and simplify
        elif _is_a(factor, OPERATION):
            prod = MULT(factor, self._augend)
            prod.simplify()
            self._augend = prod.value
            prod = MULT(factor, self._addend)
            prod.simplify()
            self._addend = prod.value
        else:
            raise TypeError(factor, "({}) is not a recognized type to ditribute over an ADD.".format(type))

    def clone(self):
        """Create a new ADD object identical to this one."""
        a = self._augend.clone()
        b = self._addend.clone()
        return ADD(a, b)
            
    @property
    def terms(self):
        """Get a flat list of all terms in both addends of the ADD, unpacking ADDs."""
        return self._unpack_add()

    @property
    def addends(self):
        """Get both addends (terms) of the sum as a tuple."""
        return (self._augend.value, self._addend.value)

    @property
    def augend(self):
        return self._augend.value

    @property
    def addend(self):
        return self._addend.value

    @property
    def value(self):
        """Get the true value of the ADD; return a copy.
        
        If the self._addend term is 0, then only return the value of the self._augend term.
        Otherwise, clone this ADD.
        
        A value of 0 in the addend term is an indication that this ADD has been simplified.
        By returning only the augend term, ADDs can be reduced, when possible, by calling
        ADD.value.
        """
        if _is_a(self._addend, Term) and self._addend.is_zero:
            return self._augend.value
        else:
            return self.clone()

    def __eq__(self, other):
        if not _is_a(other, ADD): return False
        # Shallow equality, doesn't take commutivity/associativity into consideration
        # return (self.augend == other.augend) and (self.addend == other.addend)
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
        if _is_a(self._augend, ADD):
            s.append("({})".format(str(self._augend)))
        else:
            s.append(str(self._augend))
        s.append(" + ")
        if _is_a(self._addend, ADD):
            s.append("({})".format(str(self._addend)))
        else:
            s.append(str(self._addend))
        
        return "".join(s)


class SUB(ADD):
    def __init__(self, augend, addend):
        super().__init__(augend, addend, subtract=True)


class MULT(object):
    def __init__(self, multiplicand, multiplier):
        """Create a multiplication object between the multiplicand and the multiplier.

        Parameters:
        multiplicand -- the first factor of the product. Can be type int, float, Term,
            or any operation
        multiplier -- the second factor of the product. Same restrictions as multiplicand
        """
        if _is_a(multiplicand, Term, OPERATION):
            self._multiplicand = multiplicand.clone()
        elif _is_a(multiplicand, int, float):
            self._multiplicand = Term(multiplicand)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(multiplicand, multiplier))

        if _is_a(multiplier, Term, OPERATION):
            self._multiplier = multiplier.clone()
        elif _is_a(multiplier, int, float):
            self._multiplier = Term(multiplier)
        else:
            raise TypeError("{} and {} must be of type int, float, Term, or any operation object.".format(multiplicand, multiplier))
    
    def _unpack_mult(self):
        """Recursively separate nested MULTs into a flast list of factors.

        No other operators are simplified here; they are just returned with
        the rest of the factors.
        """
        factors = []
        for factor in (self._multiplicand.value, self._multiplier.value):
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
        is stored in self._multiplicand, with the multiplicative identity in self._multiplier.
        """
        # simplfiy inner groups first (PEMDAS)
        # Save the results in local multiplicand and multiplier variables
        if _is_a(self._multiplicand, OPERATION): self._multiplicand.simplify()
        if _is_a(self._multiplier, OPERATION): self._multiplier.simplify()

        multiplicand = self._multiplicand.value
        multiplier = self._multiplier.value
      
        if _is_a(multiplicand, Term) and _is_a(multiplier, Term):
            multiplicand.multiply(multiplier)
            self._multiplicand, self._multiplier = multiplicand, Term(1)
        elif _is_a(multiplicand, Term) and _is_a(multiplier, ADD):
            multiplier.distribute(multiplicand)
            self._multiplicand, self._multiplier = multiplier, Term(1)
        elif _is_a(multiplicand, ADD) and _is_a(multiplier, Term):
            multiplicand.distribute(multiplier)
            self._multiplicand, self._multiplier = multiplicand, Term(1)
        elif _is_a(multiplicand, ADD) and _is_a(multiplier, ADD):
            multiplicand.distribute(multiplier)
            self._multiplicand, self._multiplier = multiplicand, Term(1)
        elif _is_a(multiplicand, Term, ADD) and _is_a(multiplier, DIV):
            numer = MULT(multiplicand, multiplier.dividend.value)
            numer.simplify()
            self._multiplicand = DIV(numer.value, multiplier.divisor.value)
            self._multiplier = Term(1)
        elif _is_a(multiplicand, DIV) and _is_a(multiplier, Term, ADD):
            numer = MULT(multiplier, multiplicand.dividend.value)
            numer.simplify()
            self._multiplicand = DIV(numer.value, multiplicand.divisor.value)
            self._multiplier = Term(1)
        elif _is_a(multiplicand, DIV) and _is_a(multiplier, DIV):
            numer = MULT(multiplicand.dividend.value, multiplier.dividend.value)
            numer.simplify()
            denom = MULT(multiplicand.divisor.value, multiplier.divisor.value)
            denom.simplify()
            self._multiplicand = DIV(numer.value, denom.value)
            self._multiplier = Term(1)
    
    def clone(self):
        return MULT(self._multiplicand.clone(), self._multiplier.clone())

    @property
    def value(self):
        """Get the "true" value of the MULT; return a copy.
        
        If the b factor is 1, then only return the value of the a factor; otherwise
        clone this MULT. 
        
        A value of 1 in the b factor is an indication that this MULT has been simplified.
        By returning only the a factor, MULTs can be reduced, when possible, by using
        MULT.value.
        """
        if _is_a(self._multiplier, Term) and self._multiplier.is_one:
            return self._multiplicand.value
        else:
            return self.clone()

    @property
    def factors(self):
        return (self._multiplicand.value, self._multiplier.value)

    @property
    def multiplicand(self):
        return self._multiplicand.value
    
    @property
    def multiplier(self):
        return self._multiplier.value

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
        if _is_a(self._multiplicand, ADD, MULT):
            s.append("({})".format(str(self._multiplicand)))
        else:
            s.append(str(self._multiplicand))
        s.append(" * ")
        if _is_a(self._multiplier, ADD, MULT):
            s.append("({})".format(str(self._multiplier)))
        else:
            s.append(str(self._multiplier))
        
        return "".join(s)


class DIV(object):
    def __init__(self, dividend, divisor):
        if _is_a(dividend, int, float):
            self._dividend = Term(dividend)
        elif _is_a(dividend, Term, OPERATION):
            self._dividend = dividend
        else:
            raise TypeError("dividend and divisor must be of type int, float, Term, or any operation object.")
        if _is_a(divisor, int, float):
            self._divisor = Term(divisor)
        elif _is_a(divisor, Term, OPERATION):
            self._divisor = divisor
        else:
            raise TypeError("dividend and divisor must be of type int, float, Term, or any operation object.")
    
    def simplify(self):
        """Attempt to simplify the division, simplifying higher-precedence operations first.

        Note that in this case, due to the binary nature of the operation classes, precedence/
        order of operations is explicit, not implied. Nesting => precedence. 
        
        The following rules are used:
        - Simplify dividend and divisor first, save .values
        - Term / Term => use Term.divide() to simplify to a single Term
        - x / DIV => reciprocate and multiply: create a DIV of (MULT of x and divisor) and
            dividend; simplify and save the div's dividend and divisor in self 
        - ADD / x => wrap a DIV around each addend, dividing by x. Recursively call 
            simplify on new DIVS, create an ADD of each DIV.value
        - Term / ADD => can't be simplified further at the moment

        - MULT / x => POW.simplify can still return a MULT...
        """
        # divisor == 1 means the DIV is already simplified (or doesn't need to be)
        if _is_a(self._divisor, Term) and self._divisor.is_one:
            return

        if _is_a(self._dividend, OPERATION): self._dividend.simplify()
        if _is_a(self._divisor, OPERATION): self._divisor.simplify()
        numer = self._dividend.value
        denom = self._divisor.value

        if _is_a(numer, Term) and _is_a(denom, Term):
            numer.divide(denom)
            self._dividend = numer
            self._divisor = Term(1)
        elif _is_a(denom, DIV):
            # reciprocate and multiply! 
            # simplify the mult because it can always be reduced
            numer = MULT(numer, denom.divisor)
            numer.simplify()
            denom = denom.dividend  # * 1
            div = DIV(numer.value, denom)
            # simplify the new div, since that's what we were really doing here
            div.simplify()
            self._dividend = div.dividend
            self._divisor = div.divisor
        elif _is_a(numer, ADD) and _is_a(denom, Term):
            # divide both addends by the divisor, simplify if possible
            augend = DIV(numer.augend, denom)
            addend = DIV(numer.addend, denom)
            augend.simplify()
            addend.simplify()
            self._dividend = ADD(augend.value, addend.value)
            self._divisor = Term(1)
        elif _is_a(numer, Term) and _is_a(denom, ADD):
            # can't do anything further, save the simplified numer and denom
            self._dividend = numer
            self._divisor = denom
        else:
            print("not yet implemented")

    def clone(self):
        return DIV(self._dividend.clone(), self._divisor.clone())

    @property
    def dividend(self):
        return self._dividend.value
    
    @property
    def divisor(self):
        return self._divisor.value
    
    @property
    def value(self):
        """Get the true value of the DIV; return a copy.
        
        If the divisor is 1, then only return the value of the dividend; otherwise
        clone this DIV. 
        
        A value of 1 in the divisor is an indication that this DIV has been simplified.
        By returning only the value of dividend, DIVs can be reduced, when possible, by using
        DIV.value.
        """
        if _is_a(self._divisor, Term) and self._divisor.is_one:
            return self._dividend.value
        else:
            return self.clone()

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
        self._simplify()
        # in case of nested POWs; get down to some other operation/term as the base
        while _is_a(self._base, POW):
            self._simplify()

    def _simplify(self):
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
        MULT: wrap POW around both factors with same power, keep as MULT 
        DIV: wrap POW around divisor and dividend with same power, keep as DIV
        POW: make base = POW's base; multiply powers
        """
        # Anything ^0 = 1 (see docstring)
        if self._exponent == 0:
            self._base = Term(1)
            self._exponent = 1
            return
        # exponent = 1 is already simplified (or was given as simplified) 
        if self._exponent == 1:
            return

        if _is_a(self._base, Term):
            self._base.power(self._exponent)
            self._exponent = 1
        elif _is_a(self._base, ADD):
            # Error on negative exponents on ADDs for now. 
            # TODO: add binomial expansion for neg exp.
            if self._exponent < 0:
                raise NotImplementedError

            # Binomial expansion: from 0 to the exponent
            # Since 0 exponents are dealt with as a special case, we can assume exponent != 0
            # Thus we will always have at least two terms (from the ADD)
            augend, addend = self._base.augend, self._base.addend
            terms = []
            for i in range(0, self._exponent + 1):
                coeff = choose(self._exponent, i)
                fact_a = POW(augend.clone(), self._exponent - i)
                fact_b = POW(addend.clone(), i)
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
            multiplicand = POW(self._base.multiplicand, self._exponent)
            multiplier = POW(self._base.multiplier, self._exponent)
            multiplicand.simplify()
            multiplier.simplify()
            # MULTs can always be reduced; no need to save that as the base
            base = MULT(multiplicand.value, multiplier.value)
            base.simplify()
            self._base = base.value
            self._exponent = 1
        elif _is_a(self._base, DIV):
            dividend = POW(self._base.dividend, self._exponent)
            divisor = POW(self._base.divisor, self._exponent)
            dividend.simplify()
            divisor.simplify()
            self._base = DIV(dividend.value, divisor.value)
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
        
        
OPERATION = (ADD, SUB, MULT, DIV, POW)
