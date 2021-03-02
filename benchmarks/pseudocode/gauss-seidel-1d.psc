FOR q FROM 1 TO maxiter {
    FOR i FROM 1 TO n-2 {
        STM phi[i] = ( phi[i-1] + phi[i+1] ) * (1 / 2.0);
    }
}