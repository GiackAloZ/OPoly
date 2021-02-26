FOR i FROM 1 TO L {
    FOR j FROM 2 TO M {
        FOR k FROM 2 TO N {
            STM u[j][k] = (u[j+1][k] + u[j][k+1] + u[j-1][k] + u[j][k-1]) * 0.25;
        }
    }
}