#include "hpc.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

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
    for(int new_q = 3; new_q <= 2 * maxiter + n - 2; new_q++) {
        int new_i_lb = ceil(fmax(1, (1.0 / 2.0) * (-n + new_q + 2)));
        int new_i_ub = floor(fmin(maxiter, (1.0 / 2.0) * (new_q - 1)));
        #pragma omp parallel for
        for(int new_i = new_i_lb; new_i <= new_i_ub; new_i++) {
            int q = new_i;
            int i = -2 * new_i + new_q;
            phi[i] = (phi[i - 1] + phi[i + 1]) * (1 / 2.0);
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