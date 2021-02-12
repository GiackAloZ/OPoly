FOR i FROM 1 TO L {
    FOR j FROM 1 TO M-1 {
        FOR k FROM 1 TO N-1 {
            STM u[j][k] = (u[j+1][k] + u[j][k+1] + u[j-1][k] + u[j][k-1]) * 0.25;
        }
    }
}