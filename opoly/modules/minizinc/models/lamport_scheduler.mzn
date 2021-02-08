par int: n;
par int: k;
set of int: N = 1..n;
set of int: K = 1..k;
array[K,N] of par int: deps;
array[N] of var int: a;

constraint forall(r in K)(
    sum(i in N)(deps[r,i] * a[i]) > 0
);

constraint forall(i in N)(a[i] >= 0);

solve minimize sum(i in N)(a[i]);