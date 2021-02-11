FOR k FROM 1 TO q {
    FOR i FROM 1 TO n-2 {
        STM a[i] = (a[i-1] + a[i] + a[i+1]) / 3.0;
    }
}