from operations import ADD
from term import Variable, VariablePower, Term

x = Variable("x")
y = Variable("y")
xp = []
yp = []
for i in range(1, 6):
    xp.append(VariablePower(x, i))
    yp.append(VariablePower(y, i))

t1 = Term(2, xp[1])
t2 = Term(3, xp[1])
a = ADD(t1, 5)
b = ADD(3, 1)
b.simplify()
print(a.value)
print(b.value)
a.distribute(b)
print(a)
