FOR i FROM 1 TO N {
    FOR j FROM 1 TO N {
        STM a[i][j] = (a[i-1][j] + a[i][j-1]) / 2.0;
    }
}