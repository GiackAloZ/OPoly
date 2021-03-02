#include "hpc.h"
#include <stdio.h>
#include <stdlib.h>

int main(){
    int maxiter, n, m, l;

    scanf("%d %d %d %d\n", &maxiter, &n, &m, &l);
    fprintf(stderr, "Allocating input...");
    double* tmp = (double*) malloc(n * m * l * sizeof(double));
    double*** phi = (double***) malloc(n * sizeof(double**));
    for(int i = 0; i < n; i++) {
        phi[i] = (double**) malloc(m * sizeof(double*));
        for(int j = 0; j < m; j++) {
            phi[i][j] = tmp + i*m*l + j*l;
        }
    }
    fprintf(stderr, "done\n");

    fprintf(stderr, "Reading input...");
    // Read input
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < m; j++) {
            for(int k = 0; k < l; k++) {
                scanf("%lf", &phi[i][j][k]);
            }
        }
    }
    fprintf(stderr, "done\n");

    fprintf(stderr, "Computing...");
    double start = hpc_gettime();
    // Gauss-Seidel 3d
    for(int q = 1; q <= maxiter; q++){
        for(int k = 1; k <= l-2; k++) {
            for(int j = 1; j <= m-2; j++) {
                for(int i = 1; i <= n-2; i++){
                    phi[i][j][k] = ( phi[i-1][j][k] + phi[i+1][j][k]
                                   + phi[i][j-1][k] + phi[i][j+1][k]
                                   + phi[i][j][k-1] + phi[i][j][k+1] ) * (1 / 6.0);
                }
            }
        }
    }
    double elaps = hpc_gettime() - start;
    fprintf(stderr, "done in %lf seconds\n", elaps);

    fprintf(stderr, "Printing...");
    // Print output
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < m; j++) {
            for(int k = 0; k < l; k++) {
                printf("%lf ", phi[i][j][k]);
            }
        }
    }
    fprintf(stderr, "done\n");

    return 0;
}