% Modules inclusions
% include "determinant.mzn"; TODO fix with library inclusion
% Extracts the submatrix C_{i,j} from the matrix M
function array[int,int] of var int: submatrix(int: i, int: j, int: dim, array[int,int] of var int: M) =
    array2d(1..(dim-1), 1..(dim-1), [M[a, b] | a in (1..dim diff i..i), b in (1..dim diff j..j)]);

% Computes the cofactor of the element (i,j) of the matrix M
function var int: cofactor(int: i, int: j, int: dim, array[int,int] of var int: M) =
    pow(-1, i+j) * determinant(dim-1, submatrix(i, j, dim, M));

% Calculates the determinant of a (dim)x(dim) matrix M using Laplace expansion
function var int: determinant(int: dim, array[int,int] of var int: M) =
    if dim = 1 then M[1,1] else (
        sum(j in 1..dim)(M[1,j] * cofactor(1, j, dim, M))
    ) endif;
% ---------------------
% Parameters definitions
par int: n;                 % Number of indexes
set of int: N = 1..n;
set of int: A = 2..n;       % Allocation matrix set of indexes
array[N] of par int: tau;   % Schedule vector
% ---------------------
% Variables definitions
array[N,N] of var int: T;   % Transformation matrix
% -----------------------
% Constraints definitions
% First row schedule vector constraint
constraint forall(j in N)(T[1,j] = tau[j]);
% Nonnegative coefficients constraint
constraint forall(i in A, j in N)(T[i,j] >= 0);
% Unimodular transformation matrix constraint
constraint abs(determinant(n, T)) = 1;
% -----------------------
% Minimization objective (values and distance to the diagonal)
solve minimize sum(i in A, j in N)(T[i,j] * (1 + abs(i-j)));
