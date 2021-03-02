/****************************************************************************
 *
 * hpc.h - Miscellaneous utility functions for the HPC course
 *
 * Written in 2017 by Moreno Marzolla <moreno.marzolla(at)unibo.it>
 * Last modified in 2018 by Moreno Marzolla
 *
 * To the extent possible under law, the author(s) have dedicated all 
 * copyright and related and neighboring rights to this software to the 
 * public domain worldwide. This software is distributed without any warranty.
 *
 * You should have received a copy of the CC0 Public Domain Dedication
 * along with this software. If not, see 
 * <http://creativecommons.org/publicdomain/zero/1.0/>. 
 *
 * --------------------------------------------------------------------------
 *
 * This header file provides a function double hpc_gettime() that
 * returns the elapsed time (in seconds) since "the epoch". The
 * function uses the timing routing of the underlying parallel
 * framework (OpenMP or MPI), if enabled; otherwise, the default is to
 * use the clock_gettime() function.
 *
 * IMPORTANT NOTE: to work reliably this header file must be the FIRST
 * header file that appears in your code.
 *
 ****************************************************************************/

#ifndef HPC_H
#define HPC_H

#if defined(_OPENMP)
#include <omp.h>
/******************************************************************************
 * OpenMP timing routines
 ******************************************************************************/
double hpc_gettime( void )
{
    return omp_get_wtime();
}

#elif defined(MPI_Init)
/******************************************************************************
 * MPI timing routines
 ******************************************************************************/
double hpc_gettime( void )
{
    return MPI_Wtime();
}

#else
/******************************************************************************
 * POSIX-based timing routines
 ******************************************************************************/
#if _XOPEN_SOURCE < 600
#define _XOPEN_SOURCE 600
#endif
#include <time.h>

double hpc_gettime( void )
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts );
    return ts.tv_sec + (double)ts.tv_nsec / 1e9;
}
#endif

#ifdef __CUDACC__

#include <stdio.h>
#include <stdlib.h>

/* from https://gist.github.com/ashwin/2652488 */

#define cudaSafeCall( err ) __cudaSafeCall( err, __FILE__, __LINE__ )
#define cudaCheckError()    __cudaCheckError( __FILE__, __LINE__ )

inline void __cudaSafeCall( cudaError err, const char *file, const int line )
{
#ifndef NO_CUDA_CHECK_ERROR
    if ( cudaSuccess != err ) {
        fprintf( stderr, "cudaSafeCall() failed at %s:%i : %s\n",
                 file, line, cudaGetErrorString( err ) );
        abort();
    }
#endif
}

inline void __cudaCheckError( const char *file, const int line )
{
#ifndef NO_CUDA_CHECK_ERROR
    cudaError err = cudaGetLastError();
    if ( cudaSuccess != err ) {
        fprintf( stderr, "cudaCheckError() failed at %s:%i : %s\n",
                 file, line, cudaGetErrorString( err ) );
        abort();
    }

    /* More careful checking. However, this will affect performance.
       Comment away if needed. */
    err = cudaDeviceSynchronize();
    if( cudaSuccess != err ) {
        fprintf( stderr, "cudaCheckError() with sync failed at %s:%i : %s\n",
                 file, line, cudaGetErrorString( err ) );
        abort();
    }
#endif
}

#include <unistd.h>

cudaEvent_t cudaWatchdogEvent;

void cudaWatchdogStart( void )
{
    cudaEventCreateWithFlags( &cudaWatchdogEvent, cudaEventDisableTiming);
}

/* from https://stackoverflow.com/questions/39513830/launch-cuda-kernel-with-a-timeout/39514902 */
void cudaWatchdogStop( int usec_timeout )
{
    int progressed = 0;
    /* poll the event while the kernel runs */
    while (cudaEventQuery(cudaWatchdogEvent) != cudaSuccess) {
        usleep(20000);
        progressed += 20000;
        if (progressed >= usec_timeout) {
            cudaDeviceReset();
            fprintf(stderr, "FATAL: CUDA kernel timeout. Aborting\n");
            abort();
        }
    }
    cudaEventDestroy(cudaWatchdogEvent);
}
// No timeout occured
#endif

#endif
