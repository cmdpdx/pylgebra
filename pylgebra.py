import unittest
from operations import ADD, MULT
from term import Variable, VariablePower, Term

x = Variable("x")
y = Variable("y")
xp = []
yp = []
for i in range(1, 6):
    xp.append(VariablePower(x, i))
    yp.append(VariablePower(y, i))

class ADDTestCase(unittest.TestCase):
    def setUp(self):
        self.one = Term(1)
        self.x_1 = Term(VariablePower(x))
        self.x_2 = Term(VariablePower(x, 2))
        self.x_1_plus_one = ADD(self.x_1, self.one)
        self.x_2_plus_one = ADD(self.x_2, self.one)
        self.x_2_plus_x_1 = ADD(self.x_2, self.x_1)
    
    def test_add_constants(self):
        two = Term(2)
        res = ADD(self.one, self.one)
        res.simplify()
        self.assertEqual(res.value, two, "incorrect result for adding constants")
    
    def test_add_constant_varpow(self):
        ans = ADD(self.x_1, Term(1))
        res = ans.clone()
        res.simplify()
        self.assertEqual(res.value, ans, "incorrect result for adding constant and variable power")

if __name__ == "__main__":
    #unittest.main(verbosity=2)
    t1 = Term(1)
    t2 = Term((x, 1))
    
    _expr = MULT(3, ADD(Term((x, 1)), 1))
    expr = ADD(1, ADD(2, MULT(3, ADD(Term((x, 1)), 1))))
    print(expr)
    expr.simplify()
    print(expr.value)
