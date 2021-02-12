FOR k FROM 1 TO q {
    FOR i FROM 1 TO n-2 {
        STM a[i] = b[i+1] + c[i];
        STM a[i-1] = 1.0 / a[i];
        STM b[i] = a[i];
    }
}