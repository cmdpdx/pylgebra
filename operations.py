_inst = isinstance
from term import Term

class ADD(object):
    def __init__(self, a, b):
        err = False
        if _inst(a, Term) or _inst(a, ADD):
            self.a = a
        elif _inst(a, int) or _inst(a, float):
            self.a = Term(a)
        else:
            err = True

        if _inst(b, Term) or _inst(b, ADD):
            self.b = b
        elif _inst(b, int) or _inst(b, float):
            self.b = Term(b)
        else:
            err = True
        
        if err:
            raise TypeError("{} and {} must be of type int, float, Term, or ADD.".format(a, b))
    
    def simplify(self):
        """Combines all like terms within both terms of the add.

        Unpacks nested ADD objects and flattens all terms to a single list.
        All posible like terms are combined. Simplifies the ADD object in place.
        """
        # Collect all the terms (will recursively flatten all sub-ADDs)
        all_terms = self.terms
        terms = []
        # It's all addition; combine like terms
        for i in range(len(all_terms)):
            if all_terms[i] is None:
                continue
            t = all_terms[i]
            for j in range(i+1, len(all_terms)):
                if all_terms[j] is not None and t.like_term(all_terms[j]):
                    t.add(all_terms[j])
                    all_terms[j] = None
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
        if _inst(factor, Term) or _inst(factor, int) or _inst(factor, float):
            if _inst(self.a, ADD):
                self.a.distribute(factor)
            elif _inst(self.a, Term):
                self.a.multiply(factor)
            if _inst(self.b, ADD):
                self.b.distribute(factor)
            elif _inst(self.b, Term):
                self.b.multiply(factor)
        # If the factor is an ADD, then we'll have to distribute each term
        # of the sum over the ADD factor: (a+b)(c+d) = (a+b)*c + (a+b)*d
        # Those new products become the terms of this ADD
        elif _inst(factor, ADD):
            a = factor.clone()
            b = factor.clone()
            a.distribute(self.a)
            b.distribute(self.b)
            a.simplify()
            b.simplify()
            self.a = a
            self.b = b
        self.simplify()
            
    def clone(self):
        """Create a new ADD object identical to this one."""
        a = self.a.clone()
        b = self.b.clone()
        return ADD(a, b)
            
    @property
    def terms(self):
        """Get a flat list of all terms in both parts of the ADD."""
        t = []
        if _inst(self.a, Term):
            t.append(self.a)
        else:
            t += self.a.terms
        if _inst(self.b, Term):
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
        if _inst(self.a, ADD):
            s.append("({})".format(str(self.a)))
        else:
            s.append(str(self.a))
        s.append(" + ")
        if _inst(self.b, ADD):
            s.append("({})".format(str(self.b)))
        else:
            s.append(str(self.b))
        
        return "".join(s)


class MULT(object):
    def __init__(self, a, b):
        err = False
        if _inst(a, Term) or _inst(a, ADD) or _inst(a, MULT):
            self.a = a
        elif _inst(a, int) or _inst(a, float):
            self.a = Term(a)
        else:
            err = True

        if _inst(b, Term) or _inst(b, ADD) or _inst(a, MULT):
            self.b = b
        elif _inst(b, int) or _inst(b, float):
            self.b = Term(b)
        else:
            err = True
        
        if err:
            raise TypeError("{} and {} must be of type int, float, Term, ADD, or MULT.".format(a, b))
    
    # TODO: finish simplify
    def simplify(self):
        if _inst(self.a, Term):
            if _inst(self.b, Term):
                self.a.multiply(self.b)
                self.b = Term(1)
            elif _inst(self.b, ADD):
                self.b.distribute(self.a)
                self.a = Term(1)
            # what if b is a MULT?
        # what if a is an ADD? or a MULT?
    
    # TODO: finish value
    @property
    def value(self):
        if _inst(self.a, Term) and _inst(self.b, Term):
            return Term.product(self.a, self.b)
        if _inst(self.a, Term):
            if _inst(self.b, ADD):
                b = self.b.clone()
                b.distribute(self.a)
                return b.value
            if _inst(self.b, MULT):
                # depends on what the pieces of the MULT are...
                pass
        if _inst(self.b, Term):
            if _inst(self.a, ADD):
                a = self.a.clone()
                a.distribute(self.b)
                return a.value
            if _inst(self.a, MULT):
                pass

    def clone(self):
        a = self.a.clone()
        b = self.b.clone()
        return MULT(a, b)

    def __str__(self):
        s = []
        if _inst(self.a, ADD) or _inst(self.a, MULT):
            s.append("({})".format(str(self.a)))
        else:
            s.append(str(self.a))
        s.append(" * ")
        if _inst(self.b, ADD) or _inst(self.b, MULT):
            s.append("({})".format(str(self.b)))
        else:
            s.append(str(self.b))
        
        return "".join(s)

