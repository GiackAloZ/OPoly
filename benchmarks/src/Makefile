EXE:=$(basename $(wildcard omp-*.c))
CC:=gcc
CFLAGS+=-std=c99 -Wall -Wpedantic -fopenmp
LDLIBS+=-lm

ALL: $(EXE)

.PHONY: clean fetch

clean:
	\rm -f $(EXE) *.o *~
