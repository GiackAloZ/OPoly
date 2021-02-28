% Extracts the submatrix C_{i,j} from the matrix M
function array[int,int] of var int: submatrix(int: i, int: j, int: dim, array[int,int] of var int: M) =
    array2d(1..(dim-1), 1..(dim-1), [M[a, b] | a in (1..dim diff i..i), b in (1..dim diff j..j)]);

% Computes the cofactor of the element (i,j) of the matrix M
function var int: cofactor(int: i, int: j, int: dim, array[int,int] of var int: M) =
    pow(-1, i+j) * det(dim-1, submatrix(i, j, dim, M));

% Calculates the determinant of a (dim)x(dim) matrix M using Laplace expansion
function var int: determinant(int: dim, array[int,int] of var int: M) =
    if dim = 1 then M[1,1] else (
        sum(j in 1..dim)(M[1,j] * cofactor(1, j, dim, M))
    ) endif;
