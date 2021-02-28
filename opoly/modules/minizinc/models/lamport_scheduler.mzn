% Parameters definitions
par int: n;                     % Number of indexes
par int: r;                     % Number of dependencies
set of int: N = 1..n;
set of int: R = 1..r;
array[R,N] of par int: D;       % Dependency matrix
% ---------------------
% Variables definitions
array[N] of var int: tau;       % Schedule vector
% -----------------------
% Constraints definitions
% Valid schedule constraint
constraint forall(j in R)(
    sum(i in N)(D[j,i] * tau[i]) > 0
);
% Nonnegative coefficients
constraint forall(i in N)(tau[i] >= 0);
% -----------------------
% Minimization objective (minimal latency schedule)
solve minimize sum(i in N)(tau[i]);
