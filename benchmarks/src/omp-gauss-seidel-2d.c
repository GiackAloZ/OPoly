#include "hpc.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

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
    for(int new_q = 4; new_q <= m + 2 * maxiter + n - 4; new_q++) {
        int new_j_lb = ceil(fmax(1, (1.0 / 2.0) * (-m - n + new_q + 4)));
        int new_j_ub = floor(fmin(maxiter, (1.0 / 2.0) * (new_q - 2)));
        #pragma omp parallel for
        for(int new_j = new_j_lb; new_j <= new_j_ub; new_j++) {
            int new_i_lb = fmax(1, -m - 2 * new_j + new_q + 2);
            int new_i_ub = fmin(n - 2, -2 * new_j + new_q - 1);
            for(int new_i = new_i_lb; new_i <= new_i_ub; new_i++) {
                int q = new_j;
                int j = -new_i - 2 * new_j + new_q;
                int i = new_i;
                phi[i][j] = (phi[i - 1][j] + phi[i + 1][j] + phi[i][j - 1] + phi[i][j + 1]) * (1 / 4.0);
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