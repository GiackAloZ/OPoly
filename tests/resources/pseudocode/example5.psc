FOR i FROM 1 TO N-1 {
    FOR j FROM 1 TO M-2 {
        FOR k FROM 1 TO L-2 {
            STM u[j][k] = (u[j+1][k] + u[j][k+1] + u[j-1][k] + u[j][k-1]) * 0.25;
        }
    }
}