#include "hpc.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

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
    for(int new_q = 5; new_q <= l + m + 2 * maxiter + n - 6; new_q++) {
        int new_k_lb = ceil(fmax(1, (1.0 / 2.0) * (-l - m - n + new_q + 6)));
        int new_k_ub = floor(fmin(maxiter, (1.0 / 2.0) * (new_q - 3)));
        #pragma omp parallel for
        for(int new_k = new_k_lb; new_k <= new_k_ub; new_k++) {
            int new_j_lb = fmax(1, -l - n - 2 * new_k + new_q + 4);
            int new_j_ub = fmin(m - 2, -2 * new_k + new_q - 2);
            for(int new_j = new_j_lb; new_j <= new_j_ub; new_j++) {
                int new_i_lb = fmax(1, -l - new_j - 2 * new_k + new_q + 2);
                int new_i_ub = fmin(n - 2, -new_j - 2 * new_k + new_q - 1);
                for(int new_i = new_i_lb; new_i <= new_i_ub; new_i++) {
                    int q = new_k;
                    int k = -new_i - new_j - 2 * new_k + new_q;
                    int j = new_j;
                    int i = new_i;
                    phi[i][j][k] = (phi[i - 1][j][k] + phi[i + 1][j][k] + phi[i][j - 1][k] + phi[i][j + 1][k] + phi[i][j][k - 1] + phi[i][j][k + 1]) * (1 / 6.0);
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