FOR q FROM 1 TO maxiter {
    FOR j FROM 1 TO m-2 {
        FOR i FROM 1 TO n-2 {
            STM phi[i][j] = ( phi[i-1][j] + phi[i+1][j]
                            + phi[i][j-1] + phi[i][j+1] ) * (1 / 4.0);
        }
    }
}