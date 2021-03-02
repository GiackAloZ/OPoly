#include "hpc.h"
#include <stdio.h>
#include <stdlib.h>

int main(){
    int maxiter, n;

    scanf("%d %d\n", &maxiter, &n);
    double* phi = (double*) malloc(n * sizeof(double));

    fprintf(stderr, "Reading input...");
    // Read input
    for(int i = 0; i < n; i++) {
        scanf("%lf", phi + i);
    }
    fprintf(stderr, "done\n");

    fprintf(stderr, "Computing...");
    double start = hpc_gettime();
    // Gauss-Seidel 1d
    for(int q = 1; q <= maxiter; q++){
        for(int i = 1; i <= n-2; i++){
            phi[i] = ( phi[i-1] + phi[i+1] ) * (1 / 2.0);
        }
    }
    double elaps = hpc_gettime() - start;
    fprintf(stderr, "done in %lf seconds\n", elaps);

    fprintf(stderr, "Printing...");
    // Print output
    for(int i = 0; i < n; i++) {
        printf("%lf ", phi[i]);
    }
    fprintf(stderr, "done\n");

    return 0;
}