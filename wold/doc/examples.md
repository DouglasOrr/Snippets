# Wold examples

Wold is a pure functional systems programming language on top of LLVM, with:
 - first class functions
 - type-based argument dispatch by default
 - loads of metaprogramming

```wold
quad = fun (x: float) {
  (a, b, c) = (1, 2, 3)
  a * x ^ 2 + b * x + c
}
```

# What would a graph-oriented PL look like?

 - Declarative
 - Non-linear ordering
 - How to make it "powerful" - e.g. reductions, etc?
 - How to handle subgraphs / nesting?

NN graphs are directed acyclic graphs

```
tiny_ff = graph (x, A1, b1, A2, b2) -> y {
  z = sigmoid(A1 @ x + b1)
  y = tanh(A2 @ z + b2)
} where {
  T < Real
  X :: Natural
  Z :: Natural
  Y :: Natural

  x :: T[*, X]
  A1 :: T[Z, X]
  b1 :: T[Z]
  A2 :: T[Y, Z]
  b2 :: T[Y]
  y :: T[*, Y]
}

share_ff = graph (x, A1, b1, A2, b2) -> y) {
  z = tiny_ff(x, A1, b1, A2, b2)
  y = tiny_ff(z, A1, b1, A2, b2)
} where {
  T < Real
  X < Natural
  Z < Natural

  x :: T[*, X]
  A1 :: T[Z, X]
  b1 :: T[Z]
  A2 :: T[X, Z]
  b2 :: T[X]
  y :: T[*, X]
}

share_ff = graph (x, params) -> y) {
  z = tiny_ff(x, *params)
  y = tiny_ff(z, *params)
} where {
  T < Real
  X :: Natural
  Z :: Natural

  x :: T[*, X]
  params :: tiny_ff.(-x) { .T=T, .X=X, .Z=Z, .Y=X }
  y :: T[*, X]
}

nonshare_ff = graph (x, A11, b11, A12, b12, A21, b21, A22, b22) -> y) {
  z = tiny_ff(x, A11, b11, A12, b12)
  y = tiny_ff(z, A21, b21, A22, b22)
}
```

What is a graph? A DAG between one or more inputs & one or more outputs.

How do graphs compose?
 - Connecting inputs & outputs to their parent.
 - Constant instantiation count (copies).
 - Nonconstant instantiation count (shares).

Should we metaprogram graphs? Graphs composed of unspecified subgraphs?
