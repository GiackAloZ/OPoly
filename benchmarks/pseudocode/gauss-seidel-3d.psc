FOR q FROM 1 TO maxiter {
    FOR k FROM 1 TO l-2 {
        FOR j FROM 1 TO m-2 {
            FOR i FROM 1 TO n-2 {
                STM phi[i][j][k] = ( phi[i-1][j][k] + phi[i+1][j][k]
                                   + phi[i][j-1][k] + phi[i][j+1][k]
                                   + phi[i][j][k-1] + phi[i][j][k+1] ) * (1 / 6.0);
            }
        }
    }
}