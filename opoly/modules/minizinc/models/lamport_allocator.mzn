% Extracts the minor matrix of C_{i,j} which is the (n-1)x(n-1) matrix that
% results from deleting the i-th row and j-th column from `mat`
function array[int,int] of var int: minor(int: i, int: j, int: n, array[int,int] of var int: mat) =
    array2d(1..(n-1), 1..(n-1), [mat[a, b] | a in (1..n diff i..i), b in (1..n diff j..j)]);

% Calculates the determinant of a (n)x(n) matrix `mat` using the Laplace expansion
% choosing always to delete the first row
function var int: det(int: n, array[int,int] of var int: mat) =
    if n = 1 then mat[1,1] else (
        sum(j in 1..n)(mat[1,j] * pow(-1, 1+j) * det(n-1, minor(1, j, n, mat)))
    ) endif;

par int: dim;
set of int: DIM = 1..dim;
array[DIM] of par int: a;
array[DIM,DIM] of var int: A;

% Initialization constraint
constraint forall(j in DIM)(A[1,j] = a[j]);
% All non-negative constraint
constraint forall(i in 2..dim, j in DIM)(A[i,j] >= 0);
% Unimodular matrix constraint
constraint abs(det(dim, A)) = 1;

% Minimize values and distance to the diagonal
solve minimize sum(i in 2..dim, j in DIM)(A[i,j] * (1 + abs(i-j)));
