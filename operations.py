# TODO: make this a function that can accept a list of types to check against
_isa = isinstance
from term import Term

class ADD(object):
    def __init__(self, a, b):
        err = False
        if _isa(a, Term) or _isa(a, ADD) or _isa(a, MULT):
            self.a = a.clone()
        elif _isa(a, int) or _isa(a, float):
            self.a = Term(a)
        else:
            err = True

        if _isa(b, Term) or _isa(b, ADD) or _isa(b, MULT):
            self.b = b.clone()
        elif _isa(b, int) or _isa(b, float):
            self.b = Term(b)
        else:
            err = True
        
        if err:
            raise TypeError("{} and {} must be of type int, float, Term, ADD, or MULT.".format(a, b))
    
    def _unpack_add(self, add):
        """Recursively separates ADDs into their two terms, unpack ADDs along the way.

        Note that no other operators are simplified here; they are just returned with
        the rest of the terms.
        """
        terms = []
        for addend in (add.a, add.b):
            if _isa(addend, ADD):
                terms += self._unpack_add(addend)
            else:
                terms.append(addend)
        return terms

    def simplify(self):
        """Combines all like terms within both terms of the add.

        Unpacks nested ADD objects and flattens all terms to a single list.
        All posible like terms are combined. Simplifies the ADD object in place.
        """
        # Collect all the terms (will recursively flatten all sub-ADDs)
        print("simplifying", self)
        all_terms = self.terms
        terms = []
        # It's all addition; combine like terms, unless it's a MULT
        for i in range(len(all_terms)):
            # Skip Nones (they've been combined already)
            if all_terms[i] is None:
                continue
            # Simplify MULTs; result is either an ADD or Term. Unpack ADDs and add
            # the resulting terms to the end of all_terms.
            if _isa(all_terms[i], MULT):
                mult = all_terms[i]
                mult.simplify()
                all_terms[i] = mult.value
                if _isa(all_terms[i], ADD):
                    all_terms += self._unpack_add(all_terms[i])
                    all_terms[i] = None  # clear the term; it's been simplified/unpacked
                    continue 
            # Must be a Term; check all terms past the current one, combining any 
            # like terms
            t = all_terms[i]
            for j in range(i+1, len(all_terms)):
                if _isa(all_terms[j], Term) and t.like_term(all_terms[j]):
                    print("found like terms: {} and {}".format(t, all_terms[j]))
                    t.add(all_terms[j])
                    all_terms[j] = None  # clear the term; it's been combined
            terms.append(t)
        
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

        print("DISTRIBUTING {} over {}".format(factor, self))
        if _isa(factor, Term) or _isa(factor, int) or _isa(factor, float):
            if _isa(self.a, ADD):
                self.a.distribute(factor)
            elif _isa(self.a, Term):
                self.a.multiply(factor)
            if _isa(self.b, ADD):
                self.b.distribute(factor)
            elif _isa(self.b, Term):
                self.b.multiply(factor)
        # If the factor is an ADD, then we'll have to distribute each term
        # of the sum over the ADD factor: (a+b)(c+d) = (a+b)*c + (a+b)*d
        # Those new products become the terms of this ADD
        elif _isa(factor, ADD):
            factor_a = factor.clone()
            factor_b = factor.clone()
            factor_a.distribute(self.a)
            factor_b.distribute(self.b)
            factor_a.simplify()
            factor_b.simplify()
            self.a = factor_a.value
            self.b = factor_b.value
        print("...finished distributing:", self)
        self.simplify()
            
    def clone(self):
        """Create a new ADD object identical to this one."""
        a = self.a.clone()
        b = self.b.clone()
        return ADD(a, b)
            
    @property
    def terms(self):
        """Get a flat list of all terms in both addends of the ADD."""
        t = []
        if _isa(self.a, Term) or _isa(self.a, MULT):
            t.append(self.a)
        elif _isa(self.a, ADD):
            t += self.a.terms
        
        if _isa(self.b, Term) or _isa(self.b, MULT):
            t.append(self.b)
        else:
            t += self.b.terms
        return t

    @property
    def value(self):
        if self.b.coefficient == 0:
            return self.a.clone()
        else:
            return self.clone()

    def __eq__(self, other):
        return (self.a == other.a) and (self.b == other.b)

    def __str__(self):
        s = []
        if _isa(self.a, ADD):
            s.append("({})".format(str(self.a)))
        else:
            s.append(str(self.a))
        s.append(" + ")
        if _isa(self.b, ADD):
            s.append("({})".format(str(self.b)))
        else:
            s.append(str(self.b))
        
        return "".join(s)


class MULT(object):
    def __init__(self, a, b):
        err = False
        if _isa(a, Term) or _isa(a, ADD) or _isa(a, MULT):
            self.a = a.clone()
        elif _isa(a, int) or _isa(a, float):
            self.a = Term(a)
        else:
            err = True

        if _isa(b, Term) or _isa(b, ADD) or _isa(a, MULT):
            self.b = b.clone()
        elif _isa(b, int) or _isa(b, float):
            self.b = Term(b)
        else:
            err = True
        
        if err:
            raise TypeError("{} and {} must be of type int, float, Term, ADD, or MULT.".format(a, b))
    
    # TODO: finish simplify
    def simplify(self):
        """Perform the multiplication, simplify results as much as possible.

        Multiplication can always be performed, and so the result should never
        be a MULT; possible results are Term and ADD. For consistency, the result
        is stored in self.a, with the multiplicative identity in self.b.
        """
        # simplfiy inner groups first (PEMDAS)
        # Save the results in local a and b variables
        if _isa(self.a, ADD) or _isa(self.a, MULT):
            self.a.simplify()
            a = self.a.value    # a is either a Term or ADD
        else:
            a = self.a
        if _isa(self.b, ADD) or _isa(self.b, MULT):
            self.b.simplify()
            b = self.b.value    # b is either a Term or ADD
        else:
            b = self.b

        # There should only be four possibilities at this point:
        # Term x Term, Term x ADD, ADD x Term, ADD x ADD
        if _isa(a, Term) and _isa(b, Term):
            a.multiply(b)
            self.a, self.b = a, Term(1)
        elif _isa(a, Term) and _isa(b, ADD):
            b.simplify()
            b.distribute(a)
            # TODO: determine if the ADD is really just a Term
            self.a, self.b = b, Term(1)
        elif _isa(a, ADD) and _isa(b, Term):
            a.simplify()
            a.distribute(b)
            self.a, self.b = a, Term(1)
        # (a+b) * (c+d) = a(c+d) + b(c+d)
        elif _isa(a, ADD) and _isa(b, ADD):
            a.simplify()
            b.simplify()
            # TODO: FOIL!!
            print("a =", a)
            print("b =", b)
            first = b.distribute(a.a)
            second = b.distribute(a.b)
            self.a, self.b = ADD(first, second), Term(1)
    
    @property
    def value(self):
        if not self.b.is_one():
            self.simplify()
        return self.a.clone()

    def clone(self):
        a = self.a.clone()
        b = self.b.clone()
        return MULT(a, b)

    def __str__(self):
        s = []
        if _isa(self.a, ADD) or _isa(self.a, MULT):
            s.append("({})".format(str(self.a)))
        else:
            s.append(str(self.a))
        s.append(" * ")
        if _isa(self.b, ADD) or _isa(self.b, MULT):
            s.append("({})".format(str(self.b)))
        else:
            s.append(str(self.b))
        
        return "".join(s)

