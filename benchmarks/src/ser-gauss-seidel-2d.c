#include "hpc.h"
#include <stdio.h>
#include <stdlib.h>

int main(){
    int maxiter, n, m;

    scanf("%d %d %d\n", &maxiter, &n, &m);
    double* tmp = (double*) malloc(n * m * sizeof(double));
    double** phi = (double**) malloc(n * sizeof(double*));
    for(int i = 0; i < n; i++) {
        phi[i] = tmp + i*m;
    }

    fprintf(stderr, "Reading input...");
    // Read input
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < m; j++) {
            scanf("%lf", &phi[i][j]);
        }
    }
    fprintf(stderr, "done\n");

    fprintf(stderr, "Computing...");
    double start = hpc_gettime();
    // Gauss-Seidel 2d
    for(int q = 1; q <= maxiter; q++){
        for(int j = 1; j <= m-2; j++) {
            for(int i = 1; i <= n-2; i++){
                phi[i][j] = ( phi[i-1][j] + phi[i+1][j]
                            + phi[i][j-1] + phi[i][j+1] ) * (1 / 4.0);
            }
        }
    }
    double elaps = hpc_gettime() - start;
    fprintf(stderr, "done in %lf seconds\n", elaps);

    fprintf(stderr, "Printing...");
    // Print output
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < m; j++) {
            printf("%lf ", phi[i][j]);
        }
    }
    fprintf(stderr, "done\n");

    return 0;
}