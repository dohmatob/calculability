# logic
FALSE = lambda x: lambda y: y  # chooses the second arg
TRUE = lambda x: lambda y: x  # chooses the first arg
IFTHENELSE = lambda x: lambda y: lambda z: (x)(y)(z)
AND = lambda x: lambda y: (x)(y)(FALSE)
OR = lambda x: lambda y: (x)(TRUE)(y)
NOT = lambda x: (x)(FALSE)(TRUE)  # negation
XOR = lambda x: lambda y: (x)(NOT(y))(y)  # addition modulo 2

# data containers
PAIR = lambda f: lambda x: lambda y: (y)(f)(x)
FIRST = lambda p: (p)(TRUE)  # select first arg then apply p
SECOND = lambda p: (p)(FALSE)  # select second arg then apply p (code is buggy)

# arithmetic
ZERO = lambda f: lambda x: x  # do something 0 times
SUCC = lambda n: lambda f: lambda z: 
ONE = lambda f: lambda x: f(x)  # do something 1 time
SUCC = lambda n: lambda s: lambda z: (s)((n)(s)(z))
C0 = lambda s: lambda z: z
C1 = SUCC(C0)
C2 = SUCC(C1)
C3 = SUCC(C2)
C4 = SUCC(C3)
C5 = SUCC(C4)

